import React, { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";
import ArticleCountComponent from "../components/ArticleCountComponent";

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
            <Form.Label className="font-semibold">
                Configure Hacker News:
            </Form.Label>
            {configFields.map((config, index) => (
                <div key={index} className="border border-gray-300 p-2 mb-2">
                    <div className="flex items-center justify-between mb-2 w-full">
                        <h5>
                            Config {index + 1}: {config.feed_type || "N/A"}
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
                    <Form.Label>Feed Type</Form.Label>
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
                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                    >
                        <option value="newest">Newest</option>
                        <option value="newcomments">New Comments</option>
                        <option value="frontpage">Front Page</option>
                        <option value="bestcomments">Best Comments</option>
                        <option value="ask">Ask HN</option>
                        <option value="show">Show HN</option>
                        <option value="polls">Polls</option>
                        <option value="jobs">Jobs</option>
                        <option value="whoishiring">Who is Hiring</option>
                    </Form.Control>
                    <Form.Label>Search Query</Form.Label>
                    <Form.Control
                        type="text"
                        placeholder="Enter search query..."
                        value={config.query || ""}
                        onChange={(e) =>
                            handleConfigChange(index, "query", e.target.value)
                        }
                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                    />
                    <Form.Label>Minimum Points</Form.Label>
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
                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                    />
                    <Form.Label>Minimum Comments</Form.Label>
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
                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                    />
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
                + Add another Hacker News config
            </Button>
        </Form.Group>
    );
}

export default HackerNewsConfigForm;
