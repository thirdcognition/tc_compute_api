export interface NotifierModel<T> {
    listeners: Array<{
        event: string;
        callback: (
            event: string,
            instance: T,
            ...args: unknown[]
        ) => boolean | void;
    }>;
    boundNotifyListeners: (...args: T[]) => boolean;

    listen(
        callback: (
            event: string,
            instance: T,
            ...args: unknown[]
        ) => boolean | void,
        events?: string | string[]
    ): this;
    wait(events?: string | string[]): Promise<unknown[]>;
    notifyListeners(event: string, ...args: unknown[]): boolean;
}
