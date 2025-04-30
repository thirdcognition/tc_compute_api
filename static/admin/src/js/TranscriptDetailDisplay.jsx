import { useState, useEffect } from "react";
import { Button, Card, Accordion } from "react-bootstrap"; // Keep Accordion for nested source display

import {
    fetchPanelDetails,
    fetchTranscriptContent,
    updateTranscript
} from "./helpers/fetch.js";
import {
    showConfirmationDialog,
    handleDeleteItem,
    handleCreateTranscript
} from "./helpers/panel.js";
import { getWordCountDescription, formatCronjob } from "./helpers/ui.js";
import { pollTaskStatus } from "./helpers/pollState.js";
import { prepareDuplicateTranscriptParams } from "./helpers/transcriptHelpers.js"; // Import helper

// Shared Components
import AudioDetailDisplay from "./AudioDetailDisplay.jsx"; // Keep this specific display component
import CronjobComponent from "./components/CronjobComponent.jsx";
import StatusHeader from "./components/StatusHeader.jsx";
import ErrorMessage from "./components/ErrorMessage.jsx";
import SectionCard from "./components/SectionCard.jsx";
import ObjectDisplay from "./components/ObjectDisplay.jsx";
import DetailAccordion from "./components/DetailAccordion.jsx";
import RemoveButton from "./components/RemoveButton.jsx";

// --- Main Component ---
const TranscriptDetailDisplay = ({ transcript }) => {
    // --- State ---
    const [isTranscriptVisible, setIsTranscriptVisible] = useState(false);
    const [transcriptContent, setTranscriptContent] = useState("");
    const [cronjob, setCronjob] = useState(
        transcript.generation_cronjob || transcript.metadata?.cronjob || ""
    );
    const [panelData, setPanelData] = useState(null); // For discussionData if needed for recreate
    const [audios, setAudios] = useState([]);
    const [transcriptUrls, setTranscriptUrls] = useState({}); // Needed for fetching content
    const [audioUrls, setAudioUrls] = useState({}); // Passed down to AudioDetailDisplay
    const [transcriptSources, setTranscriptSources] = useState([]);
    const [, setIsPolling] = useState(false); // Keep for pollTaskStatus callback
    const [isSourcesVisible, setIsSourcesVisible] = useState(false);
    const [taskStatus, setTaskStatus] = useState("idle"); // For recreate button state

    // --- Derived Data ---
    const config = transcript.metadata?.conversation_config || {};
    const metadata = transcript.metadata || {};

    // --- Effects ---
    useEffect(() => {
        // Fetch related data when transcript ID changes
        fetchPanelDetails(transcript.panel_id).then((response) => {
            setPanelData(response.discussionData); // Store discussion data if needed
            setAudioUrls(response.filesData.audio_urls);
            setTranscriptUrls(response.filesData.transcript_urls);
            setAudios(response.audioData || []); // Ensure audios is an array

            // Process sources (simplified logic from original)
            const sourcesById = response.transcriptSources || {};
            const processed = Object.entries(sourcesById)
                .map(([id, sources]) => {
                    const t = response.transcriptData.find(
                        (tr) => tr.id === id
                    );
                    // Prefer subjects if available and structured correctly
                    if (
                        Array.isArray(t?.metadata?.subjects) &&
                        typeof t.metadata.subjects[0] === "object"
                    ) {
                        return { id, data: t.metadata.subjects };
                    }
                    // Fallback to processing transcriptSources array
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
                .filter((p) => p.id === transcript.id); // Only keep sources for the current transcript

            setTranscriptSources(processed[0]?.data || []); // Get data for the current transcript or empty array
        });
    }, [transcript.panel_id, transcript.id]); // Rerun if panel or transcript ID changes

    // --- Handlers ---
    // Handler for the DetailAccordion's onItemToggle prop
    const handleAccordionItemToggle = (item, isOpen) => {
        // Check if the toggled item is the transcript section
        if (item.id === "transcript") {
            setIsTranscriptVisible(isOpen); // Update visibility state

            // Fetch content only if opening and content isn't already loaded/loading
            if (isOpen && !transcriptContent) {
                const transcriptUrl = transcriptUrls[transcript.id];
                if (transcriptUrl) {
                    setTranscriptContent("Loading transcript..."); // Indicate loading
                    fetchTranscriptContent(transcriptUrl)
                        .then((text) => {
                            // Check state again in case it was closed quickly
                            setIsTranscriptVisible((currentVis) => {
                                if (currentVis) {
                                    // Only update if still visible
                                    setTranscriptContent(text);
                                }
                                return currentVis;
                            });
                        })
                        .catch((error) => {
                            console.error("Error fetching transcript:", error);
                            setIsTranscriptVisible((currentVis) => {
                                if (currentVis) {
                                    // Only update if still visible
                                    setTranscriptContent(
                                        "Error loading transcript."
                                    );
                                }
                                return currentVis;
                            });
                        });
                } else {
                    setIsTranscriptVisible((currentVis) => {
                        if (currentVis) {
                            // Only update if still visible
                            setTranscriptContent("Transcript URL not found.");
                        }
                        return currentVis;
                    });
                }
            } else if (!isOpen) {
                // Optional: Clear content when closing
                // setTranscriptContent("");
            }
        }
        // Handle other items if needed, e.g., sources visibility
        else if (item.id === "sources") {
            setIsSourcesVisible(isOpen);
        }
    };

    const handleUpdateTranscriptCron = async (newCronjob) => {
        try {
            const updatedTranscriptResponse = await updateTranscript(
                transcript.id,
                transcript, // Pass the current transcript data
                newCronjob
            );
            if (updatedTranscriptResponse.success) {
                location.reload();
                // setCronjob(updatedTranscript.generation_cronjob || "");
            }
        } catch (error) {
            console.error("Error updating transcript cronjob:", error);
            alert("Failed to update schedule.");
        }
    };

    const handleDuplicateTranscript = async () => {
        setTaskStatus("processing");
        try {
            // Prepare parameters using the helper function
            const params = prepareDuplicateTranscriptParams(
                transcript,
                panelData
            );

            if (!params) {
                // Handle error if params couldn't be prepared
                setTaskStatus("failure");
                alert(
                    "Failed to prepare parameters for transcript duplication."
                );
                return;
            }

            const { taskId, success } = await handleCreateTranscript(params);
            if (success && taskId) {
                initiatePolling(taskId, "transcript"); // Use the component's polling initiator
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
        setIsPolling(true); // Indicate polling started
        setTimeout(() => {
            pollTaskStatus(
                taskId,
                type,
                () => {
                    setTaskStatus("success");
                    setIsPolling(false); /* TODO: Refresh data? */
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
                (pollingStatus) => setIsPolling(pollingStatus) // Update polling state
            );
        }, 1000);
    };

    const refreshAudios = () => {
        fetchPanelDetails(transcript.panel_id).then((response) => {
            setAudios(response.audioData || []);
            setAudioUrls(response.filesData.audio_urls);
        });
    };

    const handleDeleteAudio = (audioId) => {
        handleDeleteItem({ type: "audio", id: audioId }, refreshAudios);
    };

    // --- Render Functions ---

    // Renders the transcript text content with speaker tags highlighted
    const renderTranscriptContent = (content) => {
        if (!content) return <p>Loading transcript...</p>;
        if (content === "Error loading transcript.")
            return <p className="text-red-500">{content}</p>; // Tailwind for error

        // Regex to capture tag (e.g., Person1), optional emote, and text, allowing other attributes
        const segmentRegex =
            /<([A-Za-z]+[0-9]+)(?:[^>]*emote="([^"]*)")?[^>]*>([^<]+)<\/\1>/g;
        const matches = [...content.matchAll(segmentRegex)];
        const wordCount = content.replace(/<[^>]+>/g, "").split(/\s+/).length;

        // Get person roles for name mapping
        const personRoles = config?.person_roles || {};

        if (matches.length > 0) {
            return (
                <>
                    <p className="mb-2 text-gray-500 text-sm">
                        Word Count: {wordCount}
                    </p>
                    {matches.map((match, index) => {
                        const tagName = match[1]; // e.g., "Person1"
                        const emote = match[2]; // e.g., "excited" or undefined
                        const text = match[3].trim(); // The actual transcript line

                        // Extract number from tag (e.g., "1" from "Person1")
                        const personNumberMatch = tagName.match(/[0-9]+/);
                        const personNumber = personNumberMatch
                            ? personNumberMatch[0]
                            : null;

                        // Get display name from config, fallback to tag name
                        const speakerName =
                            personNumber && personRoles[personNumber]?.name
                                ? personRoles[personNumber].name
                                : tagName;

                        return (
                            <div
                                key={index}
                                className="flex mb-2 border-b pb-2"
                            >
                                <span className="font-semibold text-blue-600 mr-3 min-w-[80px] flex-shrink-0">
                                    {speakerName}
                                </span>
                                <span className="flex-1">
                                    {text}
                                    {emote && (
                                        <div className="text-gray-400 ml-1">
                                            - {emote}
                                        </div>
                                    )}
                                </span>
                            </div>
                        );
                    })}
                </>
            );
        } else {
            // No matches found, display raw content
            return (
                <>
                    <p className="mb-2 text-gray-500 text-sm">
                        Word Count: {wordCount}
                    </p>
                    {/* Use whitespace-pre-wrap to preserve line breaks and spacing */}
                    <p className="whitespace-pre-wrap">{content}</p>
                </>
            );
        }
    };

    // Renders a single source item card
    const renderSourceItem = (option, index) => (
        <Card key={option.url || option.title || index} className="mb-3">
            {option.image && (
                <Card.Img
                    variant="top"
                    src={option.image}
                    alt={option.title}
                    style={{ maxHeight: "150px", objectFit: "cover" }}
                />
            )}
            <Card.Body>
                <Card.Title as="h6">
                    {Array.isArray(option.url) && option.url.length > 1 ? (
                        <Accordion>
                            <Accordion.Item eventKey="0">
                                <Accordion.Header>
                                    {option.title}
                                </Accordion.Header>
                                <Accordion.Body>
                                    {option.url.map((url, idx) => (
                                        <a
                                            key={idx}
                                            href={url?.trim()}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="d-block small text-truncate"
                                        >
                                            {idx + 1}: {url?.trim()}
                                        </a>
                                    ))}
                                </Accordion.Body>
                            </Accordion.Item>
                        </Accordion>
                    ) : (
                        <a
                            href={
                                Array.isArray(option.url)
                                    ? option.url[0]
                                    : option.url
                            }
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-decoration-none"
                        >
                            {option.title}
                        </a>
                    )}
                </Card.Title>
                {option.publish_date && (
                    <Card.Text className="text-muted small mt-1">
                        Published:{" "}
                        {new Date(option.publish_date).toLocaleDateString()}
                    </Card.Text>
                )}
            </Card.Body>
        </Card>
    );

    // Renders the list of sources
    const renderSourcesList = () => {
        if (!transcriptSources || transcriptSources.length === 0) {
            return <p>No sources found.</p>;
        }

        return transcriptSources.map((option, index) => {
            if (option.references) {
                // Handle grouped sources (like from subjects)
                return (
                    <Accordion key={option.title || index} className="mb-3">
                        <Accordion.Item eventKey="0">
                            <Accordion.Header>{option.title}</Accordion.Header>
                            <Accordion.Body>
                                {option.description && (
                                    <Card.Text className="mb-3">
                                        {option.description}
                                    </Card.Text>
                                )}
                                {option.references.map(renderSourceItem)}
                            </Accordion.Body>
                        </Accordion.Item>
                    </Accordion>
                );
            } else {
                // Handle individual source items
                return renderSourceItem(option, index);
            }
        });
    };

    // Renders the display for Person Roles
    const renderPersonRolesDisplay = () => {
        let personRolesData = {};
        if (config.person_roles) {
            personRolesData = config.person_roles;
        } else {
            /* backward compatibility logic */
        }

        if (!personRolesData || Object.keys(personRolesData).length === 0)
            return null;

        return (
            <SectionCard title="Person Roles">
                {Object.entries(personRolesData).map(([id, roleObj]) => (
                    <Card key={id} className="mb-3">
                        <Card.Header as="h6">
                            Person {id}: {roleObj.name || "N/A"}
                        </Card.Header>
                        <Card.Body>
                            {roleObj.role && (
                                <Card.Subtitle className="mb-2 text-muted">
                                    Role: {roleObj.role}
                                </Card.Subtitle>
                            )}
                            {roleObj.persona && (
                                <Card.Text>
                                    <strong>Persona:</strong> {roleObj.persona}
                                </Card.Text>
                            )}
                            {roleObj.voice_config && (
                                <div className="mt-2">
                                    <strong>Voice Config:</strong>
                                    <ObjectDisplay
                                        data={roleObj.voice_config}
                                    />
                                </div>
                            )}
                        </Card.Body>
                    </Card>
                ))}
            </SectionCard>
        );
    };

    // Renders the main details section within an accordion body
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
            {config.word_count && (
                <SectionCard title="Length">
                    <p>{getWordCountDescription(config.word_count, 4000)}</p>
                </SectionCard>
            )}
            {config.conversation_style?.length > 0 && (
                <SectionCard title="Conversation Style">
                    <p>{config.conversation_style.join(", ")}</p>
                </SectionCard>
            )}
            {renderPersonRolesDisplay()}
            {config.dialogue_structure?.length > 0 && (
                <SectionCard title="Dialogue Structure">
                    <p>{config.dialogue_structure.join(" → ")}</p>
                </SectionCard>
            )}
            {config.engagement_techniques?.length > 0 && (
                <SectionCard title="Engagement Techniques">
                    <p>{config.engagement_techniques.join(", ")}</p>
                </SectionCard>
            )}
            {config.user_instructions && (
                <SectionCard title="User Instructions">
                    <p>{config.user_instructions}</p>
                </SectionCard>
            )}
            {config.output_language && (
                <SectionCard title="Output Language">
                    <p>{config.output_language}</p>
                </SectionCard>
            )}
            <SectionCard title="Transcript Processing Options">
                <p>
                    <strong>Process every article separately:</strong>{" "}
                    {metadata.longform ? "Yes" : "No"}
                </p>
                <p>
                    <strong>Use short intro/conclusion:</strong>{" "}
                    {config.short_intro_and_conclusion ? "Yes" : "No"}
                </p>
                <p>
                    <strong>Disable intro/conclusion:</strong>{" "}
                    {config.disable_intro_and_conclusion ? "Yes" : "No"}
                </p>
            </SectionCard>
        </>
    );

    // Renders the list of associated audios
    const renderAudioListBody = () => {
        const filteredAudios = audios.filter(
            (audio) => audio.transcript_id === transcript.id
        );
        if (filteredAudios.length === 0) {
            return <p>No audio generated for this transcript yet.</p>;
        }
        return (
            <DetailAccordion
                items={filteredAudios}
                itemKey="id"
                renderHeader={(audio) => audio.title || `Audio ${audio.id}`}
                renderBody={(audio) => (
                    <div className="position-relative">
                        <RemoveButton
                            onClick={() =>
                                showConfirmationDialog(
                                    "Are you sure you want to delete this audio? This action cannot be undone.",
                                    () => handleDeleteAudio(audio.id)
                                )
                            }
                            className="position-absolute top-0 end-0 m-2" // Position top-right
                            ariaLabel="Delete Audio"
                            size="sm"
                        />
                        <AudioDetailDisplay
                            audio={audio}
                            audioUrl={audioUrls[audio.id]}
                        />
                    </div>
                )}
                className="mt-0" // Remove default top margin if nested
            />
        );
    };

    // --- Main Render ---
    return (
        <>
            {/* Recreate Button (only for non-child transcripts) */}
            {!transcript.transcript_parent_id && (
                <Button
                    onClick={handleDuplicateTranscript}
                    className={`w-full py-2 mb-3 d-flex align-items-center justify-content-center ${taskStatus === "processing" ? "btn-secondary" : "btn-success"}`}
                    disabled={taskStatus === "processing"}
                >
                    {taskStatus === "processing"
                        ? "Processing..."
                        : "Recreate Transcript"}
                </Button>
            )}

            {/* Status Header */}
            <StatusHeader item={transcript} />

            {/* Error Message */}
            <ErrorMessage message={transcript.process_state_message} />

            {/* Main Accordion for Details, Transcript, Sources */}
            <DetailAccordion
                onItemToggle={handleAccordionItemToggle} // Use the new callback
                items={[
                    {
                        id: "details",
                        header: "Show Details",
                        body: renderDetailsBody
                    },
                    {
                        id: "transcript",
                        header: isTranscriptVisible // Header text now depends on state
                            ? "Hide Transcript"
                            : "View Transcript",
                        body: () => renderTranscriptContent(transcriptContent)
                        // No onClick needed here anymore
                    },
                    transcriptSources.length > 0 && {
                        id: "sources",
                        header: isSourcesVisible // Header text depends on state
                            ? "Hide Sources"
                            : "View Sources",
                        body: renderSourcesList
                        // onClick handled by onItemToggle now
                    }
                ].filter(Boolean)} // Filter out sources item if empty
                itemKey="id"
                // renderHeader no longer needs to handle onClick
                renderHeader={(item) => item.header}
                renderBody={(item) => item.body()}
                className="mb-4"
            />

            {/* Section for Associated Audios */}
            <SectionCard title="Generated Audio" headerAs="h5">
                {renderAudioListBody()}
            </SectionCard>
        </>
    );
};

export default TranscriptDetailDisplay;
