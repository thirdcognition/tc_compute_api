import React from "react";
import { Form, Card } from "react-bootstrap";

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
            <Card className="mb-2">
                <Card.Header>Language:</Card.Header>
                <Card.Body>
                    <Form.Control
                        as="select"
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    >
                        {languages.map((language) => (
                            <option key={language.code} value={language.code}>
                                {language.name}
                            </option>
                        ))}
                    </Form.Control>
                </Card.Body>
            </Card>
        </Form.Group>
    );
}

export default LanguageComponent;
