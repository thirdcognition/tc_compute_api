import { useState } from "react";
import { Form, Button } from "react-bootstrap";
import { handleCreatePanel } from "./helpers/panel.js";
import LinkForm from "./news_config/LinkForm";
import GoogleNewsConfigForm from "./news_config/GoogleNewsConfigForm";
import YleNewsConfigForm from "./news_config/YleNewsConfigForm";
import TechCrunchNewsConfigForm from "./news_config/TechCrunchNewsConfigForm";
import HackerNewsConfigForm from "./news_config/HackerNewsConfigForm";
import InputTextForm from "./news_config/InputTextForm";

function PanelDetailEdit({
    setPanelId,
    taskStatus,
    setSelectedPanel,
    fetchPanels,
    handleRefreshPanelData,
    setRedirectToPanel
}) {
    const [title, setTitle] = useState("");
    const [links, setLinks] = useState([]);
    const [googleNewsConfigs, setGoogleNewsConfigs] = useState([]);
    const [techCrunchNewsConfigs, setTechCrunchNewsConfigs] = useState([]);
    const [hackerNewsConfigs, setHackerNewsConfigs] = useState([]);
    const [inputText, setInputText] = useState("");
    const [yleNewsConfigs, setYleNewsConfigs] = useState([]);

    const handlePanelSubmit = async (e) => {
        e.preventDefault();
        handleCreatePanel({
            title,
            inputText,
            links,
            googleNewsConfigs,
            yleNewsConfigs,
            techCrunchNewsConfigs,
            hackerNewsConfigs
        }).then(({ panelId, success }) => {
            if (success && panelId) {
                setSelectedPanel(panelId);
                setPanelId(panelId);
                handleRefreshPanelData(panelId);
                fetchPanels();
                setRedirectToPanel(true);
            } else {
                alert("Error while creating panel.");
            }
        });
    };

    return (
        <>
            <div className="panel-container border p-3 mb-4 rounded">
                <h3 className="font-bold mb-3">Create Panel</h3>
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
                    />
                    <Button
                        variant="primary"
                        type="submit"
                        className="w-full py-2"
                        disabled={
                            taskStatus === "idle"
                                ? false
                                : taskStatus !== "failure" &&
                                  taskStatus !== "success"
                        }
                    >
                        Create Panel
                    </Button>
                </Form>
            </div>
        </>
    );
}

export default PanelDetailEdit;
