import React from "react";
import { Card, Accordion } from "react-bootstrap";

// Renders a single source item card (internal helper)
const renderSourceItem = (option, index) => (
    <Card key={option.url || option.title || index} className="mb-3">
        {option.image && (
            <Card.Img
                variant="top"
                src={option.image}
                alt={option.title}
                style={{ maxHeight: "150px", objectFit: "cover" }}
            />
        )}
        <Card.Body>
            <Card.Title as="h6">
                {Array.isArray(option.url) && option.url.length > 1 ? (
                    <Accordion>
                        <Accordion.Item eventKey="0">
                            <Accordion.Header>{option.title}</Accordion.Header>
                            <Accordion.Body>
                                {option.url.map((url, idx) => (
                                    <a
                                        key={idx}
                                        href={url?.trim()}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block text-sm truncate"
                                    >
                                        {idx + 1}: {url?.trim()}
                                    </a>
                                ))}
                            </Accordion.Body>
                        </Accordion.Item>
                    </Accordion>
                ) : (
                    <a
                        href={
                            Array.isArray(option.url)
                                ? option.url[0]
                                : option.url
                        }
                        target="_blank"
                        rel="noopener noreferrer"
                        className="no-underline"
                    >
                        {option.title}
                    </a>
                )}
            </Card.Title>
            {option.publish_date && (
                <Card.Text className="text-gray-500 text-sm mt-1">
                    Published:{" "}
                    {new Date(option.publish_date).toLocaleDateString()}
                </Card.Text>
            )}
        </Card.Body>
    </Card>
);

// Main component to render the list of sources
function TranscriptSourcesDisplay({ sources }) {
    if (!sources || sources.length === 0) {
        return <p>No sources found.</p>;
    }

    return sources.map((option, index) => {
        if (option.references) {
            // Handle grouped sources (like from subjects)
            return (
                <Accordion key={option.title || index} className="mb-3">
                    <Accordion.Item eventKey="0">
                        <Accordion.Header>{option.title}</Accordion.Header>
                        <Accordion.Body>
                            {option.description && (
                                <Card.Text className="mb-3">
                                    {option.description}
                                </Card.Text>
                            )}
                            {option.references.map(renderSourceItem)}
                        </Accordion.Body>
                    </Accordion.Item>
                </Accordion>
            );
        } else {
            // Handle individual source items
            return renderSourceItem(option, index);
        }
    });
}

export default TranscriptSourcesDisplay;
