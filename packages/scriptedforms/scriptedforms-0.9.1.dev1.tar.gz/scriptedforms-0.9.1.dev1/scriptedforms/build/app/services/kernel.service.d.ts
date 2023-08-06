import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { PromiseDelegate } from '@phosphor/coreutils';
import { Kernel, Session, KernelMessage } from '@jupyterlab/services';
import { JupyterService } from './jupyter.service';
export declare class KernelService {
    private myJupyterService;
    session: Session.ISession;
    sessionConnected: PromiseDelegate<Session.ISession>;
    kernel: Kernel.IKernelConnection;
    kernelStatus: BehaviorSubject<Kernel.Status>;
    jupyterError: BehaviorSubject<KernelMessage.IErrorMsg>;
    queueId: number;
    queueLog: {
        [queueId: number]: string;
    };
    queue: Promise<any>;
    queueLength: BehaviorSubject<number>;
    constructor(myJupyterService: JupyterService);
    sessionConnect(path: string): Promise<Session.ISession>;
    restartKernel(): Promise<Session.ISession>;
    addToQueue(name: string, asyncFunction: (id: number) => Promise<any>): Promise<any>;
    runCode(code: string, name: string): Promise<any>;
}
