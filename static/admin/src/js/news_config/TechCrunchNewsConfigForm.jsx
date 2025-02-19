import React, { useState, useEffect } from "react";
import { Form, Button, Card } from "react-bootstrap";
import ArticleCountComponent from "../components/ArticleCountComponent";

function TechCrunchNewsConfigForm({ initialConfigs = [], onConfigsChange }) {
    const [configFields, setConfigFields] = useState(initialConfigs);

    useEffect(() => {
        onConfigsChange(configFields);
    }, [configFields, onConfigsChange]);

    const handleConfigChange = (index, key, value) => {
        const newConfigFields = [...configFields];
        if (!newConfigFields[index]) {
            newConfigFields[index] = {};
        }
        newConfigFields[index][key] = value;
        setConfigFields(newConfigFields);
    };

    const addConfigField = () => {
        setConfigFields([...configFields, { articles: 5 }]);
    };

    const removeConfigField = (index) => {
        const newConfigFields = configFields.filter((_, i) => i !== index);
        setConfigFields(newConfigFields);
    };

    return (
        <Form.Group controlId="techCrunchNewsConfigs">
            {configFields && configFields.length > 0 && (
                <Card className="mb-2">
                    <Card.Header className="font-semibold">
                        TechCrunch News:
                    </Card.Header>
                    <Card.Body>
                        {configFields.map((config, index) => (
                            <div className="flex items-center justify-between mb-2 w-full">
                                <h5>Config {index + 1}</h5>
                                <Button
                                    variant="danger"
                                    type="button"
                                    onClick={() => removeConfigField(index)}
                                    className="py-2"
                                >
                                    Remove Config
                                </Button>
                            </div>
                        ))}
                    </Card.Body>
                </Card>
            )}
            {configFields && configFields.length == 0 && (
                <Button
                    variant="secondary"
                    type="button"
                    onClick={addConfigField}
                    className="w-full mb-2 py-2"
                >
                    + Add TechCrunch News config
                </Button>
            )}
        </Form.Group>
    );
}

export default TechCrunchNewsConfigForm;
