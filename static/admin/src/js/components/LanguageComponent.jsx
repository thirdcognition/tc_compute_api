import React from "react";
import { Form } from "react-bootstrap";

function LanguageComponent({ value, onChange }) {
    const languages = [
        { code: "en", name: "English" },
        { code: "sv", name: "Swedish" },
        { code: "no", name: "Norwegian" },
        { code: "fi", name: "Finnish" },
        { code: "da", name: "Danish" }
    ];

    return (
        <Form.Group controlId="language-select">
            <Form.Label className="font-semibold">Language:</Form.Label>
            <Form.Control
                as="select"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
            >
                {languages.map((language) => (
                    <option key={language.code} value={language.code}>
                        {language.name}
                    </option>
                ))}
            </Form.Control>
        </Form.Group>
    );
}

export default LanguageComponent;
