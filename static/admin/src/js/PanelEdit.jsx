import { Spinner, Button, Accordion } from "react-bootstrap";
import { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import PanelDetailEdit from "./PanelDetailEdit.jsx";
import PanelDetailDisplay from "./PanelDetailDisplay.jsx";
import TranscriptDetailEdit from "./TranscriptDetailEdit.jsx";
import TranscriptDetailDisplay from "./TranscriptDetailDisplay.jsx";
import AudioDetailEdit from "./AudioDetailEdit.jsx";
import { urlFormatter } from "./helpers/url.js";
import { pollTaskStatus } from "./helpers/pollState.js";
import { fetchPanelDetails } from "./helpers/fetch.js";
import { showConfirmationDialog, handleDeleteItem } from "./helpers/panel.js";
import { FaTimes, FaClock, FaRegStar, FaSyncAlt } from "react-icons/fa";

import { getStatusBarStyle, getStatusSymbol } from "./helpers/ui.js";

function PanelEdit({ fetchPanels, setSelectedPanel, initialPanelId }) {
    const [taskStatus, setTaskStatus] = useState("idle");
    const [isPolling, setIsPolling] = useState(false);
    const [existingAudio, setExistingAudio] = useState(null);
    const [panelId, setPanelId] = useState(initialPanelId || null);
    const [redirectToPanel, setRedirectToPanel] = useState(false);

    const [discussionData, setDiscussionData] = useState(null);
    const [transcriptData, setTranscriptData] = useState(null);
    const [transcriptUrls, setTranscriptUrls] = useState({});
    const [audioUrls, setAudioUrls] = useState({});

    useEffect(() => {
        if (initialPanelId) {
            setPanelId(initialPanelId);
        } else {
            setPanelId(null);
            setTranscriptData(null);
        }
    }, [initialPanelId]);

    useEffect(() => {
        if (panelId) {
            handleRefreshPanelData(panelId);
        }
    }, [panelId]);

    const handleRefreshPanelData = async (panelId) => {
        try {
            const { discussionData, transcriptData, audioData, filesData } =
                await fetchPanelDetails(panelId);
            setDiscussionData(discussionData);
            if (transcriptData.length > 0) {
                const sortedTranscripts = transcriptData.sort((a, b) => {
                    const dateA = new Date(a.created_at);
                    const dateB = new Date(b.created_at);
                    return dateB - dateA; // Descending order
                });
                setTranscriptData(sortedTranscripts);
            }
            setExistingAudio(audioData);
            const updatedTranscriptUrls = urlFormatter(
                filesData.transcript_urls
            );
            const updatedAudioUrls = urlFormatter(filesData.audio_urls);
            setTranscriptUrls(updatedTranscriptUrls);
            setAudioUrls(updatedAudioUrls);
        } catch (error) {
            console.error("Error refreshing panel data:", error);
        }
    };

    const handlePollSuccess = () => {
        fetchPanels();
        handleRefreshPanelData(panelId);
        setTaskStatus("idle");
    };

    const handlePollFailure = () => {
        setTaskStatus("idle");
    };

    const handlePollError = () => {
        console.error("Error polling task status");
        setTaskStatus("idle");
    };

    const initiatePolling = (taskId, type) => {
        setTaskStatus("processing"); // Set initial taskStatus
        setTimeout(() => {
            pollTaskStatus(
                taskId,
                type,
                handlePollSuccess,
                handlePollFailure,
                handlePollError,
                (isPolling) => setIsPolling(isPolling)
            );
        }, 1000);
    };

    const handleDelete = (deleteTarget) => {
        handleDeleteItem(deleteTarget, () => handleRefreshPanelData(panelId));
    };

    if (redirectToPanel) {
        return <Navigate to={`/panel/${panelId}`} />;
    }

    return (
        <div className="space-y-4">
            <div
                className={`status-bar p-2 text-white ${getStatusBarStyle(
                    taskStatus
                )}`}
            >
                <div className="flex items-center justify-center">
                    {isPolling && (
                        <Spinner
                            animation="border"
                            role="status"
                            className="mr-2"
                        >
                            <span className="sr-only">Building...</span>
                        </Spinner>
                    )}
                    <div className="status-text">
                        {getStatusSymbol(taskStatus)} Status: {taskStatus}
                    </div>
                </div>
            </div>
            {!panelId && (
                <PanelDetailEdit
                    setPanelId={setPanelId}
                    taskStatus={taskStatus}
                    setSelectedPanel={setSelectedPanel}
                    fetchPanels={fetchPanels}
                    handleRefreshPanelData={handleRefreshPanelData}
                    setRedirectToPanel={setRedirectToPanel}
                />
            )}
            {panelId && discussionData && (
                <PanelDetailDisplay
                    panel={discussionData}
                    isEditMode={true}
                    taskStatus={taskStatus}
                />
            )}
            {transcriptData && (
                <Accordion defaultActiveKey={0}>
                    {transcriptData.map((transcript, index) => (
                        <Accordion.Item eventKey={index}>
                            <Accordion.Header>
                                <div class="flex justify-between items-center w-full pr-4">
                                    <div className="flex-none flex flex-col items-center gap-2">
                                        {transcript.transcript_parent_id && (
                                            <FaSyncAlt
                                                className="inline-block mr-2 text-blue-500"
                                                title="Recurring Generation"
                                            />
                                        )}
                                        {!transcript.transcript_parent_id &&
                                            (transcript.generation_cronjob ? (
                                                <FaClock
                                                    className="inline-block mr-2 text-green-500"
                                                    title="Scheduled Generation"
                                                />
                                            ) : (
                                                <FaRegStar
                                                    className="inline-block mr-2 text-gray-500"
                                                    title="No Update Cycle"
                                                />
                                            ))}
                                    </div>
                                    <div class="flex-1">
                                        {`Transcript ${transcriptData.length - index}`}
                                        : {transcript.title}
                                    </div>
                                    <Button
                                        variant="danger"
                                        onClick={() =>
                                            showConfirmationDialog(
                                                "Are you sure you want to delete this transcript? This action cannot be undone.",
                                                () =>
                                                    handleDelete({
                                                        type: "transcript",
                                                        id: transcript.id
                                                    })
                                            )
                                        }
                                        className="flex-none"
                                        aria-label="Delete Transcript"
                                    >
                                        <FaTimes className="inline-block" />
                                    </Button>
                                </div>
                            </Accordion.Header>
                            <Accordion.Body>
                                <TranscriptDetailDisplay
                                    transcript={transcript}
                                    transcriptUrls={transcriptUrls}
                                    existingAudio={existingAudio}
                                    audioUrls={audioUrls}
                                />
                            </Accordion.Body>
                        </Accordion.Item>
                    ))}
                </Accordion>
            )}
            {taskStatus !== "idle" &&
            taskStatus !== "success" &&
            taskStatus !== "failure" ? null : (
                <TranscriptDetailEdit
                    panelId={panelId}
                    discussionData={discussionData}
                    taskStatus={taskStatus}
                    initiatePolling={initiatePolling}
                    visible={transcriptData && transcriptData.length === 0}
                />
            )}
            {transcriptData &&
                transcriptData.length > 0 &&
                (taskStatus !== "idle" &&
                taskStatus !== "success" &&
                taskStatus !== "failure" ? (
                    <div className="processing-container border p-3 mb-4 rounded">
                        <h3 className="font-bold mb-3">Processing...</h3>
                        <p>Please wait while the task is being processed.</p>
                    </div>
                ) : (
                    <AudioDetailEdit
                        panelId={panelId}
                        transcriptData={transcriptData}
                        taskStatus={taskStatus}
                        initiatePolling={initiatePolling}
                        visible={!transcriptData || transcriptData.length === 0}
                    />
                ))}
        </div>
    );
}

export default PanelEdit;
