export class NotifierModel {
    constructor() {
        this.listeners = [];
        this.boundNotifyListeners = (event, instance, ...args) => {
            this.notifyListeners(event, instance, ...args);
            return true;
        };
    }

    listen(callback, events = "_any_") {
        if (
            typeof callback === "function" &&
            !this.listeners.some(
                (listener) =>
                    listener.event === events && listener.callback === callback
            )
        ) {
            this.listeners.push({ events, callback });
        }
        return this;
    }

    wait(events = "_any_") {
        return new Promise((resolve) => {
            const onceListener = (event, instance, ...args) => {
                resolve({ event, instance, args });
            };
            this.listen(events, onceListener);
        });
    }

    notifyListeners(event, ...args) {
        this.listeners = this.listeners.filter((listener) => {
            const listenerEvents = Array.isArray(listener.event)
                ? listener.event
                : [listener.event];
            if (
                listenerEvents.includes(event) ||
                listenerEvents.includes("_any_")
            ) {
                return !!listener.callback(event, this, ...args);
            }
            return true;
        });
        return this.listeners.length > 0;
    }
}
