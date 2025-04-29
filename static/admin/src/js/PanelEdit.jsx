import { Spinner, Button } from "react-bootstrap"; // Removed Accordion import
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
import { FaClock, FaRegStar, FaSyncAlt } from "react-icons/fa"; // Removed FaTimes as it's in RemoveButton

import { getStatusBarStyle, getStatusSymbol } from "./helpers/ui.js";

// Import shared components
import DetailAccordion from "./components/DetailAccordion.jsx";
import RemoveButton from "./components/RemoveButton.jsx";

function PanelEdit({ fetchPanels, setSelectedPanel, initialPanelId }) {
    const [taskStatus, setTaskStatus] = useState("idle");
    const [isPolling, setIsPolling] = useState(false);
    // Remove unused state: existingAudio, transcriptUrls, audioUrls (handled within TranscriptDetailDisplay)
    // const [existingAudio, setExistingAudio] = useState(null);
    // const [transcriptUrls, setTranscriptUrls] = useState({});
    // const [audioUrls, setAudioUrls] = useState({});
    const [panelId, setPanelId] = useState(initialPanelId || null);
    const [redirectToPanel, setRedirectToPanel] = useState(false);

    const [discussionData, setDiscussionData] = useState(null);
    const [transcriptData, setTranscriptData] = useState(null);
    const [audioData, setAudioData] = useState(null); // Add state for audio data

    useEffect(() => {
        if (initialPanelId) {
            setPanelId(initialPanelId);
        } else {
            setPanelId(null);
            setTranscriptData(null);
            setAudioData(null); // Reset audio data too
        }
    }, [initialPanelId]);

    useEffect(() => {
        if (panelId) {
            handleRefreshPanelData(panelId);
        }
    }, [panelId]);

    const handleRefreshPanelData = async (panelId) => {
        try {
            // Fetch discussion, transcript, and audio data
            const { discussionData, transcriptData, audioData } =
                await fetchPanelDetails(panelId);
            setDiscussionData(discussionData);

            // Handle Transcript Data
            if (transcriptData && transcriptData.length > 0) {
                // Check if transcriptData is not null
                const sortedTranscripts = transcriptData.sort((a, b) => {
                    const dateA = new Date(a.created_at);
                    const dateB = new Date(b.created_at);
                    return dateB - dateA; // Descending order
                });
                setTranscriptData(sortedTranscripts);
            } else {
                setTranscriptData([]); // Set to empty array if null or empty
            }

            // Handle Audio Data
            if (audioData && audioData.length > 0) {
                setAudioData(audioData);
            }
            // Remove setting state for data handled internally by other components
            // const updatedTranscriptUrls = urlFormatter(filesData.transcript_urls);
            // const updatedAudioUrls = urlFormatter(filesData.audio_urls);
            // setTranscriptUrls(updatedTranscriptUrls);
            // setAudioUrls(updatedAudioUrls);
        } catch (error) {
            console.error("Error refreshing panel data:", error);
        }
    };

    const handlePollSuccess = () => {
        if (fetchPanels) fetchPanels(); // Check if fetchPanels exists
        if (panelId) handleRefreshPanelData(panelId); // Check if panelId exists
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
        setIsPolling(true); // Ensure polling state is set
        setTimeout(() => {
            pollTaskStatus(
                taskId,
                type,
                handlePollSuccess,
                handlePollFailure,
                handlePollError,
                (pollingStatus) => setIsPolling(pollingStatus) // Update polling state
            );
        }, 1000);
    };

    // Renamed for clarity, used by RemoveButton callback
    const handleDeleteTranscript = (transcriptId) => {
        // Pass only the necessary callback to refresh this component's data
        handleDeleteItem({ type: "transcript", id: transcriptId }, () =>
            handleRefreshPanelData(panelId)
        );
    };

    if (redirectToPanel) {
        return <Navigate to={`/panel/${panelId}`} />;
    }

    // --- Render Functions for DetailAccordion ---
    const renderTranscriptHeader = (transcript, index) => (
        <div className="d-flex justify-content-between align-items-center w-100">
            {/* Left side: Status Icons */}
            <div
                className="flex-shrink-0 me-3 d-flex flex-column align-items-center"
                style={{ width: "20px" }}
            >
                {transcript.transcript_parent_id && (
                    <FaSyncAlt
                        className="text-blue-500 mb-1"
                        title="Recurring Generation"
                        size="0.9em"
                    />
                )}
                {!transcript.transcript_parent_id &&
                    (transcript.generation_cronjob ? (
                        <FaClock
                            className="text-green-500 mb-1"
                            title="Scheduled Generation"
                            size="0.9em"
                        />
                    ) : (
                        <FaRegStar
                            className="text-gray-500 mb-1"
                            title="No Update Cycle"
                            size="0.9em"
                        />
                    ))}
            </div>

            {/* Middle: Title */}
            <div className="flex-grow-1 text-start mx-2">
                {`Transcript ${transcriptData.length - index}`}:{" "}
                {transcript.title || `ID: ${transcript.id.substring(0, 6)}`}
            </div>

            {/* Right side: Remove Button */}
            <div className="flex-shrink-0 ms-2">
                <RemoveButton
                    onClick={(e) => {
                        e.stopPropagation(); // Prevent accordion toggle
                        showConfirmationDialog(
                            "Are you sure you want to delete this transcript? This action cannot be undone.",
                            () => handleDeleteTranscript(transcript.id)
                        );
                    }}
                    ariaLabel="Delete Transcript"
                    size="sm" // Match previous size if needed
                />
            </div>
        </div>
    );

    // Corrected: Only pass the transcript prop
    const renderTranscriptBody = (transcript) => (
        <TranscriptDetailDisplay transcript={transcript} />
    );

    // --- Main Render ---
    return (
        <div className="space-y-4">
            {/* Status Bar */}
            <div
                className={`status-bar p-2 text-white text-center ${getStatusBarStyle(
                    taskStatus
                )}`}
            >
                <div className="d-flex align-items-center justify-content-center">
                    {isPolling && (
                        <Spinner
                            animation="border"
                            size="sm" // Smaller spinner
                            role="status"
                            className="me-2"
                        >
                            <span className="visually-hidden">Building...</span>
                        </Spinner>
                    )}
                    <div className="status-text">
                        {getStatusSymbol(taskStatus)} Status: {taskStatus}
                    </div>
                </div>
            </div>

            {/* Panel Edit/Display */}
            {!panelId && (
                <PanelDetailEdit
                    setPanelId={setPanelId}
                    taskStatus={taskStatus}
                    setSelectedPanel={setSelectedPanel}
                    fetchPanels={fetchPanels}
                    handleRefreshPanelData={handleRefreshPanelData}
                    setRedirectToPanel={setRedirectToPanel}
                    onCancel={() => {
                        /* Define cancel behavior if needed */
                    }} // Add onCancel if required by PanelDetailEdit
                />
            )}
            {panelId && discussionData && (
                <PanelDetailDisplay
                    panel={discussionData}
                    // isEditMode={true} // Prop likely redundant now
                    taskStatus={taskStatus}
                    // Pass necessary props for internal PanelDetailEdit instance
                    setPanelId={setPanelId}
                    setSelectedPanel={setSelectedPanel}
                    fetchPanels={fetchPanels}
                    handleRefreshPanelData={handleRefreshPanelData}
                    setRedirectToPanel={setRedirectToPanel}
                />
            )}

            {/* Transcript Creation Form (Conditionally Rendered) */}
            {taskStatus !== "idle" &&
            taskStatus !== "success" &&
            taskStatus !== "failure" ? null : (
                <TranscriptDetailEdit
                    panelId={panelId}
                    discussionData={discussionData}
                    transcriptData={transcriptData}
                    taskStatus={taskStatus}
                    initiatePolling={initiatePolling}
                    visible={transcriptData && transcriptData.length === 0} // Keep visibility logic
                />
            )}

            {/* Audio Creation Form (Conditionally Rendered) */}
            {transcriptData &&
                transcriptData.length > 0 &&
                (taskStatus !== "idle" &&
                taskStatus !== "success" &&
                taskStatus !== "failure" ? (
                    <div className="processing-container border p-3 mb-4 rounded text-center">
                        <h5 className="font-bold mb-2">Processing...</h5>
                        <p className="text-muted">
                            Please wait while the task is being processed.
                        </p>
                    </div>
                ) : (
                    <AudioDetailEdit
                        panelId={panelId}
                        transcriptData={transcriptData}
                        audioData={audioData} // Pass audioData prop
                        taskStatus={taskStatus}
                        initiatePolling={initiatePolling}
                        visible={!transcriptData || transcriptData.length === 0} // Keep visibility logic
                    />
                ))}

            {/* Transcript List Accordion */}
            {transcriptData && transcriptData.length > 0 && (
                <DetailAccordion
                    items={transcriptData}
                    itemKey="id" // Use transcript ID as the key
                    renderHeader={renderTranscriptHeader}
                    renderBody={renderTranscriptBody}
                    defaultActiveKey={transcriptData[0]?.id} // Open the first transcript by default using its ID
                    className="mt-4" // Add margin if needed
                />
            )}
        </div>
    );
}

export default PanelEdit;
