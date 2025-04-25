import { useState } from "react";
import { Form, Button, Accordion } from "react-bootstrap"; // Keep Accordion for now, might remove if DetailAccordion replaces all uses
import PropTypes from "prop-types";

// Helpers & Options
import { handleCreatePanel, handleUpdatePanel } from "./helpers/panel.js";
import { outputLanguageOptions } from "./options.js";

// News Config Forms (Keep these specific forms)
import LinkForm from "./news_config/LinkForm";
import GoogleNewsConfigForm from "./news_config/GoogleNewsConfigForm";
import YleNewsConfigForm from "./news_config/YleNewsConfigForm";
import TechCrunchNewsConfigForm from "./news_config/TechCrunchNewsConfigForm";
import HackerNewsConfigForm from "./news_config/HackerNewsConfigForm";
import InputTextForm from "./news_config/InputTextForm"; // Used for simple text inputs

// Shared & Existing Components
import ArticleCountComponent from "./components/ArticleCountComponent";
import SectionCard from "./components/SectionCard.jsx"; // Import shared component
// DetailAccordion might be usable for the news configs, let's evaluate

function PanelDetailEdit({
    panel = {},
    setPanelId,
    taskStatus,
    setSelectedPanel,
    fetchPanels,
    handleRefreshPanelData,
    setRedirectToPanel,
    onCancel
}) {
    // --- State ---
    const [title, setTitle] = useState(panel.title || "");
    const [displayTag, setDisplayTag] = useState(
        panel.metadata?.display_tag || ""
    );
    const [links, setLinks] = useState(panel.links || []);
    const [googleNewsConfigs, setGoogleNewsConfigs] = useState(
        panel.metadata?.google_news || []
    );
    const [techCrunchNewsConfigs, setTechCrunchNewsConfigs] = useState(
        panel.metadata?.techcrunch_news || []
    );
    const [hackerNewsConfigs, setHackerNewsConfigs] = useState(
        panel.metadata?.hackernews || []
    );
    const [inputText, setInputText] = useState(
        panel.metadata?.input_text || ""
    );
    const [yleNewsConfigs, setYleNewsConfigs] = useState(
        panel.metadata?.yle_news || []
    );
    const [newsGuidance, setNewsGuidance] = useState(
        panel.metadata?.news_guidance || ""
    );
    const [newsItems, setNewsItems] = useState(
        parseInt(panel.metadata?.news_items || 5)
    );
    const [segments, setSegments] = useState(
        parseInt(panel.metadata?.segments || 5)
    );
    const [languages, setLanguages] = useState(panel.metadata?.languages || []);
    const [isPublic, setIsPublic] = useState(panel.is_public || false);
    const [podcastName, setPodcastName] = useState(
        panel.metadata?.podcast_name || ""
    ); // Initialize from panel metadata
    const [podcastTagline, setPodcastTagline] = useState(
        panel.metadata?.podcast_tagline || ""
    ); // Initialize from panel metadata

    // --- Handlers ---
    const handlePanelSubmit = async (e) => {
        e.preventDefault();
        const panelData = {
            title,
            displayTag,
            inputText,
            googleNewsConfigs,
            yleNewsConfigs,
            techCrunchNewsConfigs,
            hackerNewsConfigs,
            newsGuidance,
            newsItems,
            segments,
            languages,
            podcastName,
            podcastTagline,
            links, // Keep links at top level if schema requires
            is_public: isPublic
        };

        // Remove empty arrays from metadata to avoid storing empty configs
        Object.keys(panelData).forEach((key) => {
            if (Array.isArray(panelData[key]) && panelData[key].length === 0) {
                delete panelData[key];
            }
        });

        if (panel.id) {
            // Update existing panel
            handleUpdatePanel(panel.id, panelData) // Pass combined data
                .then((response) => {
                    // console.log("handleUpdatePanel response:", response);
                    const { success } = response;
                    if (success) {
                        if (handleRefreshPanelData)
                            handleRefreshPanelData(panel.id);
                        if (fetchPanels) fetchPanels();
                        if (onCancel) onCancel(); // Call onCancel on successful update
                    } else {
                        // console.log("Update panel success:", success);
                        alert("Error while updating panel.");
                    }
                })
                .catch((error) => {
                    console.error(
                        "Error in handlePanelSubmit (Update):",
                        error
                    );
                    alert("Error while updating panel.");
                })
                .finally(() => {
                    window.location.reload();
                });
        } else {
            // Create new panel
            handleCreatePanel(panelData)
                .then((response) => {
                    // console.log("handleCreatePanel response:", response);
                    const { panelId: newPanelId, success } = response; // Rename to avoid conflict
                    if (success && newPanelId) {
                        if (setSelectedPanel) setSelectedPanel(newPanelId);
                        if (setPanelId) setPanelId(newPanelId); // Set the new panel ID in parent
                        if (handleRefreshPanelData)
                            handleRefreshPanelData(newPanelId);
                        if (fetchPanels) fetchPanels();
                        if (setRedirectToPanel) setRedirectToPanel(true); // Redirect if needed
                    } else {
                        alert("Error while creating panel.");
                    }
                })
                .catch((error) => {
                    console.error(
                        "Error in handleCreatePanel (Create):",
                        error
                    );
                    alert("Error while creating panel.");
                })
                .finally(() => {
                    window.location.reload();
                });
        }
    };

    // Determine default open accordion item for news configs
    const defaultNewsConfigActiveKey = () => {
        if (links?.length > 0) return "0";
        if (yleNewsConfigs?.length > 0) return "1";
        if (googleNewsConfigs?.length > 0) return "2";
        if (techCrunchNewsConfigs?.length > 0) return "3";
        if (hackerNewsConfigs?.length > 0) return "4";
        if (inputText) return "5"; // Check inputText as well
        return "0"; // Default to Links if nothing else has content
    };

    // --- Main Render ---
    return (
        <div className="panel-container border p-3 mb-4 rounded">
            <h3 className="font-bold mb-3">
                {panel.id ? "Edit Panel" : "Create Panel"}
            </h3>
            <Form onSubmit={handlePanelSubmit}>
                {/* Use SectionCard for simple fields */}
                <SectionCard title="Panel Name">
                    <InputTextForm
                        initialText={title}
                        onTextChange={setTitle}
                        textarea={false}
                    />
                </SectionCard>

                <SectionCard title="Podcast Name">
                    <InputTextForm
                        initialText={podcastName}
                        onTextChange={setPodcastName}
                        textarea={false}
                    />
                    <Form.Text className="text-muted">
                        If left empty, a predefined default will be used.
                    </Form.Text>
                </SectionCard>

                <SectionCard title="Podcast Tagline">
                    <InputTextForm
                        initialText={podcastTagline}
                        onTextChange={setPodcastTagline}
                        textarea={false}
                    />
                    <Form.Text className="text-muted">
                        If left empty, a predefined default will be used.
                    </Form.Text>
                </SectionCard>

                <SectionCard title="Display tag">
                    <InputTextForm
                        initialText={displayTag}
                        onTextChange={setDisplayTag}
                        textarea={false}
                    />
                    <Form.Text className="text-muted">
                        Shown at user selection.
                    </Form.Text>
                </SectionCard>

                <SectionCard title="Public Access">
                    <Form.Check
                        type="switch"
                        id="public-switch" // Add id for label association
                        label="Public Panel"
                        checked={isPublic}
                        onChange={(e) => setIsPublic(e.target.checked)}
                        className="font-semibold"
                    />
                    <Form.Text className="text-muted">
                        Toggle to make this panel public or private{" "}
                        <i>(hidden)</i>.
                    </Form.Text>
                </SectionCard>

                <SectionCard title="Languages">
                    <Form.Group controlId="languages">
                        <Form.Label className="font-semibold text-left">
                            Translations:
                            <br />
                            <small className="text-muted font-normal">
                                Note: Test all languages with voice models.{" "}
                                <br /> If transcript output_language matches
                                selected language, translation is skipped.
                                English is enabled by default.
                            </small>
                        </Form.Label>
                        <Form.Control
                            as="select"
                            multiple
                            value={languages}
                            onChange={(e) =>
                                setLanguages(
                                    [...e.target.selectedOptions].map(
                                        (o) => o.value
                                    )
                                )
                            }
                            className="w-full"
                            style={{ height: "150px" }} // Set height for multi-select
                        >
                            {Object.entries(outputLanguageOptions).map(
                                ([langId, language]) => (
                                    <option value={langId} key={langId}>
                                        {language} ({langId})
                                    </option>
                                )
                            )}
                        </Form.Control>
                    </Form.Group>
                </SectionCard>

                {/* Keep ArticleCountComponent as is */}
                <ArticleCountComponent
                    label="Requested total segments"
                    value={segments}
                    onChange={(value) => setSegments(parseInt(value))} // Ensure value is number
                />
                <ArticleCountComponent
                    label="Maximum news items per segment"
                    value={newsItems}
                    onChange={(value) => setNewsItems(parseInt(value))} // Ensure value is number
                />

                {/* News Guidance */}
                <SectionCard title="News Guidance">
                    <InputTextForm
                        initialText={newsGuidance}
                        onTextChange={setNewsGuidance}
                        placeholder="Guidance for LLM when organizing and filtering news items..."
                    />
                </SectionCard>

                {/* News Configs Accordion */}
                <h4 className="mt-4 pt-3 border-top">News Sources</h4>
                <Accordion
                    defaultActiveKey={defaultNewsConfigActiveKey()}
                    className="mb-4"
                >
                    {/* Event keys match the order in defaultNewsConfigActiveKey */}
                    <Accordion.Item eventKey="0">
                        <Accordion.Header>
                            Links (defined: {links.length})
                        </Accordion.Header>
                        <Accordion.Body>
                            <LinkForm
                                initialLinks={links}
                                onLinksChange={setLinks}
                            />
                        </Accordion.Body>
                    </Accordion.Item>
                    <Accordion.Item eventKey="1">
                        <Accordion.Header>
                            Yle News (defined: {yleNewsConfigs.length})
                        </Accordion.Header>
                        <Accordion.Body>
                            <YleNewsConfigForm
                                initialConfigs={yleNewsConfigs}
                                onConfigsChange={setYleNewsConfigs}
                            />
                        </Accordion.Body>
                    </Accordion.Item>
                    <Accordion.Item eventKey="2">
                        <Accordion.Header>
                            Google News (defined: {googleNewsConfigs.length})
                        </Accordion.Header>
                        <Accordion.Body>
                            <GoogleNewsConfigForm
                                initialConfigs={googleNewsConfigs}
                                onConfigsChange={setGoogleNewsConfigs}
                            />
                        </Accordion.Body>
                    </Accordion.Item>
                    <Accordion.Item eventKey="3">
                        <Accordion.Header>
                            TechCrunch News (defined:{" "}
                            {techCrunchNewsConfigs.length})
                        </Accordion.Header>
                        <Accordion.Body>
                            <TechCrunchNewsConfigForm
                                initialConfigs={techCrunchNewsConfigs}
                                onConfigsChange={setTechCrunchNewsConfigs}
                            />
                        </Accordion.Body>
                    </Accordion.Item>
                    <Accordion.Item eventKey="4">
                        <Accordion.Header>
                            Hacker News (defined: {hackerNewsConfigs.length})
                        </Accordion.Header>
                        <Accordion.Body>
                            <HackerNewsConfigForm
                                initialConfigs={hackerNewsConfigs}
                                onConfigsChange={setHackerNewsConfigs}
                            />
                        </Accordion.Body>
                    </Accordion.Item>
                    <Accordion.Item eventKey="5">
                        <Accordion.Header>Static Text Content</Accordion.Header>
                        <Accordion.Body>
                            <InputTextForm
                                initialText={inputText}
                                onTextChange={setInputText}
                                rows={15}
                                placeholder="Static text content to include in show content..."
                            />
                        </Accordion.Body>
                    </Accordion.Item>
                </Accordion>

                {/* Action Buttons */}
                <div className="d-flex justify-content-between mt-4">
                    <Button
                        variant="secondary"
                        onClick={onCancel}
                        className="py-2"
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="primary"
                        type="submit"
                        className="py-2"
                        disabled={
                            // Disable create button if task is running
                            !panel.id &&
                            taskStatus &&
                            taskStatus !== "idle" &&
                            taskStatus !== "failure" &&
                            taskStatus !== "success"
                        }
                    >
                        {panel.id ? "Update Panel" : "Create Panel"}
                    </Button>
                </div>
            </Form>
        </div>
    );
}

PanelDetailEdit.propTypes = {
    panel: PropTypes.object,
    setPanelId: PropTypes.func,
    taskStatus: PropTypes.string,
    setSelectedPanel: PropTypes.func,
    fetchPanels: PropTypes.func,
    handleRefreshPanelData: PropTypes.func,
    setRedirectToPanel: PropTypes.func,
    onCancel: PropTypes.func.isRequired
};

export default PanelDetailEdit;
