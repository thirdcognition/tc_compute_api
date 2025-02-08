import { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";
import { handleCreatePanel, handleUpdatePanel } from "./helpers/panel.js";
import LinkForm from "./news_config/LinkForm";
import GoogleNewsConfigForm from "./news_config/GoogleNewsConfigForm";
import YleNewsConfigForm from "./news_config/YleNewsConfigForm";
import TechCrunchNewsConfigForm from "./news_config/TechCrunchNewsConfigForm";
import HackerNewsConfigForm from "./news_config/HackerNewsConfigForm";
import InputTextForm from "./news_config/InputTextForm";
import ArticleCountComponent from "./components/ArticleCountComponent";

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

    const handlePanelSubmit = async (e) => {
        e.preventDefault();
        const panelData = {
            title,
            inputText,
            links,
            googleNewsConfigs,
            yleNewsConfigs,
            techCrunchNewsConfigs,
            hackerNewsConfigs,
            newsGuidance,
            newsItems
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

    return (
        <>
            <div className="panel-container border p-3 mb-4 rounded">
                <h3 className="font-bold mb-3">
                    {panel.id ? "Edit Panel" : "Create Panel"}
                </h3>
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
                    <InputTextForm
                        label="Guidance for LLM when organizing and filtering news items:"
                        initialText={newsGuidance}
                        onTextChange={setNewsGuidance}
                    />
                    <ArticleCountComponent
                        value={newsItems}
                        onChange={(value) => setNewsItems(value)}
                    />
                    <LinkForm initialLinks={links} onLinksChange={setLinks} />
                    <YleNewsConfigForm
                        initialConfigs={yleNewsConfigs}
                        onConfigsChange={setYleNewsConfigs}
                    />
                    <GoogleNewsConfigForm
                        initialConfigs={googleNewsConfigs}
                        onConfigsChange={setGoogleNewsConfigs}
                    />
                    <TechCrunchNewsConfigForm
                        initialConfigs={techCrunchNewsConfigs}
                        onConfigsChange={setTechCrunchNewsConfigs}
                    />
                    <HackerNewsConfigForm
                        initialConfigs={hackerNewsConfigs}
                        onConfigsChange={setHackerNewsConfigs}
                    />
                    <InputTextForm
                        initialText={inputText}
                        onTextChange={setInputText}
                        label="Static text content to include in show content:"
                    />
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
