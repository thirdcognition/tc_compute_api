import React from "react";
import { Form, Card } from "react-bootstrap";

function ArticleCountComponent({ value, label, onChange }) {
    return (
        <Card className="mb-4 w-full">
            <Card.Header>
                <label className="mb-1 self-start">
                    {label ? label : "Maximum news items"}
                </label>
            </Card.Header>
            <Card.Body>
                <div className="flex items-center w-full">
                    <Form.Control
                        type="range"
                        min="1"
                        max="20"
                        value={value || "5"}
                        onChange={(e) => onChange(e.target.value)}
                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mr-4 flex-grow"
                    />
                    <span className="w-40 text-left">{value || 5}</span>
                </div>
            </Card.Body>
        </Card>
    );
}

export default ArticleCountComponent;
