import React, { useState, useEffect } from "react";
import { Form, Button, Card } from "react-bootstrap";

function LinkForm({ initialLinks = [], onLinksChange }) {
    const [linkFields, setLinkFields] = useState(initialLinks);

    useEffect(() => {
        onLinksChange(linkFields);
    }, [linkFields, onLinksChange]);

    const handleLinkChange = (index, value) => {
        const newLinkFields = [...linkFields];
        newLinkFields[index] = value;
        setLinkFields(newLinkFields);
    };

    const addLinkField = () => {
        setLinkFields([...linkFields, ""]);
    };

    const removeLinkField = (index) => {
        const newLinkFields = linkFields.filter((_, i) => i !== index);
        setLinkFields(newLinkFields);
    };

    return (
        <Form.Group controlId="links">
            <Form.Label className="font-semibold">
                Add links (one per item):
            </Form.Label>
            {linkFields.map((link, index) => (
                <Card key={index} className="mb-3">
                    <Card.Header className="flex items-center justify-between">
                        <span>Link {index + 1}</span>
                        <Button
                            variant="danger"
                            type="button"
                            onClick={() => removeLinkField(index)}
                            className="py-1"
                        >
                            Remove
                        </Button>
                    </Card.Header>
                    <Card.Body>
                        <Form.Control
                            type="text"
                            placeholder="Enter URL here..."
                            value={link}
                            onChange={(e) =>
                                handleLinkChange(index, e.target.value)
                            }
                            className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                        />
                    </Card.Body>
                </Card>
            ))}
            <Button
                variant="secondary"
                type="button"
                onClick={addLinkField}
                className="w-full mb-2 py-2"
            >
                + Add another link
            </Button>
        </Form.Group>
    );
}

export default LinkForm;
