import React from "react";
import { Card } from "react-bootstrap";

/**
 * Displays an error message within a styled Card if a message is provided.
 */
const ErrorMessage = ({ message }) => {
    if (!message) {
        return null; // Don't render if no message
    }

    return (
        <Card border="danger" className="mb-3">
            <Card.Header className="bg-danger text-white">Error</Card.Header>
            <Card.Body>
                <Card.Text>{message}</Card.Text>
            </Card.Body>
        </Card>
    );
};

export default ErrorMessage;
