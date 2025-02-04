import { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";
import { handleCreatePanel, handleUpdatePanel } from "./helpers/panel.js";
import { fetchNewsLinks } from "./helpers/fetch.js";
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
        panel.metadata?.hacker_news || []
    );
    const [inputText, setInputText] = useState(panel.inputText || "");
    const [yleNewsConfigs, setYleNewsConfigs] = useState(
        panel.metadata?.yle_news || []
    );
    const [newsLinks, setNewsLinks] = useState([]);
    const [error, setError] = useState(null);
    const [expandedDescriptionIndex, setExpandedDescriptionIndex] =
        useState(null);
    const [newsGuidance, setNewsGuidance] = useState(null);
    const [newsItems, setNewsItems] = useState(5);

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
                });
        } else {
            // Create new panel
            handleCreatePanel(panelData).then((response) => {
                console.log("handleCreatePanel response:", response); // Debugging log
                const { panelId, success } = response;
                if (success && panelId) {
                    if (setSelectedPanel) setSelectedPanel(panelId);
                    if (setPanelId) setPanelId(panelId);
                    if (handleRefreshPanelData) handleRefreshPanelData(panelId);
                    if (fetchPanels) fetchPanels();
                    if (setRedirectToPanel) setRedirectToPanel(true);
                } else {
                    alert("Error while creating panel.");
                }
            });
        }
    };

    const handleTestConfigs = async () => {
        const configs = {
            google_news: googleNewsConfigs,
            yle_news: yleNewsConfigs,
            techcrunch_news: techCrunchNewsConfigs,
            hacker_news: hackerNewsConfigs
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
                    <Button
                        variant="info"
                        onClick={handleTestConfigs}
                        className="py-2 mt-3 w-full bg-green-500 text-white"
                    >
                        Test Configs
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
                                        {group.data.map((link, index) => (
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
                                                            <Button
                                                                className="text-blue-500  hover:text-blue-300 text-sm mr-2 bg-transparent border-none align-top"
                                                                onClick={() =>
                                                                    setExpandedDescriptionIndex(
                                                                        expandedDescriptionIndex ===
                                                                            index
                                                                            ? null
                                                                            : index
                                                                    )
                                                                }
                                                            >
                                                                {expandedDescriptionIndex ===
                                                                index
                                                                    ? "▼"
                                                                    : "▶"}
                                                            </Button>
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
                                                            <p className="text-gray-500 text-sm ml-12 mt-2">
                                                                Source:{" "}
                                                                {link.source}
                                                            </p>
                                                        )}
                                                        {link.publish_date && (
                                                            <p className="text-gray-400 text-xs ml-12">
                                                                Published:{" "}
                                                                {new Date(
                                                                    link.publish_date
                                                                ).toLocaleDateString()}
                                                            </p>
                                                        )}
                                                    </div>
                                                </div>
                                                {link.description &&
                                                    expandedDescriptionIndex ===
                                                        index && (
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
