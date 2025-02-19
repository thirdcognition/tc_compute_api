import React, { useState, useEffect } from "react";
import { Form, Button, Card } from "react-bootstrap";

export const conceptsMap = {
    topics: [
        { id: "18-34837", title: "Domestic" },
        { id: "18-34953", title: "Foreign" },
        { id: "18-19274", title: "Economy" },
        { id: "18-38033", title: "Politics" },
        { id: "18-150067", title: "Culture" },
        { id: "18-36066", title: "Entertainment" },
        { id: "18-819", title: "Science" },
        { id: "18-35354", title: "Nature" },
        { id: "18-35138", title: "Health" },
        { id: "18-35057", title: "Media" },
        { id: "18-12", title: "Traffic" },
        { id: "18-35381", title: "Perspectives" }
    ],
    locations: [
        { id: "18-141372", title: "South Karelia" },
        { id: "18-146311", title: "South Ostrobothnia" },
        { id: "18-141852", title: "South Savo" },
        { id: "18-141399", title: "Kainuu" },
        { id: "18-138727", title: "Kanta-Häme" },
        { id: "18-135629", title: "Central Ostrobothnia" },
        { id: "18-148148", title: "Central Finland" },
        { id: "18-131408", title: "Kymenlaakso" },
        { id: "18-139752", title: "Lapland" },
        { id: "18-146831", title: "Pirkanmaa" },
        { id: "18-148149", title: "Ostrobothnia" },
        { id: "18-141936", title: "North Karelia" },
        { id: "18-148154", title: "North Ostrobothnia" },
        { id: "18-141764", title: "North Savo" },
        { id: "18-141401", title: "Päijät-Häme" },
        { id: "18-139772", title: "Satakunta" },
        { id: "18-147345", title: "Uusimaa" },
        { id: "18-135507", title: "Southwest Finland" }
    ]
};

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
            { feed_type: "majorHeadlines", lang: "fi" }
        ]);
    };

    const removeConfigField = (index) => {
        const newConfigFields = configFields.filter((_, i) => i !== index);
        setConfigFields(newConfigFields);
    };

    return (
        <Form.Group controlId="yleNewsConfigs">
            {configFields.map((config, index) => (
                <Card key={index} className="mb-3">
                    <Card.Header className="d-flex justify-content-between align-items-center">
                        <h5 className="mb-0">
                            Config {index + 1}:{" "}
                            {config.feed_type || config.type || "N/A"}
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
                        <Card className="mb-3">
                            <Card.Header>Feed Type</Card.Header>
                            <Card.Body>
                                <Form.Control
                                    as="select"
                                    value={
                                        config.feed_type ||
                                        config.type ||
                                        "majorHeadlines"
                                    }
                                    onChange={(e) =>
                                        handleConfigChange(
                                            index,
                                            "feed_type",
                                            e.target.value
                                        )
                                    }
                                    className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                                >
                                    <option value="majorHeadlines">
                                        Major Headlines
                                    </option>
                                    <option value="mostRead">Most Read</option>
                                    <option value="topics">Topics</option>
                                </Form.Control>
                            </Card.Body>
                        </Card>

                        {config.feed_type === "topics" && (
                            <>
                                <Card className="mb-3">
                                    <Card.Header>Language</Card.Header>
                                    <Card.Body>
                                        <Form.Control
                                            as="select"
                                            value={config.lang || "fi"}
                                            onChange={(e) =>
                                                handleConfigChange(
                                                    index,
                                                    "lang",
                                                    e.target.value
                                                )
                                            }
                                            className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                                        >
                                            <option value="fi">Finnish</option>
                                            <option value="en">English</option>
                                        </Form.Control>
                                    </Card.Body>
                                </Card>
                                <div className="flex gap-3 mb-3">
                                    <Card className="flex-1">
                                        <Card.Header>Topics</Card.Header>
                                        <Card.Body>
                                            <Form.Control
                                                as="select"
                                                multiple
                                                value={config.topics || []}
                                                onChange={(e) =>
                                                    handleConfigChange(
                                                        index,
                                                        "topics",
                                                        Array.from(
                                                            e.target
                                                                .selectedOptions
                                                        ).map(
                                                            (option) =>
                                                                option.value
                                                        )
                                                    )
                                                }
                                                className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                                            >
                                                {conceptsMap.topics.map(
                                                    (topic) => (
                                                        <option
                                                            key={topic.id}
                                                            value={topic.id}
                                                        >
                                                            {topic.title}
                                                        </option>
                                                    )
                                                )}
                                            </Form.Control>
                                        </Card.Body>
                                    </Card>

                                    <Card className="flex-1">
                                        <Card.Header>Locations</Card.Header>
                                        <Card.Body>
                                            <Form.Control
                                                as="select"
                                                multiple
                                                value={config.locations || []}
                                                onChange={(e) =>
                                                    handleConfigChange(
                                                        index,
                                                        "locations",
                                                        Array.from(
                                                            e.target
                                                                .selectedOptions
                                                        ).map(
                                                            (option) =>
                                                                option.value
                                                        )
                                                    )
                                                }
                                                className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                                            >
                                                {conceptsMap.locations.map(
                                                    (location) => (
                                                        <option
                                                            key={location.id}
                                                            value={location.id}
                                                        >
                                                            {location.title}
                                                        </option>
                                                    )
                                                )}
                                            </Form.Control>
                                        </Card.Body>
                                    </Card>
                                </div>
                            </>
                        )}
                    </Card.Body>
                </Card>
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
