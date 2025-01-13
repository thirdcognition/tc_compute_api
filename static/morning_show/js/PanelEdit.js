// PanelEdit.js
import { urlFormatter } from "./helpers/url.js";
const { Form, Button, Spinner } = ReactBootstrap;
const { useState, useEffect } = React;
const { Redirect } = ReactRouterDOM;
import PanelDetailEdit from "./PanelDetailEdit.js";
import PanelDetailDisplay from "./PanelDetailDisplay.js";
import TranscriptDetailEdit from "./TranscriptDetailEdit.js";
import TranscriptDetailDisplay from "./TranscriptDetailDisplay.js";
import AudioDetailEdit from "./AudioDetailEdit.js";
import { pollTaskStatus } from "./helpers/pollState.js";
import { refreshPanelData } from "./helpers/fetch.js";

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
                await refreshPanelData(panelId);
            setDiscussionData(discussionData);
            if (transcriptData.length > 0) {
                setTranscriptData(transcriptData);
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

    if (redirectToPanel) {
        return React.createElement(Redirect, { to: `/panel/${panelId}` });
    }

    return React.createElement(
        "div",
        { className: "space-y-4" },

        React.createElement(
            "div",
            {
                className: `status-bar p-2 text-white ${getStatusBarStyle(taskStatus)}`
            },
            React.createElement(
                "div",
                { className: "flex items-center justify-center" },
                isPolling &&
                    React.createElement(
                        Spinner,
                        {
                            animation: "border",
                            role: "status",
                            className: "mr-2"
                        },
                        React.createElement(
                            "span",
                            { className: "sr-only" },
                            "Building..."
                        )
                    ),
                React.createElement(
                    "div",
                    { className: "status-text" },
                    `${getStatusSymbol(taskStatus)} Status: ${taskStatus}`
                )
            )
        ),
        !panelId &&
            React.createElement(PanelDetailEdit, {
                setPanelId,
                taskStatus,
                setSelectedPanel,
                fetchPanels,
                handleRefreshPanelData,
                setRedirectToPanel
            }),
        panelId &&
            discussionData &&
            React.createElement(PanelDetailDisplay, {
                panel: discussionData
            }),
        transcriptData &&
            transcriptData.map((transcript) =>
                React.createElement(TranscriptDetailDisplay, {
                    transcript: transcript,
                    transcriptUrls,
                    existingAudio,
                    audioUrls
                })
            ),
        taskStatus !== "idle" &&
            taskStatus !== "success" &&
            taskStatus !== "failure"
            ? null
            : React.createElement(TranscriptDetailEdit, {
                  panelId,
                  discussionData,
                  taskStatus,
                  initiatePolling
              }),
        taskStatus !== "idle" &&
            taskStatus !== "success" &&
            taskStatus !== "failure"
            ? React.createElement(
                  "div",
                  {
                      className: "processing-container border p-3 mb-4 rounded"
                  },
                  React.createElement(
                      "h3",
                      { className: "font-bold mb-3" },
                      "Processing..."
                  ),
                  React.createElement(
                      "p",
                      null,
                      "Please wait while the task is being processed."
                  )
              )
            : React.createElement(AudioDetailEdit, {
                  panelId,
                  transcriptData,
                  taskStatus,
                  initiatePolling
              })
    );
}

export default PanelEdit;
