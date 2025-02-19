import React, { useState, useEffect } from "react";
import { Form, Button, Card } from "react-bootstrap";
import ArticleCountComponent from "../components/ArticleCountComponent";
import ArticleReleasedWithinComponent from "../components/ArticleReleasedWithinComponent";
import LanguageComponent from "../components/LanguageComponent";
import CountryComponent from "../components/CountryComponent";

function GoogleNewsConfigForm({ initialConfigs = [], onConfigsChange }) {
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
                feed_type: "topic",
                lang: "en",
                country: "US",
                query: "",
                location: "",
                topic: [],
                since: null,
                articles: 5
            }
        ]);
    };

    const removeConfigField = (index) => {
        const newConfigFields = configFields.filter((_, i) => i !== index);
        setConfigFields(newConfigFields);
    };

    return (
        <Form.Group controlId="googleNewsConfigs">
            {configFields.map((config, index) => (
                <Card key={index} className="mb-3 border-gray-300">
                    <Card.Header className="d-flex justify-content-between align-items-center">
                        <h5 className="mb-0">
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
                    </Card.Header>
                    <Card.Body className="bg-gray-200">
                        <Card className="mb-4">
                            <Card.Header>Feed Type</Card.Header>
                            <Card.Body>
                                <Form.Control
                                    as="select"
                                    value={config.feed_type || "top_topics"}
                                    onChange={(e) =>
                                        handleConfigChange(
                                            index,
                                            "feed_type",
                                            e.target.value
                                        )
                                    }
                                    className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 ${
                                        !config.lang ? "border-red-500" : ""
                                    }`}
                                >
                                    <option value="search">Search</option>
                                    <option value="location">Location</option>
                                    <option value="topic">Topic</option>
                                    <option value="top_topics">
                                        Top Topics
                                    </option>
                                </Form.Control>
                            </Card.Body>
                        </Card>
                        {config.feed_type === "search" && (
                            <Card className="mb-4">
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
                                        className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 ${
                                            !config.country
                                                ? "border-red-500"
                                                : ""
                                        }`}
                                    />
                                </Card.Body>
                            </Card>
                        )}
                        {config.feed_type === "location" && (
                            <Card className="mb-4">
                                <Card.Header>
                                    Location Configuration
                                </Card.Header>
                                <Card.Body>
                                    <Form.Control
                                        type="text"
                                        placeholder="Enter locations as CSV..."
                                        value={config.location || ""}
                                        onChange={(e) =>
                                            handleConfigChange(
                                                index,
                                                "location",
                                                e.target.value
                                                    .split(",")
                                                    .map((loc) => loc.trim())
                                            )
                                        }
                                        className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 ${
                                            config.lang === ""
                                                ? "border-red-500"
                                                : ""
                                        }`}
                                    />
                                </Card.Body>
                            </Card>
                        )}
                        {config.feed_type === "topic" && (
                            <Card className="mb-4">
                                <Card.Header>Topic Selection</Card.Header>
                                <Card.Body>
                                    <Form.Control
                                        as="select"
                                        multiple
                                        value={config.topic || []}
                                        onChange={(e) =>
                                            handleConfigChange(
                                                index,
                                                "topic",
                                                Array.from(
                                                    e.target.selectedOptions,
                                                    (option) => option.value
                                                )
                                            )
                                        }
                                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                                    >
                                        <option value="WORLD">World</option>
                                        <option value="NATION">Nation</option>
                                        <option value="BUSINESS">
                                            Business
                                        </option>
                                        <option value="TECHNOLOGY">
                                            Technology
                                        </option>
                                        <option value="ENTERTAINMENT">
                                            Entertainment
                                        </option>
                                        <option value="SCIENCE">Science</option>
                                        <option value="SPORTS">Sports</option>
                                        <option value="HEALTH">Health</option>
                                    </Form.Control>
                                </Card.Body>
                            </Card>
                        )}
                        <ArticleReleasedWithinComponent
                            value={config.since}
                            onChange={(value) =>
                                handleConfigChange(index, "since", value)
                            }
                        />
                        <div className="flex gap-3">
                            <div className="flex-1">
                                <LanguageComponent
                                    value={config.lang}
                                    onChange={(value) =>
                                        handleConfigChange(index, "lang", value)
                                    }
                                />
                            </div>
                            <div className="flex-1">
                                <CountryComponent
                                    value={config.country}
                                    onChange={(value) =>
                                        handleConfigChange(
                                            index,
                                            "country",
                                            value
                                        )
                                    }
                                />
                            </div>
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
                + Add another Google News config
            </Button>
        </Form.Group>
    );
}

export default GoogleNewsConfigForm;
