import { useState, useEffect } from "react";
import { Form, Button, Card, Accordion } from "react-bootstrap";
import { handleCreatePanel, handleUpdatePanel } from "./helpers/panel.js";
import LinkForm from "./news_config/LinkForm";
import GoogleNewsConfigForm from "./news_config/GoogleNewsConfigForm";
import YleNewsConfigForm from "./news_config/YleNewsConfigForm";
import TechCrunchNewsConfigForm from "./news_config/TechCrunchNewsConfigForm";
import HackerNewsConfigForm from "./news_config/HackerNewsConfigForm";
import InputTextForm from "./news_config/InputTextForm";
import ArticleCountComponent from "./components/ArticleCountComponent";
import { outputLanguageOptions } from "./options.js";

import PropTypes from "prop-types";

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
    const [inputText, setInputText] = useState(panel.inputText || "");
    const [yleNewsConfigs, setYleNewsConfigs] = useState(
        panel.metadata?.yle_news || []
    );
    const [expandedDescriptionIndex, setExpandedDescriptionIndex] =
        useState(null);
    const [newsGuidance, setNewsGuidance] = useState(
        panel.metadata?.news_guidance || ""
    );
    const [newsItems, setNewsItems] = useState(
        parseInt(panel.metadata?.news_items || 5)
    );
    const [languages, setLanguages] = useState(
        panel.metadata?.languages || ["English"]
    );
    const [isPublic, setIsPublic] = useState(panel.is_public || false);
    const handlePanelSubmit = async (e) => {
        e.preventDefault();
        const panelData = {
            title,
            displayTag,
            inputText,
            links,
            googleNewsConfigs,
            yleNewsConfigs,
            techCrunchNewsConfigs,
            hackerNewsConfigs,
            newsGuidance,
            newsItems,
            languages,
            is_public: isPublic
        };

        if (panel.id) {
            // Update existing panel
            handleUpdatePanel(panel.id, {
                ...panel,
                ...panelData
            })
                .then((response) => {
                    console.log("handleUpdatePanel response:", response); // Debugging log
                    const { success } = response;
                    if (success) {
                        if (handleRefreshPanelData)
                            handleRefreshPanelData(panel.id);
                        if (fetchPanels) fetchPanels();
                        if (onCancel) onCancel();
                    } else {
                        console.log("Update panel success:", success); // Debugging log
                        alert("Error while updating panel.");
                    }
                })
                .catch((error) => {
                    console.error("Error in handlePanelSubmit:", error); // Debugging log
                    alert("Error while updating panel.");
                })
                .finally(() => {
                    window.location.reload();
                });
        } else {
            // Create new panel
            handleCreatePanel(panelData)
                .then((response) => {
                    console.log("handleCreatePanel response:", response); // Debugging log
                    const { panelId, success } = response;
                    if (success && panelId) {
                        if (setSelectedPanel) setSelectedPanel(panelId);
                        if (setPanelId) setPanelId(panelId);
                        if (handleRefreshPanelData)
                            handleRefreshPanelData(panelId);
                        if (fetchPanels) fetchPanels();
                        if (setRedirectToPanel) setRedirectToPanel(true);
                    } else {
                        alert("Error while creating panel.");
                    }
                })
                .catch((error) => {
                    console.error("Error in handleCreatePanel:", error); // Debugging log
                    alert("Error while creating panel.");
                })
                .finally(() => {
                    window.location.reload();
                });
        }
    };

    const defaultNewsConfigActiveKey = () => {
        if (links && links.length > 0) return "0";
        if (yleNewsConfigs && yleNewsConfigs.length > 0) return "1";
        if (googleNewsConfigs && googleNewsConfigs.length > 0) return "2";
        if (techCrunchNewsConfigs && techCrunchNewsConfigs.length > 0)
            return "3";
        if (hackerNewsConfigs && hackerNewsConfigs.length > 0) return "4";
        return null; // Default to Links if no configs are defined
    };

    return (
        <>
            <div className="panel-container border p-3 mb-4 rounded">
                <h3 className="font-bold mb-3">
                    {panel.id ? "Edit Panel" : "Create Panel"}
                </h3>
                <Form onSubmit={handlePanelSubmit}>
                    <Card className="mb-4">
                        <Card.Header>Panel Name</Card.Header>
                        <Card.Body>
                            <Form.Group controlId="title">
                                <InputTextForm
                                    initialText={title}
                                    onTextChange={setTitle}
                                    textarea={false}
                                />
                            </Form.Group>
                        </Card.Body>
                    </Card>
                    <Card className="mb-4">
                        <Card.Header>
                            Display tag <small>(shown at user selection)</small>
                        </Card.Header>
                        <Card.Body>
                            <Form.Group controlId="displaytag">
                                <InputTextForm
                                    initialText={displayTag}
                                    onTextChange={setDisplayTag}
                                    textarea={false}
                                />
                            </Form.Group>
                        </Card.Body>
                    </Card>
                    <Card className="mb-4">
                        <Card.Header>Public Access</Card.Header>
                        <Card.Body>
                            <Form.Group controlId="public">
                                <Form.Check
                                    type="switch"
                                    label="Public Panel"
                                    checked={isPublic}
                                    onChange={(e) =>
                                        setIsPublic(e.target.checked)
                                    }
                                    className="font-semibold"
                                />
                                <Form.Text className="text-muted">
                                    Toggle to make this panel public or private
                                    <i>(hidden)</i>.
                                </Form.Text>
                            </Form.Group>
                        </Card.Body>
                    </Card>

                    <Card className="mb-4">
                        <Card.Header>Languages</Card.Header>
                        <Card.Body>
                            <Form.Group controlId="languages">
                                <Form.Label className="font-semibold text-left">
                                    Extra languages:
                                    <br />
                                    <small className="text-muted font-normal">
                                        Note: Test all languages with voice
                                        models
                                    </small>
                                </Form.Label>
                                <Form.Control
                                    as="select"
                                    multiple
                                    value={languages}
                                    onChange={(e) =>
                                        setLanguages(
                                            [...e.target.selectedOptions].map(
                                                (option) => option.value
                                            )
                                        )
                                    }
                                    className="w-full"
                                >
                                    {outputLanguageOptions
                                        .filter(
                                            (item) =>
                                                item.toLowerCase() !== "english"
                                        )
                                        .map((language) => (
                                            <option
                                                value={language}
                                                key={language}
                                            >
                                                {language}
                                            </option>
                                        ))}
                                </Form.Control>
                                <Form.Text className="text-muted ml-2">
                                    English is enabled by default
                                </Form.Text>
                            </Form.Group>
                        </Card.Body>
                    </Card>
                    <ArticleCountComponent
                        value={newsItems}
                        onChange={(value) => setNewsItems(value)}
                    />

                    <Form.Group
                        controlId="news_configs"
                        className="mt-4 border-t-2"
                    >
                        <Card className="my-4">
                            <Card.Header>
                                Guidance for LLM when organizing and filtering
                                news items:
                            </Card.Header>
                            <Card.Body>
                                <InputTextForm
                                    initialText={newsGuidance}
                                    onTextChange={setNewsGuidance}
                                />
                            </Card.Body>
                        </Card>

                        <Accordion
                            defaultActiveKey={defaultNewsConfigActiveKey()}
                        >
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
                                    Yle News Configs (defined:{" "}
                                    {yleNewsConfigs.length})
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
                                    Google News Configs (defined:{" "}
                                    {googleNewsConfigs.length})
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
                                    TechCrunch News Config
                                </Accordion.Header>
                                <Accordion.Body>
                                    <TechCrunchNewsConfigForm
                                        initialConfigs={techCrunchNewsConfigs}
                                        onConfigsChange={
                                            setTechCrunchNewsConfigs
                                        }
                                    />
                                </Accordion.Body>
                            </Accordion.Item>
                            <Accordion.Item eventKey="4">
                                <Accordion.Header>
                                    Hacker News Configs (defined:{" "}
                                    {hackerNewsConfigs.length})
                                </Accordion.Header>
                                <Accordion.Body>
                                    <HackerNewsConfigForm
                                        initialConfigs={hackerNewsConfigs}
                                        onConfigsChange={setHackerNewsConfigs}
                                    />
                                </Accordion.Body>
                            </Accordion.Item>
                            <Accordion.Item eventKey="5">
                                <Accordion.Header>
                                    Static text content to include in show
                                    content
                                </Accordion.Header>
                                <Accordion.Body>
                                    <InputTextForm
                                        initialText={inputText}
                                        onTextChange={setInputText}
                                    />
                                </Accordion.Body>
                            </Accordion.Item>
                        </Accordion>
                    </Form.Group>

                    <div className="flex justify-between mt-4">
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
                                !panel.id &&
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
        </>
    );
}

PanelDetailEdit.propTypes = {
    onCancel: PropTypes.func.isRequired
};

export default PanelDetailEdit;
