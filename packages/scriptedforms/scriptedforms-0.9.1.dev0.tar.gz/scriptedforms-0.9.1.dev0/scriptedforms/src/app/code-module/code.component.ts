// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.


/*
A component that clobbers the html <code> tags.

Markdown turns the following syntax into <code> tags:
```
code here
```

This component highjacks those tags, reads the text written within them and
preps the code for sending to the Python kernel.

The function 'runCode' can be called on this component to have its code sent
to the Python kernel.
*/

// import { BehaviorSubject } from 'rxjs/BehaviorSubject';
// import { Subscription } from 'rxjs/Subscription';

import {
  Component, AfterViewInit, ViewChild, ElementRef, OnDestroy
} from '@angular/core';

import {
  JSONObject, PromiseDelegate
} from '@phosphor/coreutils';

import {
  nbformat
} from '@jupyterlab/coreutils';

import {
  RenderMimeRegistry, standardRendererFactories as initialFactories
} from '@jupyterlab/rendermime';
import { OutputArea, OutputAreaModel } from '@jupyterlab/outputarea';
import { Kernel, KernelMessage } from '@jupyterlab/services';

import {
  Mode
} from '@jupyterlab/codemirror';

import { KernelService } from '../services/kernel.service';
import { FileService } from '../services/file.service';

@Component({
  selector: 'code.language-python',
  template: `<span #codecontainer [hidden]="this.name !== undefined"><ng-content></ng-content></span>`
})
export class CodeComponent implements AfterViewInit, OnDestroy {
  private _displayIdMap = new Map<string, number[]>();
  sessionId: string;
  name: string;
  renderMime: RenderMimeRegistry = new RenderMimeRegistry({
    initialFactories,
    sanitizer: {
      sanitize: (input: string) => input
    }
  });
  model: OutputAreaModel = new OutputAreaModel();
  outputAreaOptions: OutputArea.IOptions = {
    model: this.model,
    rendermime: this.renderMime
  };
  outputArea: OutputArea = new OutputArea(this.outputAreaOptions);

  promise: Promise<Kernel.IFuture>;
  outputContainer: HTMLDivElement;
  // containerUpdated: BehaviorSubject<boolean> = new BehaviorSubject(false);

  // mutationObserver: MutationObserver;
  // mutationBehaviorSubject: BehaviorSubject<null> = new BehaviorSubject(null);

  firstDisplay: PromiseDelegate<null>;

  // onIOPub: BehaviorSubject<KernelMessage.IIOPubMessage> = new BehaviorSubject(null);
  // onIOPubSubscription: Subscription = null;

  code: string;
  @ViewChild('codecontainer') codecontainer: ElementRef;

  constructor(
    private myKernelSevice: KernelService,
    private myFileService: FileService,
    private _eRef: ElementRef
  ) { }

  updateOutputAreaModel() {
    this.outputAreaOptions = {
      model: this.model,
      rendermime: this.renderMime
    };
    this.outputArea = new OutputArea(this.outputAreaOptions);
  }

  ngAfterViewInit() {
    this.code = this.codecontainer.nativeElement.innerText;

    // Apply python syntax highlighting to every code block
    Mode.ensure('python').then((spec) => {
      const el = document.createElement('div');
      Mode.run(this.code, spec.mime, el);
      this.codecontainer.nativeElement.innerHTML = el.innerHTML;
      this._eRef.nativeElement.classList.add('cm-s-jupyter');
    });

    const element: HTMLElement = this._eRef.nativeElement;
    this.outputContainer = document.createElement('div');
    // this.outputContainer.classList.add('avoid-page-break')
    this.outputContainer.appendChild(this.outputArea.node);
    element.parentNode.parentNode.insertBefore(this.outputContainer, element.parentNode);

    // // Mutation observer is awesome! Use more of this.
    // this.mutationObserver = new MutationObserver(() => {
    //   this.mutationBehaviorSubject.next(null);
    // });

    // this.mutationObserver.observe(
    //   this.outputContainer,
    //   {
    //     childList: true,
    //     subtree: true
    //   }
    // );

    // this.containerUpdated.subscribe(() => {
    //   console.log('container updated');
    //   this.mutationBehaviorSubject.asObservable().toPromise().then(() => {
    //     this.updateLinks();
    //   });
    // });
  }

  ngOnDestroy() {
    // this.outputArea.dispose();
  }

  updateLinks() {
    const links: HTMLAnchorElement[] = Array.from(this.outputArea.node.getElementsByTagName('a'));
    console.log(this.outputArea.node.innerHTML);
    console.log(links);
    this.myFileService.morphLinksToUpdateFile(links);
  }

  /**
   * Each runnable code component on the form has a unique name. This is defined by
   * it's parent section. The name is used to detect repeat submissions for the purpose
   * of only running the most recent submission.
   *
   * @param name A unique name for the code component
   */
  // codeComponentInit(sessionId: string, name: string) {
  //   this.name = name;
  //   this.sessionId = sessionId
  // }

  /**
   * Run the code within the code component. Update the output area with the results of the
   * code.
   */
  runCode(): Promise<null> {
    // if (this.onIOPubSubscription) {
    //   this.onIOPubSubscription.unsubscribe();
    // }
    const codeCompleted = new PromiseDelegate<null>();
    this.promise = this.myKernelSevice.runCode(this.sessionId, this.code, this.name);
    this.promise.then(future => {
      if (future) {
        this.firstDisplay = new PromiseDelegate();
        this.model = new OutputAreaModel();

        future.onIOPub = this._onIOPub;
        future.done.then(() => {
          this.updateLinks();
          codeCompleted.resolve(null);
        });

        this.firstDisplay.promise.then(() => {
          this.updateOutputAreaModel();

          this.outputContainer.replaceChild(this.outputArea.node, this.outputContainer.firstChild);
          // this.containerUpdated.next(true);
          // this.onIOPubSubscription = this.onIOPub.subscribe(msg => {
          //   const msgType = msg.header.msg_type;
          //   if (msgType === 'display_data' || msgType === 'stream' || msgType === 'update_display_data') {
          //     this.containerUpdated.next(true);
          //   }
          // });

          const element: HTMLDivElement = this.outputContainer;
          element.style.minHeight = String(this.outputArea.node.clientHeight) + 'px';
        });
      } else {
        codeCompleted.resolve(null);
      }
    });
    return codeCompleted.promise;
  }

  // Extract from @jupyterlab/outputarea/src/widget.ts
  private _onIOPub = (msg: KernelMessage.IIOPubMessage) => {
    const model = this.model;
    const msgType = msg.header.msg_type;
    let output: nbformat.IOutput;
    const transient = (msg.content.transient || {}) as JSONObject;
    const displayId = transient['display_id'] as string;
    let targets: number[];

    switch (msgType) {
    case 'execute_result':
    case 'display_data':
    case 'stream':
    case 'error':
      output = msg.content as nbformat.IOutput;
      output.output_type = msgType as nbformat.OutputType;
      model.add(output);
      break;
    case 'clear_output':
      const wait = (msg as KernelMessage.IClearOutputMsg).content.wait;
      model.clear(wait);
      break;
    case 'update_display_data':
      output = msg.content as nbformat.IOutput;
      output.output_type = 'display_data';
      targets = this._displayIdMap.get(displayId);
      if (targets) {
        for (const index of targets) {
          model.set(index, output);
        }
      }
      break;
    default:
      break;
    }
    if (msgType === 'display_data' || msgType === 'stream' || msgType === 'update_display_data') {
      this.firstDisplay.resolve(null);
    }
    if (displayId && msgType === 'display_data') {
       targets = this._displayIdMap.get(displayId) || [];
       targets.push(model.length - 1);
       this._displayIdMap.set(displayId, targets);
    }
    // this.onIOPub.next(msg);
  }
}
