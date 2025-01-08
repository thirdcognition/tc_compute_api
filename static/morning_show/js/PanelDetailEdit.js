const { useState } = React;
const { Form, Button } = ReactBootstrap;

function PanelDetailEdit({
    title,
    setTitle,
    links = [],
    setLinks,
    googleNewsConfigs = [],
    setGoogleNewsConfigs,
    inputText,
    setInputText,
    yleNewsConfigs = [],
    setYleNewsConfigs
}) {
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

    return React.createElement(
        React.Fragment,
        null,

        React.createElement(
            Form.Group,
            { controlId: "title" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Title:"
            ),
            React.createElement(Form.Control, {
                type: "text",
                placeholder: "Enter title here...",
                value: title,
                onChange: (e) => setTitle(e.target.value),
                className:
                    "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            })
        ),
        React.createElement(
            Form.Group,
            { controlId: "links" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Add links (one per item):"
            ),
            linkFields.map((link, index) =>
                React.createElement(
                    "div",
                    {
                        key: index,
                        style: {
                            display: "flex",
                            alignItems: "center",
                            marginBottom: "10px"
                        }
                    },
                    React.createElement(Form.Control, {
                        type: "text",
                        placeholder: "Enter URL here...",
                        value: link,
                        onChange: (e) =>
                            handleLinkChange(index, e.target.value),
                        className:
                            "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                        style: { flexGrow: 1, marginRight: "10px" }
                    }),
                    React.createElement(
                        Button,
                        {
                            variant: "danger",
                            type: "button",
                            onClick: () => removeLinkField(index),
                            className: "py-2"
                        },
                        "Remove"
                    )
                )
            ),
            React.createElement(
                Button,
                {
                    variant: "secondary",
                    type: "button",
                    onClick: addLinkField,
                    style: { width: "100%", marginBottom: "10px" },
                    className: "py-2"
                },
                "+ Add another link"
            )
        ),
        React.createElement(
            Form.Group,
            { controlId: "yleNewsConfigs" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Configure Yle News:"
            ),
            yleNewsFields.map((config, index) =>
                React.createElement(
                    "div",
                    {
                        key: index,
                        style: {
                            border: "1px solid #ccc",
                            padding: "10px",
                            marginBottom: "10px"
                        }
                    },
                    React.createElement(
                        "div",
                        {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                marginBottom: "10px",
                                width: "100%"
                            }
                        },
                        React.createElement(
                            "h5",
                            null,
                            `Config ${index + 1}: ${config.type || "N/A"}`
                        ),
                        React.createElement(
                            Button,
                            {
                                variant: "danger",
                                type: "button",
                                onClick: () => {
                                    const newYleNewsFields =
                                        yleNewsFields.filter(
                                            (_, i) => i !== index
                                        );
                                    setYleNewsFields(newYleNewsFields);
                                    setYleNewsConfigs(newYleNewsFields);
                                },
                                className: "py-2"
                            },
                            "Remove Config"
                        )
                    ),
                    React.createElement(
                        Form.Control,
                        {
                            as: "select",
                            value: config.type || "majorHeadlines",
                            onChange: (e) =>
                                handleYleNewsConfigChange(
                                    index,
                                    "type",
                                    e.target.value
                                ),
                            style: { marginBottom: "10px" },
                            className:
                                "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                        },
                        React.createElement(
                            "option",
                            { value: "majorHeadlines" },
                            "Major Headlines"
                        ),
                        React.createElement(
                            "option",
                            { value: "mostRead" },
                            "Most Read"
                        )
                    ),
                    React.createElement(Form.Control, {
                        type: "number",
                        min: "1",
                        max: "20",
                        value: config.articles || 5,
                        onChange: (e) =>
                            handleYleNewsConfigChange(
                                index,
                                "articles",
                                parseInt(e.target.value, 10)
                            ),
                        style: { marginBottom: "10px" },
                        className:
                            "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    })
                )
            ),
            React.createElement(
                Button,
                {
                    variant: "secondary",
                    type: "button",
                    onClick: addYleNewsConfigField,
                    style: { width: "100%", marginBottom: "10px" },
                    className: "py-2"
                },
                "+ Add another Yle News config"
            )
        ),
        React.createElement(
            Form.Group,
            { controlId: "googleNewsConfigs" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Configure Google News:"
            ),
            googleNewsConfigFields.map((config, index) =>
                React.createElement(
                    "div",
                    {
                        key: index,
                        style: {
                            border: "1px solid #ccc",
                            padding: "10px",
                            marginBottom: "10px"
                        }
                    },
                    React.createElement(
                        "div",
                        {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                                marginBottom: "10px",
                                width: "100%"
                            }
                        },
                        React.createElement(
                            "h5",
                            null,
                            `Config ${index + 1}: ${config.type || "N/A"}`
                        ),
                        React.createElement(
                            Button,
                            {
                                variant: "danger",
                                type: "button",
                                onClick: () =>
                                    removeGoogleNewsConfigField(index),
                                className: "py-2"
                            },
                            "Remove Config"
                        )
                    ),
                    React.createElement(
                        Form.Control,
                        {
                            as: "select",
                            value: config.type || "search",
                            onChange: (e) =>
                                handleNewsConfigChange(
                                    index,
                                    "type",
                                    e.target.value
                                ),

                            style: { marginBottom: "10px" },
                            className: `border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 ${!config.lang ? "border-red-500" : ""}`
                        },
                        React.createElement(
                            "option",
                            { value: "search" },
                            "Search"
                        ),
                        React.createElement(
                            "option",
                            { value: "location" },
                            "Location"
                        ),
                        React.createElement(
                            "option",
                            { value: "topic" },
                            "Topic"
                        ),
                        React.createElement(
                            "option",
                            { value: "top_topics" },
                            "Top Topics"
                        )
                    ),
                    config.type === "search" &&
                        React.createElement(Form.Control, {
                            type: "text",
                            placeholder: "Enter search query...",
                            value: config.query || "",
                            onChange: (e) =>
                                handleNewsConfigChange(
                                    index,
                                    "query",
                                    e.target.value
                                ),
                            style: { marginBottom: "10px" },
                            className: `border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 ${!config.country ? "border-red-500" : ""}`
                        }),
                    config.type === "location" &&
                        React.createElement(Form.Control, {
                            type: "text",
                            placeholder: "Enter locations as CSV...",
                            value: config.location || "",
                            onChange: (e) =>
                                handleNewsConfigChange(
                                    index,
                                    "location",
                                    e.target.value
                                        .split(",")
                                        .map((loc) => loc.trim())
                                ),
                            style: { marginBottom: "10px" },
                            className: `border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 ${config.lang === "" ? "border-red-500" : ""}`
                        }),
                    config.type === "topic" &&
                        React.createElement(
                            Form.Control,
                            {
                                as: "select",
                                multiple: true,
                                value: config.topic || [],
                                onChange: (e) =>
                                    handleNewsConfigChange(
                                        index,
                                        "topic",
                                        Array.from(
                                            e.target.selectedOptions,
                                            (option) => option.value
                                        )
                                    ),
                                style: { marginBottom: "10px" },
                                className:
                                    "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                            },
                            React.createElement(
                                "option",
                                { value: "WORLD" },
                                "World"
                            ),
                            React.createElement(
                                "option",
                                { value: "NATION" },
                                "Nation"
                            ),
                            React.createElement(
                                "option",
                                { value: "BUSINESS" },
                                "Business"
                            ),
                            React.createElement(
                                "option",
                                { value: "TECHNOLOGY" },
                                "Technology"
                            ),
                            React.createElement(
                                "option",
                                { value: "ENTERTAINMENT" },
                                "Entertainment"
                            ),
                            React.createElement(
                                "option",
                                { value: "SCIENCE" },
                                "Science"
                            ),
                            React.createElement(
                                "option",
                                { value: "SPORTS" },
                                "Sports"
                            ),
                            React.createElement(
                                "option",
                                { value: "HEALTH" },
                                "Health"
                            )
                        ),
                    React.createElement(
                        Form.Group,
                        { controlId: `lang-${index}` },
                        React.createElement(
                            Form.Label,
                            { className: "font-semibold" },
                            "Language:"
                        ),
                        React.createElement(Form.Control, {
                            type: "text",
                            placeholder: "Enter language code...",
                            value: config.lang,
                            onChange: (e) =>
                                handleNewsConfigChange(
                                    index,
                                    "lang",
                                    e.target.value
                                ),
                            style: { marginBottom: "10px" },
                            className: `border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 ${config.country === "" ? "border-red-500" : ""}`
                        })
                    ),
                    React.createElement(
                        Form.Group,
                        { controlId: `country-${index}` },
                        React.createElement(
                            Form.Label,
                            { className: "font-semibold" },
                            "Country:"
                        ),
                        React.createElement(Form.Control, {
                            type: "text",
                            placeholder: "Enter country code...",
                            value: config.country,
                            onChange: (e) =>
                                handleNewsConfigChange(
                                    index,
                                    "country",
                                    e.target.value
                                ),
                            style: { marginBottom: "10px" },
                            className:
                                "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                        })
                    ),
                    React.createElement(
                        "div",
                        {
                            style: {
                                display: "flex",
                                alignItems: "flex-start",
                                marginBottom: "10px",
                                flexDirection: "column",
                                width: "100%"
                            }
                        },
                        React.createElement(
                            "label",
                            {
                                style: {
                                    marginBottom: "5px",
                                    alignSelf: "flex-start"
                                }
                            },
                            React.createElement("input", {
                                type: "checkbox",
                                checked: config.since !== undefined,
                                onChange: (e) =>
                                    handleNewsConfigChange(
                                        index,
                                        "since",
                                        e.target.checked ? 0 : undefined
                                    )
                            }),
                            " Article has to be released within"
                        ),
                        config.since !== undefined &&
                            React.createElement(
                                "div",
                                {
                                    style: {
                                        display: "flex",
                                        alignItems: "flex-start",
                                        width: "100%"
                                    }
                                },
                                React.createElement(Form.Control, {
                                    type: "range",
                                    min: "0",
                                    max: "1440", // 2 months in hours
                                    value:
                                        convertTimeFormatToHours(
                                            config.since
                                        ) || "0",
                                    onChange: (e) =>
                                        handleNewsConfigChange(
                                            index,
                                            "since",
                                            convertHoursToTimeFormat(
                                                e.target.value
                                            )
                                        ),
                                    className:
                                        "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                                    style: { marginRight: "10px", flexGrow: 1 }
                                }),
                                React.createElement(
                                    "span",
                                    {
                                        style: {
                                            width: "120px",
                                            textAlign: "left"
                                        }
                                    },
                                    config.since || "0h"
                                )
                            )
                    ),
                    React.createElement(
                        "div",
                        {
                            style: {
                                display: "flex",
                                alignItems: "flex-start",
                                marginBottom: "10px",
                                flexDirection: "column",
                                width: "100%"
                            }
                        },
                        React.createElement(
                            "label",
                            {
                                style: {
                                    marginBottom: "5px",
                                    alignSelf: "flex-start"
                                }
                            },
                            React.createElement("input", {
                                type: "checkbox",
                                checked: config.articles !== undefined,
                                onChange: (e) =>
                                    handleNewsConfigChange(
                                        index,
                                        "articles",
                                        e.target.checked ? 1 : undefined
                                    )
                            }),
                            " Maximum articles"
                        ),
                        config.articles !== undefined &&
                            React.createElement(
                                "div",
                                {
                                    style: {
                                        display: "flex",
                                        alignItems: "center",
                                        width: "100%"
                                    }
                                },
                                React.createElement(Form.Control, {
                                    type: "range",
                                    min: "1",
                                    max: "20",
                                    value: config.articles || "1",
                                    onChange: (e) =>
                                        handleNewsConfigChange(
                                            index,
                                            "articles",
                                            e.target.value
                                        ),
                                    className:
                                        "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                                    style: { marginRight: "10px", flexGrow: 1 }
                                }),
                                React.createElement(
                                    "span",
                                    {
                                        style: {
                                            width: "120px",
                                            textAlign: "left"
                                        }
                                    },
                                    config.articles || 1
                                )
                            )
                    )
                )
            ),
            React.createElement(
                Button,
                {
                    variant: "secondary",
                    type: "button",
                    onClick: addGoogleNewsConfigField,
                    style: { width: "100%", marginBottom: "10px" },
                    className: "py-2"
                },
                "+ Add another Google News config"
            )
        ),
        React.createElement(
            Form.Group,
            { controlId: "inputText" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Input Text:"
            ),
            React.createElement(Form.Control, {
                as: "textarea",
                rows: 5,
                placeholder: "Enter text here...",
                value: inputText,
                onChange: (e) => setInputText(e.target.value),
                className:
                    "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            })
        )
    );
}

export default PanelDetailEdit;
