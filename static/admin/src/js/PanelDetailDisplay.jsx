import { useState } from "react";

const PanelDetailDisplay = ({ panel }) => {
    const [showDetails, setShowDetails] = useState(false);

    if (!panel) {
        return (
            <div className="panel-detail-display border p-3 mb-4 rounded">
                No panel data available.
            </div>
        );
    }

    const links = panel.links || [];
    const metadata = panel.metadata || {};
    const googleNewsConfigs = metadata.google_news || [];
    const yleNewsConfigs = metadata.yle_news || [];
    const techCrunchNewsConfigs = metadata.techcrunch_news || [];
    const inputText = panel.inputText || "";

    return (
        <div className="panel-detail-display border p-3 mb-4 rounded">
            {panel.title && <h2 className="font-bold mb-2">{panel.title}</h2>}
            {inputText && (
                <div className="border p-3 mb-4 rounded">
                    <strong className="font-semibold">Input Text:</strong>
                    <p className="mb-2">{inputText}</p>
                </div>
            )}
            {links.length > 0 && (
                <div>
                    <strong className="font-semibold">Links:</strong>
                    {links.map((link, index) => (
                        <p key={index} className="ml-4">
                            <a
                                href={link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500 underline"
                            >
                                {link}
                            </a>
                        </p>
                    ))}
                </div>
            )}
            <button
                onClick={() => setShowDetails(!showDetails)}
                className="w-full py-2 mb-4 flex items-center justify-center bg-blue-500 text-white rounded"
            >
                <span className="mr-2">{showDetails ? "▼" : "▶"}</span>
                <span>
                    {showDetails ? "Hide Details" : "Show More Details"}
                </span>
            </button>
            {showDetails && (
                <div className="border p-3 mb-4 rounded">
                    {metadata.urls &&
                        Array.isArray(metadata.urls) &&
                        metadata.urls.length > 0 && (
                            <div>
                                <strong className="font-semibold">
                                    Metadata URLs:
                                </strong>
                                {metadata.urls.map((url, index) => (
                                    <p key={index} className="ml-4">
                                        <a
                                            href={url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-blue-500 underline"
                                        >
                                            {url}
                                        </a>
                                    </p>
                                ))}
                            </div>
                        )}
                    {metadata.longform !== undefined && (
                        <p className="mb-2">
                            Process every article separately. (higher quality,
                            longer process time):{" "}
                            {metadata.longform ? "Yes" : "No"}
                        </p>
                    )}
                    {googleNewsConfigs.length > 0 && (
                        <div>
                            <strong className="font-semibold">
                                Google News Configurations:
                            </strong>
                            {googleNewsConfigs.map((config, index) => (
                                <div key={index} className="ml-4 mb-2">
                                    {config.lang && (
                                        <p>Language: {config.lang}</p>
                                    )}
                                    {config.country && (
                                        <p>Country: {config.country}</p>
                                    )}
                                    {config.topics && (
                                        <p>
                                            Topics:{" "}
                                            {Array.isArray(config.topics)
                                                ? config.topics.join(", ")
                                                : config.topics}
                                        </p>
                                    )}
                                    {config.query && (
                                        <p>Query: {config.query}</p>
                                    )}
                                    {config.location && (
                                        <p>
                                            Location:{" "}
                                            {Array.isArray(config.location)
                                                ? config.location.join(", ")
                                                : config.location}
                                        </p>
                                    )}
                                    {config.since && (
                                        <p>Since: {config.since}</p>
                                    )}
                                    {config.articles && (
                                        <p>Articles: {config.articles}</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                    {techCrunchNewsConfigs.length > 0 && (
                        <div>
                            <strong className="font-semibold">
                                TechCrunch News Configurations:
                            </strong>
                            {techCrunchNewsConfigs.map((config, index) => (
                                <div key={index} className="ml-4 mb-2">
                                    {config.articles && (
                                        <p>Articles: {config.articles}</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                    {yleNewsConfigs.length > 0 && (
                        <div>
                            <strong className="font-semibold">
                                Yle News Configurations:
                            </strong>
                            {yleNewsConfigs.map((config, index) => (
                                <div key={index} className="ml-4 mb-2">
                                    {config.type && <p>Type: {config.type}</p>}
                                    {config.articles && (
                                        <p>Articles: {config.articles}</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default PanelDetailDisplay;
