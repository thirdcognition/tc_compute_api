import { useState } from "react";
import { fetchNewsLinks } from "./helpers/fetch.js";
import { Button } from "react-bootstrap";
import PanelDetailEdit from "./PanelDetailEdit";
import { conceptsMap } from "./news_config/YleNewsConfigForm";

const PanelDetailDisplay = ({ panel, isEditMode = false, taskStatus }) => {
    const [showDetails, setShowDetails] = useState(false);
    const [newsLinks, setNewsLinks] = useState([]);
    const [error, setError] = useState(null);
    const [runningConfigTest, setRunningConfigTest] = useState(false);

    const handleTestConfigs = async () => {
        setRunningConfigTest(true); // Start the progress indicator
        const configs = {
            news_guidance: panel?.metadata?.news_guidance || "",
            news_items: parseInt(panel?.metadata?.news_items || 5),
            google_news: panel?.metadata?.google_news,
            yle_news: panel?.metadata?.yle_news,
            techcrunch_news: panel?.metadata?.techcrunch_news,
            hackernews: panel?.metadata?.hackernews
        };

        try {
            const response = await fetchNewsLinks(configs);
            console.log("News links", response);
            setNewsLinks(response || []);
            setError(null);
        } catch (err) {
            setError(
                "Failed to fetch news links. Please check your configurations."
            );
            setNewsLinks([]);
        } finally {
            setRunningConfigTest(false); // Stop the progress indicator
        }
    };
    const [isEditing, setIsEditing] = useState(false);

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
    const hackerNewsConfigs = metadata.hackernews || [];
    const techCrunchNewsConfigs = metadata.techcrunch_news || [];
    const inputText = panel.inputText || "";

    console.log("panel", panel);

    if (isEditing) {
        return (
            <PanelDetailEdit
                panel={panel}
                onCancel={() => setIsEditing(false)}
            />
        );
    }

    return (
        <div className="panel-detail-display border p-3 mb-4 rounded">
            {panel.title && <h2 className="font-bold mb-2">{panel.title}</h2>}
            {panel.metadata?.languages && (
                <p className="mb-2">
                    <strong className="font-semibold">
                        Additional languages:
                    </strong>
                    &nbsp;
                    {panel.metadata.languages.join(", ")}
                </p>
            )}
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
                    {metadata.news_items && (
                        <p>
                            <strong className="font-semibold mr-2">
                                News items:
                            </strong>
                            {metadata.news_items}
                        </p>
                    )}
                    {metadata.news_guidance && (
                        <>
                            <p>
                                <strong className="font-semibold">
                                    News Guidance:
                                </strong>
                            </p>
                            <p className="pl-5 mb-2">
                                {metadata.news_guidance}
                            </p>
                        </>
                    )}
                    {metadata.urls &&
                        Array.isArray(metadata.urls) &&
                        metadata.urls.length > 0 && (
                            <div className="mb-4">
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
                                            ({index + 1}): {url}
                                        </a>
                                    </p>
                                ))}
                            </div>
                        )}

                    {googleNewsConfigs.length > 0 && (
                        <div className="mb-4">
                            <strong className="font-semibold">
                                Google News Configurations:
                            </strong>
                            {googleNewsConfigs.map((config, index) => (
                                <div key={index} className="ml-4 mb-2">
                                    <p className="mt-2">
                                        <strong className="font-semibold">
                                            Config {index + 1}:
                                        </strong>
                                    </p>
                                    {config.feed_type && (
                                        <p>Type: {config.feed_type}</p>
                                    )}

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
                                </div>
                            ))}
                        </div>
                    )}

                    {techCrunchNewsConfigs.length > 0 && (
                        <div className="mb-4">
                            <strong className="font-semibold">
                                TechCrunch News Configurations:
                            </strong>
                            {techCrunchNewsConfigs.map((config, index) => (
                                <div key={index} className="ml-4 mb-2">
                                    <p className="mt-2">
                                        <strong className="font-semibold">
                                            Config {index + 1}:
                                        </strong>
                                    </p>
                                    {config.articles && (
                                        <p>Articles: {config.articles}</p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                    {yleNewsConfigs.length > 0 && (
                        <div className="mb-4">
                            <strong className="font-semibold">
                                Yle News Configurations:
                            </strong>
                            {yleNewsConfigs.map((config, index) => (
                                <div key={index} className="ml-4 mb-2">
                                    <p className="mt-2">
                                        <strong className="font-semibold">
                                            Config {index + 1}:
                                        </strong>
                                    </p>
                                    {(config.feed_type || config.type) && (
                                        <p>
                                            Type:{" "}
                                            {config.feed_type || config.type}
                                        </p>
                                    )}
                                    {config.lang && (
                                        <p>Language: {config.lang}</p>
                                    )}
                                    {config.topics && (
                                        <p>
                                            Topics:{" "}
                                            {config.topics
                                                .map(
                                                    (id) =>
                                                        conceptsMap.topics.find(
                                                            (topic) =>
                                                                topic.id === id
                                                        )?.title || id
                                                )
                                                .join(", ")}
                                        </p>
                                    )}
                                    {config.locations && (
                                        <p>
                                            Locations:{" "}
                                            {config.locations
                                                .map(
                                                    (id) =>
                                                        conceptsMap.locations.find(
                                                            (location) =>
                                                                location.id ===
                                                                id
                                                        )?.title || id
                                                )
                                                .join(", ")}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                    {hackerNewsConfigs.length > 0 && (
                        <div className="mb-4">
                            <strong className="font-semibold">
                                Hacker News Configurations:
                            </strong>
                            {hackerNewsConfigs.map((config, index) => (
                                <div key={index} className="ml-4 mb-2">
                                    <p className="mt-2">
                                        <strong className="font-semibold">
                                            Config {index + 1}:
                                        </strong>
                                    </p>
                                    {config.feed_type && (
                                        <p>Feed Type: {config.feed_type}</p>
                                    )}
                                    {config.query && (
                                        <p>Query: {config.query}</p>
                                    )}
                                    {config.points !== undefined && (
                                        <p>Minimum Points: {config.points}</p>
                                    )}
                                    {config.comments !== undefined && (
                                        <p>
                                            Minimum Comments: {config.comments}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
            <button
                onClick={() => setIsEditing(true)}
                disabled={taskStatus !== "idle"}
                className={`w-full py-2 mb-4 mt-4 flex items-center justify-center rounded ${
                    taskStatus === "idle"
                        ? "bg-green-500 text-white"
                        : "bg-gray-500 text-gray-300"
                }`}
            >
                Edit Configuration
            </button>
            <Button
                variant="info"
                onClick={handleTestConfigs}
                className="py-2 mt-3 w-full bg-green-500 text-white"
                disabled={runningConfigTest} // Disable the button while testing
            >
                {runningConfigTest ? "Processing..." : "Test Panel Sources"}{" "}
            </Button>
            {error && <p className="text-danger mt-2">{error}</p>}
            {newsLinks.length > 0 && (
                <div className="mt-4">
                    <h5>Fetched News Links:</h5>
                    <div className="grid grid-cols-1 gap-4">
                        {newsLinks.map((group, groupIndex) => (
                            <div key={groupIndex} className="news-group">
                                <h6>{group.title || "Group " + groupIndex}</h6>
                                {group.data.web_sources.map((link, index) => (
                                    <div
                                        key={index}
                                        className="border p-4 rounded shadow"
                                    >
                                        <div className="flex gap-4 items-start">
                                            {link.image && (
                                                <img
                                                    src={link.image}
                                                    alt={link.title}
                                                    className="w-32 h-32 object-cover rounded"
                                                />
                                            )}
                                            <div className="flex-1">
                                                <p className="font-medium text-base flex items-center">
                                                    <a
                                                        href={
                                                            link.original_source
                                                        }
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-blue-500 underline"
                                                    >
                                                        {link.title}
                                                    </a>
                                                </p>
                                                {link.source && (
                                                    <p className="text-gray-500 text-sm mt-2">
                                                        Source: {link.source}
                                                    </p>
                                                )}
                                                {link.publish_date && (
                                                    <p className="text-gray-400 text-xs">
                                                        Published:{" "}
                                                        {new Date(
                                                            link.publish_date
                                                        ).toLocaleDateString()}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                        {link.description && (
                                            <div className="formatted-description mt-2">
                                                <div
                                                    dangerouslySetInnerHTML={{
                                                        __html: link.description
                                                    }}
                                                />
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default PanelDetailDisplay;
