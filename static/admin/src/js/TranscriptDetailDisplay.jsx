import React, { useState, useEffect, useCallback } from "react";
import { Button, Card, Accordion } from "react-bootstrap";

import { fetchPanelDetails, updateTranscript } from "./helpers/fetch.js";
import {
    showConfirmationDialog,
    handleDeleteItem,
    handleCreateTranscript
} from "./helpers/panel.js";
import { getWordCountDescription, formatCronjob } from "./helpers/ui.js";
import { pollTaskStatus } from "./helpers/pollState.js";
import { prepareDuplicateTranscriptParams } from "./helpers/transcriptHelpers.js";

// Shared & New Components
import CronjobComponent from "./components/CronjobComponent.jsx";
import StatusHeader from "./components/StatusHeader.jsx";
import ErrorMessage from "./components/ErrorMessage.jsx";
import SectionCard from "./components/SectionCard.jsx";
import DetailAccordion from "./components/DetailAccordion.jsx";
import TranscriptEditor from "./components/TranscriptEditor.jsx";
import TranscriptSourcesDisplay from "./components/TranscriptSourcesDisplay.jsx";
import PersonRolesDisplay from "./components/PersonRolesDisplay.jsx";
import TranscriptConfigDetails from "./components/TranscriptConfigDetails.jsx";
import TranscriptAudioList from "./components/TranscriptAudioList.jsx";

// --- Main Component ---
const TranscriptDetailDisplay = ({ transcript }) => {
    // --- State ---
    const [isTranscriptVisible, setIsTranscriptVisible] = useState(false);
    const [cronjob, setCronjob] = useState(
        transcript.generation_cronjob || transcript.metadata?.cronjob || ""
    );
    const [panelData, setPanelData] = useState(null);
    const [audios, setAudios] = useState([]);
    const [transcriptUrls, setTranscriptUrls] = useState({});
    const [audioUrls, setAudioUrls] = useState({});
    const [transcriptSources, setTranscriptSources] = useState([]);
    const [, setIsPolling] = useState(false);
    const [isSourcesVisible, setIsSourcesVisible] = useState(false);
    const [taskStatus, setTaskStatus] = useState("idle");
    const [refreshKey, setRefreshKey] = useState(0); // State to force refresh after save

    // --- Derived Data ---
    const metadata = transcript.metadata || {};
    const config = metadata.conversation_config || {};
    const personRoles = config.person_roles || {};

    // --- Effects ---
    useEffect(() => {
        fetchPanelDetails(transcript.panel_id)
            .then((response) => {
                setPanelData(response.discussionData);
                setAudioUrls(response.filesData.audio_urls);
                setTranscriptUrls(response.filesData.transcript_urls);
                setAudios(response.audioData || []);

                // Process sources
                const sourcesById = response.transcriptSources || {};
                const processed = Object.entries(sourcesById)
                    .map(([id, sources]) => {
                        const t = response.transcriptData.find(
                            (tr) => tr.id === id
                        );
                        if (
                            Array.isArray(t?.metadata?.subjects) &&
                            typeof t.metadata.subjects[0] === "object"
                        ) {
                            return { id, data: t.metadata.subjects };
                        }
                        return {
                            id,
                            data: Array.isArray(sources)
                                ? sources.map((s) => ({
                                      id: s?.id,
                                      url: s?.data?.url || "",
                                      title: s?.data?.title || "",
                                      publish_date: s?.data?.publish_date || "",
                                      image:
                                          s?.data?.image ||
                                          t?.metadata?.images?.[
                                              sources.indexOf(s)
                                          ] ||
                                          ""
                                  }))
                                : []
                        };
                    })
                    .filter((p) => p.id === transcript.id);

                setTranscriptSources(processed[0]?.data || []);
            })
            .catch((error) => {
                console.error("Failed to fetch panel details:", error);
            });
    }, [transcript.panel_id, transcript.id, refreshKey]);

    // --- Handlers ---
    const handleAccordionItemToggle = (item, isOpen) => {
        if (item.id === "transcript") {
            setIsTranscriptVisible(isOpen);
        } else if (item.id === "sources") {
            setIsSourcesVisible(isOpen);
        }
    };

    const handleSaveSuccess = useCallback(() => {
        setRefreshKey((prevKey) => prevKey + 1);
    }, []);

    const handleUpdateTranscriptCron = async (newCronjob) => {
        try {
            const updatedTranscriptResponse = await updateTranscript(
                transcript.id,
                transcript,
                newCronjob
            );
            if (updatedTranscriptResponse.success) {
                setRefreshKey((prevKey) => prevKey + 1); // Refresh data on success
            }
        } catch (error) {
            console.error("Error updating transcript cronjob:", error);
            alert("Failed to update schedule.");
        }
    };

    const handleDuplicateTranscript = async () => {
        setTaskStatus("processing");
        try {
            const params = prepareDuplicateTranscriptParams(
                transcript,
                panelData
            );
            if (!params) {
                setTaskStatus("failure");
                alert(
                    "Failed to prepare parameters for transcript duplication."
                );
                return;
            }
            const { taskId, success } = await handleCreateTranscript(params);
            if (success && taskId) {
                initiatePolling(taskId, "transcript");
            } else {
                setTaskStatus("failure");
                alert("Failed to initiate transcript duplication.");
            }
        } catch (error) {
            console.error("Error duplicating transcript:", error);
            setTaskStatus("failure");
            alert("An error occurred while duplicating the transcript.");
        }
    };

    const initiatePolling = (taskId, type) => {
        setTaskStatus("processing");
        setIsPolling(true);
        setTimeout(() => {
            pollTaskStatus(
                taskId,
                type,
                () => {
                    setTaskStatus("success");
                    setIsPolling(false);
                    setRefreshKey((prevKey) => prevKey + 1); // Refresh on success
                },
                () => {
                    setTaskStatus("failure");
                    setIsPolling(false);
                },
                () => {
                    console.error("Error polling task status");
                    setTaskStatus("failure");
                    setIsPolling(false);
                },
                (pollingStatus) => setIsPolling(pollingStatus)
            );
        }, 1000);
    };

    const refreshAudios = useCallback(() => {
        setRefreshKey((prevKey) => prevKey + 1); // Trigger refresh
    }, []);

    // handleDeleteAudio logic moved into TranscriptAudioList component

    // --- Render Functions ---
    // Renders the main details section using extracted components
    const renderDetailsBody = () => (
        <>
            {!transcript.transcript_parent_id && (
                <SectionCard title="Scheduling">
                    {transcript.generation_cronjob ? (
                        <>
                            <p>{formatCronjob(cronjob)}</p>
                            <Button
                                variant="outline-danger"
                                size="sm"
                                onClick={() => handleUpdateTranscriptCron("")}
                            >
                                Clear Schedule
                            </Button>
                        </>
                    ) : (
                        <>
                            <CronjobComponent
                                value={cronjob}
                                onChange={setCronjob}
                            />
                            <Button
                                size="sm"
                                className="mt-2"
                                onClick={() =>
                                    handleUpdateTranscriptCron(cronjob)
                                }
                            >
                                Save Schedule
                            </Button>
                        </>
                    )}
                </SectionCard>
            )}
            {/* Use extracted components */}
            <TranscriptConfigDetails config={config} metadata={metadata} />
            <PersonRolesDisplay personRoles={personRoles} />
        </>
    );

    // --- Main Render ---
    return (
        <>
            {!transcript.transcript_parent_id && (
                <Button
                    onClick={handleDuplicateTranscript}
                    className={`w-full py-2 mb-3 flex items-center justify-center ${taskStatus === "processing" ? "btn-secondary" : "btn-success"}`}
                    disabled={taskStatus === "processing"}
                >
                    {taskStatus === "processing"
                        ? "Processing..."
                        : "Recreate Transcript"}
                </Button>
            )}

            <StatusHeader item={transcript} />
            <ErrorMessage message={transcript.process_state_message} />

            <DetailAccordion
                onItemToggle={handleAccordionItemToggle}
                items={[
                    {
                        id: "details",
                        header: "Show Details",
                        body: renderDetailsBody // Use the simplified render function
                    },
                    {
                        id: "transcript",
                        header: isTranscriptVisible
                            ? "Hide Transcript"
                            : "View Transcript",
                        body: () =>
                            isTranscriptVisible ? (
                                <TranscriptEditor
                                    key={refreshKey}
                                    transcript={transcript}
                                    transcriptUrls={transcriptUrls}
                                    onSaveSuccess={handleSaveSuccess}
                                />
                            ) : null
                    },
                    transcriptSources.length > 0 && {
                        id: "sources",
                        header: isSourcesVisible
                            ? "Hide Sources"
                            : "View Sources",
                        // Use extracted component
                        body: () => (
                            <TranscriptSourcesDisplay
                                sources={transcriptSources}
                            />
                        )
                    }
                ].filter(Boolean)}
                itemKey="id"
                renderHeader={(item) => item.header}
                renderBody={(item) => item.body()}
                className="mb-4"
            />

            <SectionCard title="Generated Audio" headerAs="h5">
                {/* Use extracted component */}
                <TranscriptAudioList
                    audios={audios.filter(
                        (a) => a.transcript_id === transcript.id
                    )}
                    audioUrls={audioUrls}
                    onActionComplete={refreshAudios} // Pass refreshAudios as onActionComplete
                />
            </SectionCard>
        </>
    );
};

export default TranscriptDetailDisplay;
