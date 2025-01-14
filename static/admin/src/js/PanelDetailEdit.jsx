import { useState } from "react";
import { Form, Button } from "react-bootstrap";
import { handleCreatePanel } from "./helpers/panel.js";

function PanelDetailEdit({
    setPanelId,
    taskStatus,
    setSelectedPanel,
    fetchPanels,
    handleRefreshPanelData,
    setRedirectToPanel
}) {
    const [title, setTitle] = useState("");
    const [links, setLinks] = useState([]);
    const [googleNewsConfigs, setGoogleNewsConfigs] = useState([]);
    const [inputText, setInputText] = useState("");
    const [yleNewsConfigs, setYleNewsConfigs] = useState([]);

    const [linkFields, setLinkFields] = useState(links);
    const [googleNewsConfigFields, setGoogleNewsConfigFields] =
        useState(googleNewsConfigs);
    const [yleNewsFields, setYleNewsFields] = useState(yleNewsConfigs);

    const handleLinkChange = (index, value) => {
        const newLinkFields = [...linkFields];
        newLinkFields[index] = value;
        setLinkFields(newLinkFields);
        setLinks(newLinkFields);
    };

    const addLinkField = () => {
        setLinkFields([...linkFields, ""]);
    };

    const removeLinkField = (index) => {
        const newLinkFields = linkFields.filter((_, i) => i !== index);
        setLinkFields(newLinkFields);
        setLinks(newLinkFields);
    };

    const handleNewsConfigChange = (index, key, value) => {
        const newNewsConfigFields = [...googleNewsConfigFields];
        if (!newNewsConfigFields[index]) {
            newNewsConfigFields[index] = {};
        }
        if ((key === "lang" || key === "country") && value === "") {
            newNewsConfigFields[index][key] = "";
        } else {
            newNewsConfigFields[index][key] = value;
        }
        setGoogleNewsConfigFields(newNewsConfigFields);
        setGoogleNewsConfigs(newNewsConfigFields);
    };

    const addGoogleNewsConfigField = () => {
        const newNewsConfigFields = [
            ...googleNewsConfigFields,
            { type: "topic", lang: "en", country: "US" }
        ];
        setGoogleNewsConfigFields(newNewsConfigFields);
        setGoogleNewsConfigs(newNewsConfigFields);
    };
    const removeGoogleNewsConfigField = (index) => {
        const newNewsConfigFields = googleNewsConfigFields.filter(
            (_, i) => i !== index
        );
        setGoogleNewsConfigFields(newNewsConfigFields);
        setGoogleNewsConfigs(newNewsConfigFields);
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

    const handleYleNewsConfigChange = (index, key, value) => {
        const newYleNewsFields = [...yleNewsFields];
        if (!newYleNewsFields[index]) {
            newYleNewsFields[index] = {};
        }
        newYleNewsFields[index][key] = value;
        setYleNewsFields(newYleNewsFields);
        setYleNewsConfigs(newYleNewsFields);
    };

    const addYleNewsConfigField = () => {
        const newYleNewsFields = [
            ...yleNewsFields,
            { type: "majorHeadlines", articles: 5 }
        ];
        setYleNewsFields(newYleNewsFields);
        setYleNewsConfigs(newYleNewsFields);
    };

    const handlePanelSubmit = async (e) => {
        e.preventDefault();
        handleCreatePanel({
            title,
            inputText,
            links,
            googleNewsConfigs,
            yleNewsConfigs
        }).then(({ panelId, success }) => {
            if (success && panelId) {
                setSelectedPanel(panelId);
                setPanelId(panelId);
                handleRefreshPanelData(panelId);
                fetchPanels();
                setRedirectToPanel(true);
            } else {
                alert("Error while creating panel.");
            }
        });
    };

    return (
        <>
            <div className="panel-container border p-3 mb-4 rounded">
                <h3 className="font-bold mb-3">Create Panel</h3>
                <Form onSubmit={handlePanelSubmit}>
                    <Form.Group controlId="title">
                        <Form.Label className="font-semibold">
                            Title:
                        </Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Enter title here..."
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                        />
                    </Form.Group>
                    <Form.Group controlId="links">
                        <Form.Label className="font-semibold">
                            Add links (one per item):
                        </Form.Label>
                        {linkFields.map((link, index) => (
                            <div key={index} className="flex items-center mb-2">
                                <Form.Control
                                    type="text"
                                    placeholder="Enter URL here..."
                                    value={link}
                                    onChange={(e) =>
                                        handleLinkChange(index, e.target.value)
                                    }
                                    className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 flex-grow mr-2"
                                />
                                <Button
                                    variant="danger"
                                    type="button"
                                    onClick={() => removeLinkField(index)}
                                    className="py-2"
                                >
                                    Remove
                                </Button>
                            </div>
                        ))}
                        <Button
                            variant="secondary"
                            type="button"
                            onClick={addLinkField}
                            className="w-full mb-2 py-2"
                        >
                            + Add another link
                        </Button>
                    </Form.Group>
                    <Form.Group controlId="yleNewsConfigs">
                        <Form.Label className="font-semibold">
                            Configure Yle News:
                        </Form.Label>
                        {yleNewsFields.map((config, index) => (
                            <div
                                key={index}
                                className="border border-gray-300 p-2 mb-2"
                            >
                                <div className="flex items-center justify-between mb-2 w-full">
                                    <h5>
                                        Config {index + 1}:{" "}
                                        {config.type || "N/A"}
                                    </h5>
                                    <Button
                                        variant="danger"
                                        type="button"
                                        onClick={() => {
                                            const newYleNewsFields =
                                                yleNewsFields.filter(
                                                    (_, i) => i !== index
                                                );
                                            setYleNewsFields(newYleNewsFields);
                                            setYleNewsConfigs(newYleNewsFields);
                                        }}
                                        className="py-2"
                                    >
                                        Remove Config
                                    </Button>
                                </div>
                                <Form.Control
                                    as="select"
                                    value={config.type || "majorHeadlines"}
                                    onChange={(e) =>
                                        handleYleNewsConfigChange(
                                            index,
                                            "type",
                                            e.target.value
                                        )
                                    }
                                    className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                                >
                                    <option value="majorHeadlines">
                                        Major Headlines
                                    </option>
                                    <option value="mostRead">Most Read</option>
                                </Form.Control>
                                <Form.Control
                                    type="number"
                                    min="1"
                                    max="20"
                                    value={config.articles || 5}
                                    onChange={(e) =>
                                        handleYleNewsConfigChange(
                                            index,
                                            "articles",
                                            parseInt(e.target.value, 10)
                                        )
                                    }
                                    className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                                />
                            </div>
                        ))}
                        <Button
                            variant="secondary"
                            type="button"
                            onClick={addYleNewsConfigField}
                            className="w-full mb-2 py-2"
                        >
                            + Add another Yle News config
                        </Button>
                    </Form.Group>
                    <Form.Group controlId="googleNewsConfigs">
                        <Form.Label className="font-semibold">
                            Configure Google News:
                        </Form.Label>
                        {googleNewsConfigFields.map((config, index) => (
                            <div
                                key={index}
                                className="border border-gray-300 p-2 mb-2"
                            >
                                <div className="flex items-center justify-between mb-2 w-full">
                                    <h5>
                                        Config {index + 1}:{" "}
                                        {config.type || "N/A"}
                                    </h5>
                                    <Button
                                        variant="danger"
                                        type="button"
                                        onClick={() =>
                                            removeGoogleNewsConfigField(index)
                                        }
                                        className="py-2"
                                    >
                                        Remove Config
                                    </Button>
                                </div>
                                <Form.Control
                                    as="select"
                                    value={config.type || "search"}
                                    onChange={(e) =>
                                        handleNewsConfigChange(
                                            index,
                                            "type",
                                            e.target.value
                                        )
                                    }
                                    className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2 ${
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
                                {config.type === "search" && (
                                    <Form.Control
                                        type="text"
                                        placeholder="Enter search query..."
                                        value={config.query || ""}
                                        onChange={(e) =>
                                            handleNewsConfigChange(
                                                index,
                                                "query",
                                                e.target.value
                                            )
                                        }
                                        className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2 ${
                                            !config.country
                                                ? "border-red-500"
                                                : ""
                                        }`}
                                    />
                                )}
                                {config.type === "location" && (
                                    <Form.Control
                                        type="text"
                                        placeholder="Enter locations as CSV..."
                                        value={config.location || ""}
                                        onChange={(e) =>
                                            handleNewsConfigChange(
                                                index,
                                                "location",
                                                e.target.value
                                                    .split(",")
                                                    .map((loc) => loc.trim())
                                            )
                                        }
                                        className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2 ${
                                            config.lang === ""
                                                ? "border-red-500"
                                                : ""
                                        }`}
                                    />
                                )}
                                {config.type === "topic" && (
                                    <Form.Control
                                        as="select"
                                        multiple
                                        value={config.topic || []}
                                        onChange={(e) =>
                                            handleNewsConfigChange(
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
                                )}
                                <Form.Group controlId={`lang-${index}`}>
                                    <Form.Label className="font-semibold">
                                        Language:
                                    </Form.Label>
                                    <Form.Control
                                        type="text"
                                        placeholder="Enter language code..."
                                        value={config.lang}
                                        onChange={(e) =>
                                            handleNewsConfigChange(
                                                index,
                                                "lang",
                                                e.target.value
                                            )
                                        }
                                        className={`border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2 ${
                                            config.country === ""
                                                ? "border-red-500"
                                                : ""
                                        }`}
                                    />
                                </Form.Group>
                                <Form.Group controlId={`country-${index}`}>
                                    <Form.Label className="font-semibold">
                                        Country:
                                    </Form.Label>
                                    <Form.Control
                                        type="text"
                                        placeholder="Enter country code..."
                                        value={config.country}
                                        onChange={(e) =>
                                            handleNewsConfigChange(
                                                index,
                                                "country",
                                                e.target.value
                                            )
                                        }
                                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
                                    />
                                </Form.Group>
                                <div className="flex items-start mb-2 flex-col w-full">
                                    <label className="mb-1 self-start">
                                        <input
                                            type="checkbox"
                                            checked={config.since !== undefined}
                                            onChange={(e) =>
                                                handleNewsConfigChange(
                                                    index,
                                                    "since",
                                                    e.target.checked
                                                        ? 0
                                                        : undefined
                                                )
                                            }
                                        />
                                        {" Article has to be released within"}
                                    </label>
                                    {config.since !== undefined && (
                                        <div className="flex items-start w-full">
                                            <Form.Control
                                                type="range"
                                                min="0"
                                                max="1440" // 2 months in hours
                                                value={
                                                    convertTimeFormatToHours(
                                                        config.since
                                                    ) || "0"
                                                }
                                                onChange={(e) =>
                                                    handleNewsConfigChange(
                                                        index,
                                                        "since",
                                                        convertHoursToTimeFormat(
                                                            e.target.value
                                                        )
                                                    )
                                                }
                                                className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mr-2 flex-grow"
                                            />
                                            <span className="w-30 text-left">
                                                {config.since || "0h"}
                                            </span>
                                        </div>
                                    )}
                                </div>
                                <div className="flex items-start mb-2 flex-col w-full">
                                    <label className="mb-1 self-start">
                                        <input
                                            type="checkbox"
                                            checked={
                                                config.articles !== undefined
                                            }
                                            onChange={(e) =>
                                                handleNewsConfigChange(
                                                    index,
                                                    "articles",
                                                    e.target.checked
                                                        ? 1
                                                        : undefined
                                                )
                                            }
                                        />
                                        {" Maximum articles"}
                                    </label>
                                    {config.articles !== undefined && (
                                        <div className="flex items-center w-full">
                                            <Form.Control
                                                type="range"
                                                min="1"
                                                max="20"
                                                value={config.articles || "1"}
                                                onChange={(e) =>
                                                    handleNewsConfigChange(
                                                        index,
                                                        "articles",
                                                        e.target.value
                                                    )
                                                }
                                                className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mr-2 flex-grow"
                                            />
                                            <span className="w-30 text-left">
                                                {config.articles || 1}
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        <Button
                            variant="secondary"
                            type="button"
                            onClick={addGoogleNewsConfigField}
                            className="w-full mb-2 py-2"
                        >
                            + Add another Google News config
                        </Button>
                    </Form.Group>
                    <Form.Group controlId="inputText">
                        <Form.Label className="font-semibold">
                            Input Text:
                        </Form.Label>
                        <Form.Control
                            as="textarea"
                            rows={5}
                            placeholder="Enter text here..."
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                        />
                    </Form.Group>
                    <Button
                        variant="primary"
                        type="submit"
                        className="w-full py-2"
                        disabled={
                            taskStatus === "idle"
                                ? false
                                : taskStatus !== "failure" &&
                                  taskStatus !== "success"
                        }
                    >
                        Create Panel
                    </Button>
                </Form>
            </div>
        </>
    );
}

export default PanelDetailEdit;
