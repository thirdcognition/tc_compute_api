import { useState, useEffect } from "react";
import AudioDetailDisplay from "./AudioDetailDisplay.jsx";
import { handleCreateTranscript } from "./helpers/panel.js";
import {
    fetchPanelDetails,
    fetchTranscriptContent,
    updateTranscript
} from "./helpers/fetch.js";
import { showConfirmationDialog, handleDeleteItem } from "./helpers/panel.js";
import {
    processStateIcon,
    getWordCountDescription,
    formatCronjob
} from "./helpers/ui.js";
import {
    FaTimes,
    FaClock,
    FaRegStar,
    FaCalendarAlt,
    FaSyncAlt
} from "react-icons/fa";
import CronjobComponent from "./components/CronjobComponent.jsx";
import { Button, Card, Accordion } from "react-bootstrap";
import { pollTaskStatus } from "./helpers/pollState.js";

const TranscriptDetailDisplay = ({ transcript }) => {
    const [showDetails, setShowDetails] = useState(false);
    const [isTranscriptVisible, setIsTranscriptVisible] = useState(false);
    const [transcriptContent, setTranscriptContent] = useState("");
    const [cronjob, setCronjob] = useState(
        transcript.generation_cronjob || transcript.metadata?.cronjob || ""
    ); // Editable cronjob in seconds
    const config = transcript.metadata?.conversation_config || {};
    const [audios, setAudios] = useState([]);
    const [transcriptUrls, setTranscriptUrls] = useState({});
    const [audioUrls, setAudioUrls] = useState({});
    const [transcriptSources, setTranscriptSources] = useState([]);
    const [, setIsPolling] = useState(false);
    const [isSourcesVisible, setIsSourcesVisible] = useState(false);
    const [taskStatus, setTaskStatus] = useState("idle");

    useEffect(() => {
        fetchPanelDetails(transcript.panel_id).then((response) => {
            setTranscriptUrls(response.filesData.transcript_urls);
            setAudioUrls(response.filesData.audio_urls);
            setAudios(response.audioData);
            setTranscriptSources(
                response.transcriptSources[transcript.id] || []
            );
        });
    }, [transcript.panel_id, transcript.id]);

    const toggleTranscriptVisibility = (transcriptId) => {
        if (!isTranscriptVisible && transcriptUrls[transcriptId]) {
            fetchTranscriptContent(transcriptUrls[transcriptId])
                .then((text) => {
                    setTranscriptContent(text);
                    setIsTranscriptVisible(true);
                })
                .catch((error) =>
                    console.error("Error fetching transcript:", error)
                );
        } else {
            setIsTranscriptVisible(!isTranscriptVisible);
        }
    };

    const renderTranscript = (transcriptContent) => {
        const personRegex = /<([^>]+)>([^<]+)<\/\1>/g;
        const matches = [...transcriptContent.matchAll(personRegex)];

        return matches.map((match, index) => (
            <div
                key={index}
                className="flex items-start mb-2 p-2 border-b border-gray-300"
            >
                <strong className="text-blue-600 w-24">{match[1]}</strong>
                <span className="text-gray-700 flex-1">{match[2].trim()}</span>
            </div>
        ));
    };

    const renderSources = () => {
        return transcriptSources.map((source) => (
            <Card key={source.id} className="mb-4">
                {source.data.image && (
                    <Card.Img
                        variant="top"
                        src={source.data.image}
                        alt={source.data.title}
                    />
                )}
                <Card.Body>
                    <Card.Title>
                        {source.data.url ? (
                            <a
                                href={source.data.url}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {source.data.title}
                            </a>
                        ) : (
                            source.data.title
                        )}
                    </Card.Title>
                    <Card.Text>
                        {new Date(source.data.publish_date).toLocaleString()}
                    </Card.Text>
                </Card.Body>
            </Card>
        ));
    };

    const toggleSourcesVisibility = () => {
        setIsSourcesVisible(!isSourcesVisible);
    };

    const handleUpdateTranscript = async (newCronjob) => {
        try {
            const updatedTranscript = await updateTranscript(
                transcript.id,
                transcript,
                newCronjob
            );
            setCronjob(updatedTranscript.generation_cronjob || "");
        } catch (error) {
            console.error("Error updating transcript:", error);
        }
    };

    const handleDuplicateTranscript = async () => {
        setTaskStatus("processing");
        try {
            const { taskId, success } = await handleCreateTranscript({
                panelId: transcript.panel_id,
                discussionData: { metadata: transcript.metadata },
                wordCount:
                    transcript.metadata?.conversation_config?.word_count ||
                    2500,
                creativity:
                    transcript.metadata?.conversation_config?.creativity || 0.7,
                conversationStyle:
                    transcript.metadata?.conversation_config
                        ?.conversation_style || [],
                rolesPerson1:
                    transcript.metadata?.conversation_config?.roles_person1 ||
                    "",
                rolesPerson2:
                    transcript.metadata?.conversation_config?.roles_person2 ||
                    "",
                dialogueStructure:
                    transcript.metadata?.conversation_config
                        ?.dialogue_structure || [],
                engagementTechniques:
                    transcript.metadata?.conversation_config
                        ?.engagement_techniques || [],
                userInstructions:
                    transcript.metadata?.conversation_config
                        ?.user_instructions || "",
                outputLanguage:
                    transcript.metadata?.conversation_config?.output_language ||
                    "English",
                longForm: transcript.metadata?.longform,
                cronjob: cronjob
            });
            if (success && taskId) {
                console.log(
                    "Transcript duplicated successfully, taskId:",
                    taskId
                );
                initiatePolling(taskId, "transcript");
            } else {
                setTaskStatus("failure");
            }
        } catch (error) {
            console.error("Error duplicating transcript:", error);
            setTaskStatus("failure");
        }
    };

    const initiatePolling = (taskId, type) => {
        setTaskStatus("processing"); // Set initial taskStatus
        setTimeout(() => {
            pollTaskStatus(
                taskId,
                type,
                () => {
                    setTaskStatus("success");
                },
                () => {
                    setTaskStatus("failure");
                },
                () => {
                    console.error("Error polling task status");
                    setTaskStatus("failure");
                },
                (isPolling) => setIsPolling(isPolling)
            );
        }, 1000);
    };

    const refreshAudios = () => {
        fetchPanelDetails(transcript.panel_id).then((response) => {
            setAudios(response.audioData);
        });
    };

    const handleDeleteAudio = (audioId) => {
        handleDeleteItem({ type: "audio", id: audioId }, refreshAudios);
    };

    return (
        <>
            {!transcript.transcript_parent_id && (
                <Button
                    onClick={handleDuplicateTranscript}
                    className={`w-full py-2 mb-4 flex items-center justify-center ${
                        taskStatus === "processing"
                            ? "bg-gray-500 border-gray-800 text-white"
                            : "bg-green-500 border-green-800 text-white"
                    }`}
                    disabled={taskStatus === "processing"}
                >
                    {taskStatus === "idle" && "Recreate Transcript"}
                    {taskStatus === "processing" && "Processing..."}
                    {taskStatus === "success" && "Success"}
                    {taskStatus === "failure" && "Failed"}
                </Button>
            )}
            <div className="flex items-center mb-4">
                <span className="mr-2">
                    {processStateIcon(transcript.process_state)}
                </span>
                <div class="flex-1 self-center">
                    <span className="mr-2">
                        <FaCalendarAlt className="inline-block" />
                    </span>
                    <span className="mr-2">
                        {new Date(transcript.created_at).toLocaleString()}
                    </span>
                </div>
                <div class="flex-1 self-center">
                    <span className="mr-2">
                        <FaClock className="inline-block" />
                    </span>
                    <span>
                        {new Date(transcript.updated_at).toLocaleString()}
                    </span>
                </div>
            </div>
            {transcript.process_state_message && (
                <Card className="mb-2 border-danger">
                    <Card.Header className="bg-danger text-white">
                        Error
                    </Card.Header>
                    <Card.Body>
                        <Card.Text>
                            {transcript.process_state_message}
                        </Card.Text>
                    </Card.Body>
                </Card>
            )}
            <Accordion defaultActiveKey={showDetails ? "0" : null}>
                <Accordion.Item eventKey="0">
                    <Accordion.Header>
                        {showDetails ? "Hide Details" : "Show More Details"}
                    </Accordion.Header>
                    <Accordion.Body>
                        {!transcript.transcript_parent_id && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Scheduling</Card.Title>
                                    {transcript.generation_cronjob &&
                                    cronjob ? (
                                        <>
                                            <Card.Text>
                                                {formatCronjob(cronjob)}
                                            </Card.Text>
                                            <Button
                                                variant="danger"
                                                onClick={() => setCronjob("")}
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
                                                onClick={() =>
                                                    handleUpdateTranscript(
                                                        cronjob
                                                    )
                                                }
                                            >
                                                Save schedule
                                            </Button>
                                        </>
                                    )}
                                </Card.Body>
                            </Card>
                        )}
                        {config.word_count && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Length</Card.Title>
                                    <Card.Text>
                                        {getWordCountDescription(
                                            config.word_count,
                                            4000
                                        )}
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                        )}
                        {config.conversation_style && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Conversation Style</Card.Title>
                                    <Card.Text>
                                        {config.conversation_style.join(", ")}
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                        )}
                        {config.roles_person1 && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Person 1 Details</Card.Title>
                                    <Card.Text>
                                        <strong>Name:</strong>{" "}
                                        {config.roles_person1.name || "Elton"}
                                    </Card.Text>
                                    <Card.Text>
                                        <strong>Persona:</strong>{" "}
                                        {config.roles_person1.persona ||
                                            "Not set"}
                                    </Card.Text>
                                    <Card.Text>
                                        <strong>Role:</strong>{" "}
                                        {config.roles_person1.role}
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                        )}
                        {config.roles_person2 && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Person 2 Details</Card.Title>
                                    <Card.Text>
                                        <strong>Name:</strong>{" "}
                                        {config.roles_person2.name || "Julia"}
                                    </Card.Text>
                                    <Card.Text>
                                        <strong>Persona:</strong>{" "}
                                        {config.roles_person2.persona ||
                                            "Not set"}
                                    </Card.Text>
                                    <Card.Text>
                                        <strong>Role:</strong>{" "}
                                        {config.roles_person2.role}
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                        )}
                        {config.dialogue_structure && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Dialogue Structure</Card.Title>
                                    <Card.Text>
                                        {config.dialogue_structure.join(", ")}
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                        )}
                        {config.engagement_techniques && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>
                                        Engagement Techniques
                                    </Card.Title>
                                    <Card.Text>
                                        {config.engagement_techniques.join(
                                            ", "
                                        )}
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                        )}
                        {config.user_instructions && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>User Instructions</Card.Title>
                                    <Card.Text>
                                        {config.user_instructions}
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                        )}
                        {config.output_language && (
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title>Output Language</Card.Title>
                                    <Card.Text>
                                        {config.output_language}
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                        )}
                        <Card className="mb-4">
                            <Card.Body>
                                <Card.Title>Process Mode</Card.Title>
                                <Card.Text>
                                    <strong>
                                        Process every article separately:
                                    </strong>{" "}
                                    {transcript.metadata?.longform
                                        ? "Yes"
                                        : "No"}
                                </Card.Text>
                            </Card.Body>
                        </Card>
                    </Accordion.Body>
                </Accordion.Item>
                <Accordion.Item eventKey="1">
                    <Accordion.Header
                        onClick={() => {
                            toggleTranscriptVisibility(transcript.id);
                        }}
                    >
                        {isTranscriptVisible
                            ? "Hide Transcript"
                            : "View Transcript"}
                    </Accordion.Header>
                    <Accordion.Body>
                        {(transcriptContent && (
                            <>
                                <p className="mb-2">
                                    Word Count:{" "}
                                    {
                                        transcriptContent
                                            .replace(/<\/?person\d+>/gi, "")
                                            .split(/\s+/).length
                                    }
                                </p>
                                {renderTranscript(transcriptContent)}
                            </>
                        )) || <p>Loading transcript...</p>}
                    </Accordion.Body>
                </Accordion.Item>
                {transcriptSources.length > 0 && (
                    <Accordion.Item eventKey="2">
                        <Accordion.Header onClick={toggleSourcesVisibility}>
                            {isSourcesVisible ? "Hide Sources" : "View Sources"}
                        </Accordion.Header>
                        <Accordion.Body>
                            {isSourcesVisible && renderSources()}
                        </Accordion.Body>
                    </Accordion.Item>
                )}
            </Accordion>
            <Accordion className="mt-4">
                {audios &&
                    audios
                        .filter(
                            (audio) => audio.transcript_id === transcript.id
                        )
                        .map((audio, index) => (
                            <Accordion.Item
                                eventKey={index.toString()}
                                key={audio.id}
                            >
                                <Accordion.Header>
                                    {audio.title}
                                </Accordion.Header>
                                <Accordion.Body>
                                    <div className="relative">
                                        <Button
                                            variant="danger"
                                            onClick={() =>
                                                showConfirmationDialog(
                                                    "Are you sure you want to delete this audio? This action cannot be undone.",
                                                    () =>
                                                        handleDeleteAudio(
                                                            audio.id
                                                        )
                                                )
                                            }
                                            className="absolute top-1 right-1"
                                            aria-label="Delete Audio"
                                        >
                                            <FaTimes className="inline-block" />
                                        </Button>
                                        <AudioDetailDisplay
                                            audio={audio}
                                            audioUrl={audioUrls[audio.id]}
                                        />
                                    </div>
                                </Accordion.Body>
                            </Accordion.Item>
                        ))}
            </Accordion>
        </>
    );
};

export default TranscriptDetailDisplay;
