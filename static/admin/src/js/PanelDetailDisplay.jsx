import { useState } from "react";
import { Button, Accordion, Card } from "react-bootstrap";
import PropTypes from "prop-types";

// Helpers & Configs
import { fetchNewsLinks } from "./helpers/fetch.js";
import { conceptsMap } from "./news_config/YleNewsConfigForm";

// Shared Components
import SectionCard from "./components/SectionCard.jsx";
import ObjectDisplay from "./components/ObjectDisplay.jsx"; // Use for displaying config details

// Other Components
import { Link } from "react-router-dom"; // Import Link for navigation
import PanelDetailEdit from "./PanelDetailEdit";

const PanelDetailDisplay = ({
    panel,
    // allowInternalEdit = false, // New prop to control internal editing
    taskStatus,
    // Props needed only if allowInternalEdit is true
    setPanelId,
    setSelectedPanel,
    fetchPanels,
    handleRefreshPanelData,
    setRedirectToPanel
}) => {
    // State for testing news links
    const [newsLinks, setNewsLinks] = useState([]);
    const [error, setError] = useState(null);
    const [runningConfigTest, setRunningConfigTest] = useState(false);
    const [isEditing, setIsEditing] = useState(false); // State to toggle edit mode

    // Handler to test news configurations
    const handleTestConfigs = async () => {
        setRunningConfigTest(true);
        setError(null); // Clear previous errors
        const metadata = panel?.metadata || {};
        const configs = {
            news_guidance: metadata.news_guidance || "",
            news_items: parseInt(metadata.news_items || 5),
            segments: parseInt(metadata.segments || 5),
            google_news: metadata.google_news,
            yle_news: metadata.yle_news,
            techcrunch_news: metadata.techcrunch_news,
            hackernews: metadata.hackernews
        };

        try {
            const response = await fetchNewsLinks(configs);
            setNewsLinks(response || []); // Ensure it's an array
        } catch (err) {
            console.error("Error fetching news links:", err);
            setError(
                "Failed to fetch news links. Please check configurations or server status."
            );
            setNewsLinks([]);
        } finally {
            setRunningConfigTest(false);
        }
    };

    // Render loading/error state or if panel is missing
    if (!panel) {
        return (
            <div className="panel-detail-display border p-3 mb-4 rounded text-muted">
                No panel data available.
            </div>
        );
    }

    // Toggle edit mode
    if (isEditing) {
        console.log("Is editing", isEditing);
        return (
            <PanelDetailEdit
                panel={panel}
                onCancel={() => setIsEditing(false)} // Pass cancel handler
                // Pass through all the necessary props from parent
                setPanelId={setPanelId}
                taskStatus={taskStatus}
                setSelectedPanel={setSelectedPanel}
                fetchPanels={fetchPanels}
                handleRefreshPanelData={handleRefreshPanelData}
                setRedirectToPanel={setRedirectToPanel}
            />
        );
    }

    // Extract data for easier access
    const links = panel.links || [];
    const metadata = panel.metadata || {};
    const podcastName = metadata.podcast_name || "";
    const podcastTagline = metadata.podcast_tagline || "";
    const googleNewsConfigs = metadata.google_news || [];
    const yleNewsConfigs = metadata.yle_news || [];
    const hackerNewsConfigs = metadata.hackernews || [];
    const techCrunchNewsConfigs = metadata.techcrunch_news || [];
    const inputText = metadata.input_text || "";
    const hasNewsConfigs =
        googleNewsConfigs.length > 0 ||
        yleNewsConfigs.length > 0 ||
        techCrunchNewsConfigs.length > 0 ||
        hackerNewsConfigs.length > 0;

    // Helper to render simple key-value pairs within news config cards
    const renderConfigDetail = (label, value) => {
        if (value === undefined || value === null || value === "") return null;
        // Special handling for Yle topics/locations using conceptsMap
        if (
            (label === "Topics" || label === "Locations") &&
            Array.isArray(value) &&
            yleNewsConfigs.length > 0
        ) {
            const map =
                label === "Topics" ? conceptsMap.topics : conceptsMap.locations;
            value = value.map(
                (id) => map.find((item) => item.id === id)?.title || id
            );
        }
        return (
            <p className="mb-1">
                <strong className="font-semibold">{label}:</strong>{" "}
                {Array.isArray(value) ? value.join(", ") : String(value)}
            </p>
        );
    };

    return (
        // Removed outer Accordion, using simple div or Card wrapper if needed by parent
        <div className="panel-detail-display">
            {/* Panel Title */}
            <h4 className="mb-3">
                {panel.title || "Untitled Panel"}{" "}
                {metadata.display_tag ? `(${metadata.display_tag})` : ""}
            </h4>

            {/* Display simple metadata fields using SectionCard */}
            {metadata.languages?.length > 0 && (
                <SectionCard title="Additional Languages">
                    <p>{metadata.languages.join(", ")}</p>
                </SectionCard>
            )}
            {podcastName && (
                <SectionCard title="Podcast Name">
                    <p>{podcastName}</p>
                </SectionCard>
            )}
            {podcastTagline && (
                <SectionCard title="Podcast Tagline">
                    <p>{podcastTagline}</p>
                </SectionCard>
            )}
            {metadata.segments && (
                <SectionCard title="Transcript Segments">
                    <p>{metadata.segments}</p>
                </SectionCard>
            )}
            {metadata.news_items && (
                <SectionCard title="News Items per Segment">
                    <p>{metadata.news_items}</p>
                </SectionCard>
            )}
            {metadata.news_guidance && (
                <SectionCard title="News Guidance">
                    <p style={{ whiteSpace: "pre-wrap" }}>
                        {metadata.news_guidance}
                    </p>
                </SectionCard>
            )}

            {/* Display Links */}
            {links.length > 0 && (
                <SectionCard title="Links">
                    {links.map((link, index) => (
                        <p key={index} className="mb-1">
                            <a
                                href={link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary text-decoration-none"
                            >
                                {link}
                            </a>
                        </p>
                    ))}
                </SectionCard>
            )}

            {/* Display Metadata URLs */}
            {metadata.urls?.length > 0 && (
                <SectionCard title="Metadata URLs">
                    {metadata.urls.map((url, index) => (
                        <p key={index} className="mb-1">
                            <a
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary text-decoration-none"
                            >
                                ({index + 1}): {url}
                            </a>
                        </p>
                    ))}
                </SectionCard>
            )}

            {/* News Configurations */}
            {hasNewsConfigs && (
                <h5 className="mt-4 mb-3">News Source Configurations</h5>
            )}

            {googleNewsConfigs.length > 0 && (
                <SectionCard title="Google News">
                    {googleNewsConfigs.map((config, index) => (
                        <div key={index} className="mb-3 pb-2 border-bottom">
                            <p className="mb-1">
                                <strong className="font-semibold">
                                    Config {index + 1}:
                                </strong>
                            </p>
                            {renderConfigDetail("Type", config.feed_type)}
                            {renderConfigDetail("Language", config.lang)}
                            {renderConfigDetail("Country", config.country)}
                            {renderConfigDetail("Topics", config.topics)}
                            {renderConfigDetail("Query", config.query)}
                            {renderConfigDetail("Location", config.location)}
                            {renderConfigDetail("Since", config.since)}
                        </div>
                    ))}
                </SectionCard>
            )}

            {techCrunchNewsConfigs.length > 0 && (
                <SectionCard title="TechCrunch News">
                    {techCrunchNewsConfigs.map((config, index) => (
                        <div key={index} className="mb-3 pb-2 border-bottom">
                            <p className="mb-1">
                                <strong className="font-semibold">
                                    Config {index + 1}:
                                </strong>
                            </p>
                            {renderConfigDetail("Articles", config.articles)}
                        </div>
                    ))}
                </SectionCard>
            )}

            {yleNewsConfigs.length > 0 && (
                <SectionCard title="Yle News">
                    {yleNewsConfigs.map((config, index) => (
                        <div key={index} className="mb-3 pb-2 border-bottom">
                            <p className="mb-1">
                                <strong className="font-semibold">
                                    Config {index + 1}:
                                </strong>
                            </p>
                            {renderConfigDetail(
                                "Type",
                                config.feed_type || config.type
                            )}
                            {renderConfigDetail("Language", config.lang)}
                            {renderConfigDetail("Topics", config.topics)}
                            {renderConfigDetail("Locations", config.locations)}
                        </div>
                    ))}
                </SectionCard>
            )}

            {hackerNewsConfigs.length > 0 && (
                <SectionCard title="Hacker News">
                    {hackerNewsConfigs.map((config, index) => (
                        <div key={index} className="mb-3 pb-2 border-bottom">
                            <p className="mb-1">
                                <strong className="font-semibold">
                                    Config {index + 1}:
                                </strong>
                            </p>
                            {renderConfigDetail("Feed Type", config.feed_type)}
                            {renderConfigDetail("Query", config.query)}
                            {renderConfigDetail("Min Points", config.points)}
                            {renderConfigDetail(
                                "Min Comments",
                                config.comments
                            )}
                        </div>
                    ))}
                </SectionCard>
            )}

            {/* Static Text Content */}
            {inputText && (
                <SectionCard title="Static Text Content">
                    <Accordion>
                        <Accordion.Item eventKey="static-text">
                            <Accordion.Header>View Content</Accordion.Header>
                            <Accordion.Body>
                                <p style={{ whiteSpace: "pre-wrap" }}>
                                    {inputText}
                                </p>
                            </Accordion.Body>
                        </Accordion.Item>
                    </Accordion>
                </SectionCard>
            )}

            {/* Action Buttons */}
            <div className="mt-4 d-grid gap-2">
                {/* {allowInternalEdit ? ( */}
                <Button
                    onClick={() => setIsEditing(true)}
                    disabled={taskStatus !== "idle" && taskStatus}
                    className={`w-full py-2 mt-4 flex items-center justify-center rounded ${
                        taskStatus === "idle" || !taskStatus
                            ? "bg-green-500 border-green-800 text-white"
                            : "bg-gray-500 border-gray-800 text-gray-300"
                    }`}
                >
                    Edit Configuration
                </Button>
                {/* ) : (
                    <Button
                        as={Link}
                        to={`/panel/${panel.id}/edit`}
                        variant="outline-primary"
                    >
                        Go to Edit Page
                    </Button>
                )} */}
                <Button
                    variant="outline-info" // Use outline style
                    onClick={handleTestConfigs}
                    disabled={runningConfigTest}
                >
                    {runningConfigTest ? "Testing..." : "Test Panel Sources"}
                </Button>
            </div>

            {/* Test Results */}
            {error && <p className="text-danger mt-3">{error}</p>}
            {newsLinks.length > 0 && (
                <SectionCard
                    title="Fetched News Links (Test Result)"
                    className="mt-4"
                >
                    <div className="d-grid gap-3">
                        {" "}
                        {/* Use Bootstrap grid helpers */}
                        {newsLinks.map((group, groupIndex) => (
                            <div
                                key={groupIndex}
                                className="news-group border rounded p-3"
                            >
                                <h6>
                                    {group.title || `Group ${groupIndex + 1}`}
                                </h6>
                                {group.data?.web_sources?.map((link, index) => (
                                    <Card
                                        key={index}
                                        className="mb-3 shadow-sm"
                                    >
                                        <Card.Body>
                                            <div className="d-flex gap-3 align-items-start">
                                                {link.image && (
                                                    <img
                                                        src={link.image}
                                                        alt={
                                                            link.title ||
                                                            "News image"
                                                        }
                                                        style={{
                                                            width: "100px",
                                                            height: "100px",
                                                            objectFit: "cover",
                                                            borderRadius: "4px"
                                                        }}
                                                    />
                                                )}
                                                <div className="flex-grow-1">
                                                    <Card.Title
                                                        as="p"
                                                        className="mb-1"
                                                    >
                                                        <a
                                                            href={
                                                                link.original_source
                                                            }
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="text-primary text-decoration-none"
                                                        >
                                                            {link.title}
                                                        </a>
                                                    </Card.Title>
                                                    {link.source && (
                                                        <Card.Subtitle className="mb-1 text-muted small">
                                                            Source:{" "}
                                                            {link.source}
                                                        </Card.Subtitle>
                                                    )}
                                                    {link.publish_date && (
                                                        <Card.Text className="text-muted small">
                                                            Published:{" "}
                                                            {new Date(
                                                                link.publish_date
                                                            ).toLocaleDateString()}
                                                        </Card.Text>
                                                    )}
                                                </div>
                                            </div>
                                            {link.description && (
                                                <div
                                                    className="mt-2 small"
                                                    dangerouslySetInnerHTML={{
                                                        __html: link.description
                                                    }}
                                                />
                                            )}
                                        </Card.Body>
                                    </Card>
                                ))}
                                {(!group.data ||
                                    !group.data.web_sources ||
                                    group.data.web_sources.length === 0) && (
                                    <p className="text-muted small">
                                        No web sources found for this group.
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                </SectionCard>
            )}
        </div>
    );
};

// Add PropTypes for validation
PanelDetailDisplay.propTypes = {
    panel: PropTypes.object.isRequired,
    // allowInternalEdit: PropTypes.bool, // Prop to control edit button behavior
    taskStatus: PropTypes.string,
    // Props needed for PanelDetailEdit (only required if allowInternalEdit is true)
    setPanelId: PropTypes.func,
    setSelectedPanel: PropTypes.func,
    fetchPanels: PropTypes.func,
    handleRefreshPanelData: PropTypes.func,
    setRedirectToPanel: PropTypes.func
};

export default PanelDetailDisplay;
