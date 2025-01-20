import React, { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";
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
                type: "topic",
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

    const convertHoursToTimeFormat = (hours) => {
        const days = Math.floor(hours / 24);
        const remainingHours = hours % 24;
        const months = Math.floor(days / 30);
        const remainingDays = days % 30;
        let result = "";
        if (months > 0) result += `${months}m `;
        if (remainingDays > 0) result += `${remainingDays}d `;
        if (remainingHours > 0) result += `${remainingHours}h`;
        return result.trim();
    };

    const convertTimeFormatToHours = (timeFormat) => {
        if (typeof timeFormat !== "string") {
            console.error(
                "Expected a string for timeFormat, but received:",
                timeFormat
            );
            return 0; // or handle the error as needed
        }
        const timeParts = timeFormat.split(" ");
        let totalHours = 0;
        timeParts.forEach((part) => {
            if (part.endsWith("m")) {
                totalHours += parseInt(part) * 30 * 24;
            } else if (part.endsWith("d")) {
                totalHours += parseInt(part) * 24;
            } else if (part.endsWith("h")) {
                totalHours += parseInt(part);
            }
        });
        return totalHours;
    };

    const nordicCountries = [
        { code: "SE", name: "Sweden" },
        { code: "NO", name: "Norway" },
        { code: "FI", name: "Finland" },
        { code: "DK", name: "Denmark" },
        { code: "IS", name: "Iceland" }
    ];

    const euCountries = [
        { code: "DE", name: "Germany" },
        { code: "FR", name: "France" },
        { code: "IT", name: "Italy" },
        { code: "ES", name: "Spain" },
        { code: "PL", name: "Poland" }
    ];

    const usCountries = [{ code: "US", name: "United States" }];

    const languages = [
        { code: "en", name: "English" },
        { code: "sv", name: "Swedish" },
        { code: "no", name: "Norwegian" },
        { code: "fi", name: "Finnish" },
        { code: "da", name: "Danish" }
    ];

    return (
        <Form.Group controlId="googleNewsConfigs">
            <Form.Label className="font-semibold">
                Configure Google News:
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
                        value={config.type || "search"}
                        onChange={(e) =>
                            handleConfigChange(index, "type", e.target.value)
                        }
                        className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2 ${
                            !config.lang ? "border-red-500" : ""
                        }`}
                    >
                        <option value="search">Search</option>
                        <option value="location">Location</option>
                        <option value="topic">Topic</option>
                        <option value="top_topics">Top Topics</option>
                    </Form.Control>
                    {config.type === "search" && (
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
                            className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2 ${
                                !config.country ? "border-red-500" : ""
                            }`}
                        />
                    )}
                    {config.type === "location" && (
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
                            className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2 ${
                                config.lang === "" ? "border-red-500" : ""
                            }`}
                        />
                    )}
                    {config.type === "topic" && (
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
                            className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                        >
                            <option value="WORLD">World</option>
                            <option value="NATION">Nation</option>
                            <option value="BUSINESS">Business</option>
                            <option value="TECHNOLOGY">Technology</option>
                            <option value="ENTERTAINMENT">Entertainment</option>
                            <option value="SCIENCE">Science</option>
                            <option value="SPORTS">Sports</option>
                            <option value="HEALTH">Health</option>
                        </Form.Control>
                    )}
                    <ArticleReleasedWithinComponent
                        value={config.since}
                        onChange={(value) =>
                            handleConfigChange(index, "since", value)
                        }
                    />
                    <ArticleCountComponent
                        value={config.articles}
                        onChange={(value) =>
                            handleConfigChange(index, "articles", value)
                        }
                    />
                    <LanguageComponent
                        value={config.lang}
                        onChange={(value) =>
                            handleConfigChange(index, "lang", value)
                        }
                    />
                    <CountryComponent
                        value={config.country}
                        onChange={(value) =>
                            handleConfigChange(index, "country", value)
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
                + Add another Google News config
            </Button>
        </Form.Group>
    );
}

export default GoogleNewsConfigForm;
