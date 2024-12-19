const { useState } = React;

const PanelDetailDisplay = ({ panel }) => {
    if (!panel) {
        return React.createElement(
            "div",
            { className: "panel-detail-display border p-3 mb-4 rounded" },
            "No panel data available."
        );
    }

    const [showDetails, setShowDetails] = useState(false);
    const links = panel.links || [];
    const metadata = panel.metadata || {};

    return React.createElement(
        "div",
        { className: "panel-detail-display border p-3 mb-4 rounded" },
        panel.title &&
            React.createElement(
                "h2",
                { className: "font-bold mb-2" },
                panel.title
            ),
        panel.inputText &&
            React.createElement(
                "p",
                { className: "mb-2" },
                `Input Text: ${panel.inputText}`
            ),
        links.length > 0 &&
            React.createElement(
                "div",
                null,
                React.createElement(
                    "strong",
                    { className: "font-semibold" },
                    "Links:"
                ),
                links.map((link, index) =>
                    React.createElement(
                        "p",
                        { key: index, className: "ml-4" },
                        React.createElement(
                            "a",
                            {
                                href: link,
                                target: "_blank",
                                rel: "noopener noreferrer",
                                className: "text-blue-500 underline"
                            },
                            link
                        )
                    )
                )
            ),
        React.createElement(
            "button",
            {
                onClick: () => setShowDetails(!showDetails),
                className:
                    "w-full py-2 mb-4 flex items-center justify-center bg-blue-500 text-white rounded"
            },
            React.createElement(
                "span",
                { className: "mr-2" },
                showDetails ? "▼" : "▶"
            ),
            React.createElement(
                "span",
                null,
                showDetails ? "Hide Details" : "Show More Details"
            )
        ),
        showDetails &&
            React.createElement(
                "div",
                { className: "border p-3 mb-4 rounded" },
                metadata.urls &&
                    metadata.urls.length > 0 &&
                    React.createElement(
                        "div",
                        null,
                        React.createElement(
                            "strong",
                            { className: "font-semibold" },
                            "Metadata URLs:"
                        ),
                        metadata.urls.map((url, index) =>
                            React.createElement(
                                "p",
                                { key: index, className: "ml-4" },
                                React.createElement(
                                    "a",
                                    {
                                        href: url,
                                        target: "_blank",
                                        rel: "noopener noreferrer",
                                        className: "text-blue-500 underline"
                                    },
                                    url
                                )
                            )
                        )
                    ),
                metadata.longform !== undefined &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Longform: ${metadata.longform ? "Yes" : "No"}`
                    )
            )
    );
};

export default PanelDetailDisplay;
