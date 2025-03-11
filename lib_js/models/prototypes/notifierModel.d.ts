export interface Listener<T> {
    events: string | string[];
    callback: (
        event: string,
        instance: T,
        ...args: unknown[]
    ) => boolean | void;
}

export interface NotifyResult<T> {
    event: string;
    instance: T;
    args: unknown[];
}

export declare class NotifierModel<T> {
    listeners: Listener<T>[];
    boundNotifyListeners: (
        event: string,
        instance: T,
        ...args: unknown[]
    ) => boolean;

    listen(
        callback: (
            event: string,
            instance: T,
            ...args: unknown[]
        ) => boolean | void,
        events?: string | string[]
    ): this;

    wait(events?: string | string[]): Promise<NotifyResult<T>>;
    notifyListeners(event: string, ...args: unknown[]): boolean;
}
