import React, { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";
import ArticleCountComponent from "../components/ArticleCountComponent";

function YleNewsConfigForm({ initialConfigs = [], onConfigsChange }) {
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
        setConfigFields([
            ...configFields,
            { type: "majorHeadlines", articles: 5 }
        ]);
    };

    const removeConfigField = (index) => {
        const newConfigFields = configFields.filter((_, i) => i !== index);
        setConfigFields(newConfigFields);
    };

    return (
        <Form.Group controlId="yleNewsConfigs">
            <Form.Label className="font-semibold">
                Configure Yle News:
            </Form.Label>
            {configFields.map((config, index) => (
                <div key={index} className="border border-gray-300 p-2 mb-2">
                    <div className="flex items-center justify-between mb-2 w-full">
                        <h5>
                            Config {index + 1}: {config.type || "N/A"}
                        </h5>
                        <Button
                            variant="danger"
                            type="button"
                            onClick={() => removeConfigField(index)}
                            className="py-2"
                        >
                            Remove Config
                        </Button>
                    </div>
                    <Form.Control
                        as="select"
                        value={config.type || "majorHeadlines"}
                        onChange={(e) =>
                            handleConfigChange(index, "type", e.target.value)
                        }
                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                    >
                        <option value="majorHeadlines">Major Headlines</option>
                        <option value="mostRead">Most Read</option>
                    </Form.Control>
                    <ArticleCountComponent
                        value={config.articles}
                        onChange={(value) =>
                            handleConfigChange(index, "articles", value)
                        }
                    />
                </div>
            ))}
            <Button
                variant="secondary"
                type="button"
                onClick={addConfigField}
                className="w-full mb-2 py-2"
            >
                + Add another Yle News config
            </Button>
        </Form.Group>
    );
}

export default YleNewsConfigForm;
