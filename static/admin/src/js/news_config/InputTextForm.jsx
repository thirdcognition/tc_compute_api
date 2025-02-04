import React, { useState, useEffect } from "react";
import { Form } from "react-bootstrap";

function InputTextForm({
    initialText = "",
    onTextChange,
    label = "Input Text:"
}) {
    const [text, setText] = useState(initialText);

    useEffect(() => {
        onTextChange(text);
    }, [text, onTextChange]);

    return (
        <Form.Group controlId="inputText">
            <Form.Label className="font-semibold">{label}</Form.Label>
            <Form.Control
                as="textarea"
                rows={5}
                placeholder="Enter text here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
        </Form.Group>
    );
}

export default InputTextForm;
