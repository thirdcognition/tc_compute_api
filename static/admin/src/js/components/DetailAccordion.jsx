import React, { useState, useEffect } from "react";
import { Accordion } from "react-bootstrap";

/**
 * Renders a Bootstrap Accordion with dynamically generated items.
 * Optionally calls an onItemToggle callback when an item's state changes.
 */
const DetailAccordion = ({
    items = [], // Array of data items to render in the accordion
    itemKey, // Function(item, index) => string | number, or string key path for eventKey
    renderHeader, // Function(item, index) => JSX for Accordion.Header
    renderBody, // Function(item, index) => JSX for Accordion.Body
    onItemToggle, // Optional: Function(item, isOpen: boolean) called when item state changes
    defaultActiveKey, // Optional: Key(s) to be open by default
    activeKey, // Optional: Controlled active key(s)
    onSelect, // Optional: Callback for selection changes (if controlled externally)
    alwaysOpen = false, // Optional: Allow multiple items open
    className = "",
    ...props // Other props for the main Accordion component
}) => {
    // Internal state to track active keys if not controlled externally
    // Initialize with defaultActiveKey
    const [internalActiveKey, setInternalActiveKey] = useState(() => {
        // Ensure defaultActiveKey is in array format if alwaysOpen is true
        if (
            alwaysOpen &&
            defaultActiveKey &&
            !Array.isArray(defaultActiveKey)
        ) {
            return [defaultActiveKey];
        }
        return defaultActiveKey;
    });

    // Determine the active key to use (external control takes precedence)
    const currentActiveKey =
        activeKey !== undefined ? activeKey : internalActiveKey;

    // Effect to update internal state if defaultActiveKey changes (useful if items load async)
    // and the component is not externally controlled
    useEffect(() => {
        if (activeKey === undefined) {
            // Ensure defaultActiveKey is in array format if alwaysOpen is true
            let initialKey = defaultActiveKey;
            if (alwaysOpen && initialKey && !Array.isArray(initialKey)) {
                initialKey = [initialKey];
            }
            setInternalActiveKey(initialKey);
        }
    }, [defaultActiveKey, activeKey, alwaysOpen]);

    // Moved generateKey and useMemo before the early return to comply with Rules of Hooks
    const generateKey = (item, index) => {
        if (typeof itemKey === "function") {
            return itemKey(item, index);
        }
        if (typeof itemKey === "string") {
            // Basic key path access, assumes item is an object
            return item?.[itemKey] ?? index.toString();
        }
        // Fallback to index
        return index.toString();
    };

    // Memoize the items array with their generated keys to avoid recalculating
    // and potentially help with stability in the handleSelect closure.
    const itemsWithKeys = React.useMemo(
        () =>
            items.map((item, index) => {
                if (
                    typeof item === "object" &&
                    item !== null &&
                    !Array.isArray(item)
                ) {
                    return {
                        ...item,
                        _generatedKey: generateKey(item, index)
                    };
                } else {
                    return {
                        value: item,
                        _generatedKey: generateKey(item, index)
                    };
                }
            }),
        [items, itemKey]
    ); // Recalculate only if items or itemKey function changes

    if (!renderHeader || !renderBody) {
        console.error(
            "DetailAccordion requires both renderHeader and renderBody props."
        );
        return (
            <div className="text-danger">
                Error: renderHeader or renderBody prop missing.
            </div>
        );
    }

    // handleSelect remains here as it's not a hook
    const handleSelect = (selectedEventKey) => {
        // selectedEventKey from react-bootstrap Accordion is:
        // - string | null: if alwaysOpen is false
        // - string[]: if alwaysOpen is true

        const newActiveKeys = alwaysOpen
            ? Array.isArray(selectedEventKey)
                ? selectedEventKey
                : [] // It's already an array if alwaysOpen
            : selectedEventKey
              ? [selectedEventKey]
              : []; // Convert string/null to array

        const previousActiveKeys = alwaysOpen
            ? Array.isArray(currentActiveKey)
                ? currentActiveKey
                : currentActiveKey
                  ? [currentActiveKey]
                  : []
            : currentActiveKey
              ? [currentActiveKey]
              : []; // Ensure previous is also an array

        // Update internal state only if not controlled externally
        if (activeKey === undefined) {
            // Store as array if alwaysOpen, otherwise store string/null
            setInternalActiveKey(
                alwaysOpen ? newActiveKeys : (newActiveKeys[0] ?? null)
            );
        }

        // Call external onSelect if provided (for controlled components)
        if (onSelect) {
            onSelect(selectedEventKey); // Pass the raw event key value
        }

        // Call onItemToggle for items whose state changed
        if (typeof onItemToggle === "function") {
            itemsWithKeys.forEach((item) => {
                const key = item._generatedKey;
                const wasOpen = previousActiveKeys.includes(key);
                const isOpen = newActiveKeys.includes(key);

                if (isOpen !== wasOpen) {
                    // Pass the original item data (without _generatedKey)
                    const { _generatedKey, ...originalItem } = item;
                    onItemToggle(originalItem, isOpen);
                }
            });
        }
    };

    return (
        <Accordion
            defaultActiveKey={defaultActiveKey}
            activeKey={currentActiveKey} // Use controlled or internal state
            onSelect={handleSelect} // Use the enhanced handler
            alwaysOpen={alwaysOpen}
            className={className}
            {...props}
        >
            {itemsWithKeys.map((item, index) => {
                const key = item._generatedKey;
                // Ensure item has necessary props before rendering
                if (
                    !item ||
                    typeof renderHeader !== "function" ||
                    typeof renderBody !== "function"
                ) {
                    console.warn(`Skipping invalid item with key ${key}`, item);
                    return null;
                }
                return (
                    <Accordion.Item eventKey={key} key={key}>
                        <Accordion.Header>
                            {renderHeader(item, index)}
                        </Accordion.Header>
                        <Accordion.Body>
                            {renderBody(item, index)}
                        </Accordion.Body>
                    </Accordion.Item>
                );
            })}
        </Accordion>
    );
};

export default DetailAccordion;
