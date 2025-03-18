export class NotifierModel {
    constructor() {
        this.listeners = [];
        this.boundNotifyListeners = (event, instance, ...args) => {
            this.notifyListeners(event, instance, ...args);
            return true;
        };
    }

    listen(callback, events = "_any_") {
        if (!Array.isArray(events)) {
            events = [events];
        }
        events.sort();

        if (
            typeof callback === "function" &&
            !this.listeners.some(
                (listener) =>
                    (Array.isArray(listener.events) && Array.isArray(events)
                        ? listener.events.toString() === events.toString()
                        : listener.events === events) &&
                    listener.callback === callback
            )
        ) {
            this.listeners.push({ events, callback });
        }
        return this;
    }

    wait(events = "_any_") {
        if (Array.isArray(events)) {
            events.sort();
        }
        return new Promise((resolve) => {
            const onceListener = (event, instance, ...args) => {
                resolve({ event, instance, args });
            };
            this.listen(events, onceListener);
        });
    }

    notifyListeners(event, ...args) {
        this.listeners = this.listeners.filter((listener) => {
            const listenerEvents = listener.events;
            if (
                listenerEvents.includes(event) ||
                listenerEvents.includes("_any_")
            ) {
                try {
                    return !!listener.callback(event, this, ...args);
                } catch (e) {
                    console.error("Issue with handling listener", e);
                }
            }
            return true;
        });
        return this.listeners.length > 0;
    }
}
