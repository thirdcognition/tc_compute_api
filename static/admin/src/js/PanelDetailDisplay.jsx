import { useState } from "react";
import { fetchNewsLinks } from "./helpers/fetch.js";
import { Button, Accordion, Card } from "react-bootstrap";
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
            segments: parseInt(panel?.metadata?.segments || 5),
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
        <>
            <Accordion>
                <Accordion.Item eventKey="0">
                    <Accordion.Header>
                        {panel.title && panel.title}{" "}
                        {panel.metadata?.display_tag
                            ? "(" + panel.metadata.display_tag + ")"
                            : ""}
                    </Accordion.Header>
                    <Accordion.Body>
                        {panel.metadata?.languages && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>
                                        Additional Languages
                                    </Card.Title>
                                    <p>{panel.metadata.languages.join(", ")}</p>
                                </Card.Body>
                            </Card>
                        )}

                        {inputText && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Input Text</Card.Title>
                                    <p className="mb-2">{inputText}</p>
                                </Card.Body>
                            </Card>
                        )}

                        {links.length > 0 && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Links</Card.Title>
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
                                </Card.Body>
                            </Card>
                        )}

                        {metadata.segments && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Transcript segments</Card.Title>
                                    <p>{metadata.segments}</p>
                                </Card.Body>
                            </Card>
                        )}

                        {metadata.news_items && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>News Items</Card.Title>
                                    <p>{metadata.news_items}</p>
                                </Card.Body>
                            </Card>
                        )}

                        {metadata.news_guidance && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>News Guidance</Card.Title>
                                    <p className="pl-5 mb-2">
                                        {metadata.news_guidance}
                                    </p>
                                </Card.Body>
                            </Card>
                        )}

                        {metadata.urls &&
                            Array.isArray(metadata.urls) &&
                            metadata.urls.length > 0 && (
                                <Card className="mb-4">
                                    <Card.Body>
                                        <Card.Title>Metadata URLs</Card.Title>
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
                                    </Card.Body>
                                </Card>
                            )}

                        {googleNewsConfigs.length > 0 && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>
                                        Google News Configurations
                                    </Card.Title>
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
                                                    {Array.isArray(
                                                        config.topics
                                                    )
                                                        ? config.topics.join(
                                                              ", "
                                                          )
                                                        : config.topics}
                                                </p>
                                            )}
                                            {config.query && (
                                                <p>Query: {config.query}</p>
                                            )}
                                            {config.location && (
                                                <p>
                                                    Location:{" "}
                                                    {Array.isArray(
                                                        config.location
                                                    )
                                                        ? config.location.join(
                                                              ", "
                                                          )
                                                        : config.location}
                                                </p>
                                            )}
                                            {config.since && (
                                                <p>Since: {config.since}</p>
                                            )}
                                        </div>
                                    ))}
                                </Card.Body>
                            </Card>
                        )}

                        {techCrunchNewsConfigs.length > 0 && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>
                                        TechCrunch News Configurations
                                    </Card.Title>
                                    {techCrunchNewsConfigs.map(
                                        (config, index) => (
                                            <div
                                                key={index}
                                                className="ml-4 mb-2"
                                            >
                                                <p className="mt-2">
                                                    <strong className="font-semibold">
                                                        Config {index + 1}:
                                                    </strong>
                                                </p>
                                                {config.articles && (
                                                    <p>
                                                        Articles:{" "}
                                                        {config.articles}
                                                    </p>
                                                )}
                                            </div>
                                        )
                                    )}
                                </Card.Body>
                            </Card>
                        )}

                        {yleNewsConfigs.length > 0 && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>
                                        Yle News Configurations
                                    </Card.Title>
                                    {yleNewsConfigs.map((config, index) => (
                                        <div key={index} className="ml-4 mb-2">
                                            <p className="mt-2">
                                                <strong className="font-semibold">
                                                    Config {index + 1}:
                                                </strong>
                                            </p>
                                            {(config.feed_type ||
                                                config.type) && (
                                                <p>
                                                    Type:{" "}
                                                    {config.feed_type ||
                                                        config.type}
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
                                                                        topic.id ===
                                                                        id
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
                                                                    (
                                                                        location
                                                                    ) =>
                                                                        location.id ===
                                                                        id
                                                                )?.title || id
                                                        )
                                                        .join(", ")}
                                                </p>
                                            )}
                                        </div>
                                    ))}
                                </Card.Body>
                            </Card>
                        )}

                        {hackerNewsConfigs.length > 0 && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>
                                        Hacker News Configurations
                                    </Card.Title>
                                    {hackerNewsConfigs.map((config, index) => (
                                        <div key={index} className="ml-4 mb-2">
                                            <p className="mt-2">
                                                <strong className="font-semibold">
                                                    Config {index + 1}:
                                                </strong>
                                            </p>
                                            {config.feed_type && (
                                                <p>
                                                    Feed Type:{" "}
                                                    {config.feed_type}
                                                </p>
                                            )}
                                            {config.query && (
                                                <p>Query: {config.query}</p>
                                            )}
                                            {config.points !== undefined && (
                                                <p>
                                                    Minimum Points:{" "}
                                                    {config.points}
                                                </p>
                                            )}
                                            {config.comments !== undefined && (
                                                <p>
                                                    Minimum Comments:{" "}
                                                    {config.comments}
                                                </p>
                                            )}
                                        </div>
                                    ))}
                                </Card.Body>
                            </Card>
                        )}
                        <Button
                            variant="info"
                            onClick={handleTestConfigs}
                            className="py-2 mt-3 w-full bg-green-500 border-green-800 text-white"
                            disabled={runningConfigTest} // Disable the button while testing
                        >
                            {runningConfigTest
                                ? "Processing..."
                                : "Test Panel Sources"}{" "}
                        </Button>
                        {error && <p className="text-danger mt-2">{error}</p>}
                        {newsLinks.length > 0 && (
                            <div className="mt-4">
                                <h5>Fetched News Links:</h5>
                                <div className="grid grid-cols-1 gap-4">
                                    {newsLinks.map((group, groupIndex) => (
                                        <div
                                            key={groupIndex}
                                            className="news-group"
                                        >
                                            <h6>
                                                {group.title ||
                                                    "Group " + groupIndex}
                                            </h6>
                                            {group.data.web_sources.map(
                                                (link, index) => (
                                                    <div
                                                        key={index}
                                                        className="border p-4 rounded shadow"
                                                    >
                                                        <div className="flex gap-4 items-start">
                                                            {link.image && (
                                                                <img
                                                                    src={
                                                                        link.image
                                                                    }
                                                                    alt={
                                                                        link.title
                                                                    }
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
                                                                        {
                                                                            link.title
                                                                        }
                                                                    </a>
                                                                </p>
                                                                {link.source && (
                                                                    <p className="text-gray-500 text-sm mt-2">
                                                                        Source:{" "}
                                                                        {
                                                                            link.source
                                                                        }
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
                                                )
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </Accordion.Body>
                </Accordion.Item>
            </Accordion>
            <Button
                onClick={() => setIsEditing(true)}
                disabled={taskStatus !== "idle"}
                className={`w-full py-2 mb-4 mt-4 flex items-center justify-center rounded ${
                    taskStatus === "idle"
                        ? "bg-green-500 border-green-800 text-white"
                        : "bg-gray-500 border-gray-800 text-gray-300"
                }`}
            >
                Edit Configuration
            </Button>
        </>
    );
};

export default PanelDetailDisplay;
