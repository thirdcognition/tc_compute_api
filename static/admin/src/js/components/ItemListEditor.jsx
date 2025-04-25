import React from "react";
import { Button, Card } from "react-bootstrap"; // Added Card
import RemoveButton from "./RemoveButton";

/**
 * Renders a dynamic list of items within Cards, allowing editing, adding, and removing.
 * State management (the actual 'items' array and update logic) is handled by the parent component.
 */
const ItemListEditor = ({
    items = [], // The array of data items
    onAddItem, // Function to call when Add button is clicked
    onRemoveItem, // Function(index) to call when Remove button is clicked
    renderItem, // Function(item, index) => JSX for the Card.Body content
    renderItemHeader, // Optional Function(item, index) => JSX for Card.Header content (defaults to "Item X")
    addButtonLabel = "Add Item",
    itemContainerClass = "mb-3", // Class for the Card itself
    showAddButton = true,
    showRemoveButton = true, // Can be boolean or function(item, index) => boolean
    alwaysKeepOneItem = false // If true, prevents removing the last item
}) => {
    if (!renderItem) {
        console.error("ItemListEditor requires a renderItem prop.");
        return (
            <div className="text-danger">Error: renderItem prop missing.</div>
        );
    }

    return (
        <div>
            {items.map((item, index) => {
                // Determine if the remove button should be shown for this specific item
                const canRemoveThisItem =
                    (!alwaysKeepOneItem || items.length > 1) &&
                    (typeof showRemoveButton === "function"
                        ? showRemoveButton(item, index)
                        : showRemoveButton);

                return (
                    // Each item is rendered inside a Card
                    <Card key={index} className={itemContainerClass}>
                        {/* Render header only if a custom header renderer is provided OR if the remove button is shown */}
                        {(renderItemHeader || canRemoveThisItem) && (
                            <Card.Header className="d-flex justify-content-between align-items-center">
                                <div className="flex-grow-1">
                                    {/* Use custom header renderer or default */}
                                    {renderItemHeader ? (
                                        renderItemHeader(item, index)
                                    ) : (
                                        <span className="font-semibold">
                                            Item {index + 1}
                                        </span>
                                    )}
                                </div>
                                {/* Render remove button if allowed for this item */}
                                {canRemoveThisItem && onRemoveItem && (
                                    <RemoveButton
                                        onClick={() => onRemoveItem(index)}
                                        ariaLabel={`Remove item ${index + 1}`}
                                        className="ms-2" // Add some margin
                                    />
                                )}
                            </Card.Header>
                        )}
                        <Card.Body>
                            {/* Render the main content of the item using the provided function */}
                            {renderItem(item, index)}
                        </Card.Body>
                    </Card>
                );
            })}
            {/* Render the Add button if allowed */}
            {showAddButton && onAddItem && (
                <Button
                    variant="secondary"
                    onClick={onAddItem}
                    className="mt-2"
                >
                    {addButtonLabel}
                </Button>
            )}
        </div>
    );
};

export default ItemListEditor;
