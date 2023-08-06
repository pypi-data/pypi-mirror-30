import { Session } from '@jupyterlab/services';
import { ServiceManager } from '@jupyterlab/services';
export interface PromiseReturn {
    session: Session.ISession;
}
export declare function jupyterSessionConnect(serviceManager: ServiceManager, path: string, activeSessionIds: string[]): Promise<PromiseReturn>;
