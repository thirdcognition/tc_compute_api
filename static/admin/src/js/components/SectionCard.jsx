import React from "react";
import { Card } from "react-bootstrap";

/**
 * A reusable Card component for wrapping content sections with a consistent header.
 */
const SectionCard = ({
    title, // Title for the Card.Header
    headerAs = "h6", // HTML element type for the header title (e.g., 'h5', 'h6')
    children, // Content for the Card.Body
    className = "mb-4", // Default bottom margin, can be overridden
    headerClassName = "", // Additional classes for Card.Header
    bodyClassName = "", // Additional classes for Card.Body
    ...props // Other props to pass directly to the Card component
}) => {
    return (
        <Card className={className} {...props}>
            {title && (
                <Card.Header as={headerAs} className={headerClassName}>
                    {title}
                </Card.Header>
            )}
            <Card.Body className={bodyClassName}>{children}</Card.Body>
        </Card>
    );
};

export default SectionCard;
