import React from "react";
import { Button } from "react-bootstrap";
import { FaTimes } from "react-icons/fa";

/**
 * A standardized Button for removing items.
 * Renders a red button with a times icon (X).
 */
const RemoveButton = ({
    onClick,
    size = "sm",
    className = "",
    ariaLabel = "Remove Item",
    ...props
}) => {
    return (
        <Button
            variant="danger"
            size={size}
            onClick={onClick}
            className={`d-inline-flex align-items-center mx-2 ${className}`}
            aria-label={ariaLabel}
            {...props}
        >
            <FaTimes />
        </Button>
    );
};

export default RemoveButton;
