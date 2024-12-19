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
    setInputText
}) {
    const [linkFields, setLinkFields] = useState(links);
    const [newsConfigFields, setNewsConfigFields] = useState(googleNewsConfigs);

    const handleLinkChange = (index, value) => {
        const newLinkFields = [...linkFields];
        newLinkFields[index] = value;
        setLinkFields(newLinkFields);
        setLinks(newLinkFields);
    };

    const addLinkField = () => {
        setLinkFields([...linkFields, ""]);
    };

    const handleNewsConfigChange = (index, key, value) => {
        const newNewsConfigFields = [...newsConfigFields];
        if (!newNewsConfigFields[index]) {
            newNewsConfigFields[index] = {};
        }
        newNewsConfigFields[index][key] = value;
        setNewsConfigFields(newNewsConfigFields);
        setGoogleNewsConfigs(newNewsConfigFields);
    };

    const addNewsConfigField = () => {
        setNewsConfigFields([...newsConfigFields, { type: "topic" }]);
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
                React.createElement(Form.Control, {
                    key: index,
                    type: "text",
                    placeholder: "Enter URL here...",
                    value: link,
                    onChange: (e) => handleLinkChange(index, e.target.value),
                    style: { marginBottom: "10px" },
                    className:
                        "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                })
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
            { controlId: "googleNewsConfigs" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Configure Google News:"
            ),
            newsConfigFields.map((config, index) =>
                React.createElement(
                    React.Fragment,
                    { key: index },
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
                            className:
                                "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
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
                            className:
                                "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                        }),
                    config.type === "location" &&
                        React.createElement(Form.Control, {
                            type: "text",
                            placeholder: "Enter location...",
                            value: config.location || "",
                            onChange: (e) =>
                                handleNewsConfigChange(
                                    index,
                                    "location",
                                    e.target.value
                                ),
                            style: { marginBottom: "10px" },
                            className:
                                "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                        }),
                    config.type === "topic" &&
                        React.createElement(
                            Form.Control,
                            {
                                as: "select",
                                value: config.topic || "",
                                onChange: (e) =>
                                    handleNewsConfigChange(
                                        index,
                                        "topic",
                                        e.target.value
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
                        "div",
                        {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                marginBottom: "10px"
                            }
                        },
                        React.createElement(
                            "label",
                            { style: { marginRight: "10px" } },
                            React.createElement("input", {
                                type: "checkbox",
                                checked:
                                    config.useDaysHours !== undefined
                                        ? config.useDaysHours
                                        : config.type === "topic",
                                onChange: (e) =>
                                    handleNewsConfigChange(
                                        index,
                                        "useDaysHours",
                                        e.target.checked
                                    )
                            }),
                            " Article has to be released within"
                        ),
                        config.useDaysHours &&
                            React.createElement(
                                "div",
                                {
                                    style: {
                                        display: "flex",
                                        alignItems: "center"
                                    }
                                },
                                React.createElement(
                                    "label",
                                    { style: { marginRight: "5px" } },
                                    "Days:"
                                ),
                                React.createElement(
                                    Form.Control,
                                    {
                                        as: "select",
                                        value: config.days || "0",
                                        onChange: (e) =>
                                            handleNewsConfigChange(
                                                index,
                                                "days",
                                                e.target.value
                                            ),
                                        className:
                                            "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                                        style: { marginRight: "10px" }
                                    },
                                    Array.from({ length: 31 }, (_, i) =>
                                        React.createElement(
                                            "option",
                                            { key: i, value: i },
                                            `${i} days`
                                        )
                                    )
                                ),
                                React.createElement(
                                    "label",
                                    { style: { marginRight: "5px" } },
                                    "Hours:"
                                ),
                                React.createElement(
                                    Form.Control,
                                    {
                                        as: "select",
                                        value: config.hours || "0",
                                        onChange: (e) =>
                                            handleNewsConfigChange(
                                                index,
                                                "hours",
                                                e.target.value
                                            ),
                                        className:
                                            "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                                    },
                                    Array.from({ length: 24 }, (_, i) =>
                                        React.createElement(
                                            "option",
                                            { key: i, value: i },
                                            `${i} hours`
                                        )
                                    )
                                )
                            )
                    ),
                    React.createElement(
                        "div",
                        {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                marginBottom: "10px"
                            }
                        },
                        React.createElement(
                            "label",
                            { style: { marginRight: "10px" } },
                            React.createElement("input", {
                                type: "checkbox",
                                checked:
                                    config.useNumberSelect !== undefined
                                        ? config.useNumberSelect
                                        : config.type === "topic",
                                onChange: (e) =>
                                    handleNewsConfigChange(
                                        index,
                                        "useNumberSelect",
                                        e.target.checked
                                    )
                            }),
                            " Maximum articles"
                        ),
                        config.useNumberSelect &&
                            React.createElement(
                                "div",
                                {
                                    style: {
                                        display: "flex",
                                        alignItems: "center"
                                    }
                                },
                                React.createElement(
                                    "label",
                                    { style: { marginRight: "5px" } },
                                    "Articles:"
                                ),
                                React.createElement(
                                    Form.Control,
                                    {
                                        as: "select",
                                        value: config.articles || "1",
                                        onChange: (e) =>
                                            handleNewsConfigChange(
                                                index,
                                                "articles",
                                                e.target.value
                                            ),
                                        className:
                                            "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                                    },
                                    Array.from({ length: 100 }, (_, i) =>
                                        React.createElement(
                                            "option",
                                            { key: i, value: i + 1 },
                                            `${i + 1}`
                                        )
                                    )
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
                    onClick: addNewsConfigField,
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
