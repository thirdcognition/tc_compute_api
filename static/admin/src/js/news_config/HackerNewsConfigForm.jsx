import React, { useState, useEffect } from "react";
import { Form, Button, Card } from "react-bootstrap";

function HackerNewsConfigForm({ initialConfigs = [], onConfigsChange }) {
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
            {
                feed_type: "frontpage",
                query: "",
                points: 0,
                comments: 0,
                articles: 5
            }
        ]);
    };

    const removeConfigField = (index) => {
        const newConfigFields = configFields.filter((_, i) => i !== index);
        setConfigFields(newConfigFields);
    };

    return (
        <Form.Group controlId="hackerNewsConfigs">
            {configFields.map((config, index) => (
                <Card key={index} className="border border-gray-300 mb-2">
                    <Card.Header className="d-flex justify-content-between align-items-center">
                        <h5 className="mb-0">
                            Config {index + 1}: {config.feed_type || "N/A"}
                        </h5>
                        <Button
                            variant="danger"
                            type="button"
                            onClick={() => removeConfigField(index)}
                        >
                            Remove Config
                        </Button>
                    </Card.Header>
                    <Card.Body className="bg-gray-200">
                        <Card className="mb-3">
                            <Card.Header>Feed Type</Card.Header>
                            <Card.Body>
                                <Form.Control
                                    as="select"
                                    value={config.feed_type || "newest"}
                                    onChange={(e) =>
                                        handleConfigChange(
                                            index,
                                            "feed_type",
                                            e.target.value
                                        )
                                    }
                                    className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                                >
                                    <option value="newest">Newest</option>
                                    <option value="newcomments">
                                        New Comments
                                    </option>
                                    <option value="frontpage">
                                        Front Page
                                    </option>
                                    <option value="bestcomments">
                                        Best Comments
                                    </option>
                                    <option value="ask">Ask HN</option>
                                    <option value="show">Show HN</option>
                                    <option value="polls">Polls</option>
                                    <option value="jobs">Jobs</option>
                                    <option value="whoishiring">
                                        Who is Hiring
                                    </option>
                                </Form.Control>
                            </Card.Body>
                        </Card>
                        <Card className="mb-3">
                            <Card.Header>Search Query</Card.Header>
                            <Card.Body>
                                <Form.Control
                                    type="text"
                                    placeholder="Enter search query..."
                                    value={config.query || ""}
                                    onChange={(e) =>
                                        handleConfigChange(
                                            index,
                                            "query",
                                            e.target.value
                                        )
                                    }
                                    className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                                />
                            </Card.Body>
                        </Card>
                        <div className="flex mb-3 gap-3">
                            <Card className="flex-1">
                                <Card.Header>Minimum Points</Card.Header>
                                <Card.Body>
                                    <Form.Control
                                        type="number"
                                        placeholder="Minimum points..."
                                        value={config.points || 0}
                                        onChange={(e) =>
                                            handleConfigChange(
                                                index,
                                                "points",
                                                parseInt(e.target.value, 10)
                                            )
                                        }
                                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                                    />
                                </Card.Body>
                            </Card>
                            <Card className="flex-1">
                                <Card.Header>Minimum Comments</Card.Header>
                                <Card.Body>
                                    <Form.Control
                                        type="number"
                                        placeholder="Minimum comments..."
                                        value={config.comments || 0}
                                        onChange={(e) =>
                                            handleConfigChange(
                                                index,
                                                "comments",
                                                parseInt(e.target.value, 10)
                                            )
                                        }
                                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                                    />
                                </Card.Body>
                            </Card>
                        </div>
                    </Card.Body>
                </Card>
            ))}
            <Button
                variant="secondary"
                type="button"
                onClick={addConfigField}
                className="w-full mb-2 py-2"
            >
                + Add another Hacker News config
            </Button>
        </Form.Group>
    );
}

export default HackerNewsConfigForm;
