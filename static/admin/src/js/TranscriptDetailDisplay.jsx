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
    FaTrash,
    FaClock,
    FaRegStar,
    FaCalendarAlt,
    FaChevronDown,
    FaChevronRight,
    FaSyncAlt
} from "react-icons/fa";
import CronjobComponent from "./components/CronjobComponent.jsx";
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
            <div key={source.id} className="mb-4 p-2 border rounded">
                <h6 className="font-bold">
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
                </h6>
                <p>{new Date(source.data.publish_date).toLocaleString()}</p>
                {source.data.image && (
                    <img
                        src={source.data.image}
                        alt={source.data.title}
                        className="w-full h-auto"
                    />
                )}
            </div>
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
        <div className="transcript-detail-display border p-3 mb-4 rounded">
            <div className="flex align-end mb-4">
                <div className="flex flex-col gap-2 self-center mr-4">
                    {transcript.transcript_parent_id && (
                        <FaSyncAlt
                            className="inline-block mr-2 text-blue-500"
                            title="Recurring Generation"
                        />
                    )}
                    {transcript.generation_cronjob ? (
                        <FaClock
                            className="inline-block mr-2 text-green-500"
                            title="Scheduled Generation"
                        />
                    ) : (
                        <FaRegStar
                            className="inline-block mr-2 text-gray-500"
                            title="No Update Cycle"
                        />
                    )}
                </div>
                <h5 className="font-bold self-center pr-5">
                    {transcript.title}
                </h5>
            </div>
            <p className="mb-3 flex items-between">
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
            </p>
            {transcript.process_state_message && (
                <p className="mb-2 text-red-500">
                    Error: {transcript.process_state_message}
                </p>
            )}
            {!transcript.transcript_parent_id && (
                <button
                    onClick={handleDuplicateTranscript}
                    className={`w-full py-2 mb-4 flex items-center justify-center rounded ${
                        taskStatus === "processing"
                            ? "bg-gray-500 text-white"
                            : "bg-green-500 text-white"
                    }`}
                    disabled={taskStatus === "processing"}
                >
                    {taskStatus === "idle" && "Recreate Transcript"}
                    {taskStatus === "processing" && "Processing..."}
                    {taskStatus === "success" && "Success"}
                    {taskStatus === "failure" && "Failed"}
                </button>
            )}
            <button
                onClick={() => setShowDetails(!showDetails)}
                className="w-full py-2 mb-4 flex items-center justify-center bg-blue-500 text-white rounded"
            >
                <span className="mr-2">
                    {showDetails ? (
                        <FaChevronDown className="inline-block" />
                    ) : (
                        <FaChevronRight className="inline-block" />
                    )}
                </span>
                <span>
                    {showDetails ? "Hide Details" : "Show More Details"}
                </span>
            </button>
            {showDetails && (
                <div className="border p-3 mb-4 rounded">
                    {config.word_count && (
                        <p className="mb-2">
                            Length:{" "}
                            {getWordCountDescription(config.word_count, 4000)}
                        </p>
                    )}
                    {/* {config.creativity && (
                        <p className="mb-2">Creativity: {config.creativity}</p>
                    )} */}
                    {config.conversation_style && (
                        <p className="mb-2">
                            Conversation Style:{" "}
                            {config.conversation_style.join(", ")}
                        </p>
                    )}
                    {config.roles_person1 && (
                        <div className="mb-2">
                            <p>
                                Name (Person 1):{" "}
                                {config.roles_person1.name || "Elton"}
                            </p>
                            <p>
                                Persona (Person 1):{" "}
                                {config.roles_person1.persona || "Not set"}
                            </p>
                            <p>Role (Person 1): {config.roles_person1.role}</p>
                        </div>
                    )}
                    {config.roles_person2 && (
                        <div className="mb-2">
                            <p>
                                Name (Person 2):{" "}
                                {config.roles_person2.name || "Julia"}
                            </p>
                            <p>
                                Persona (Person 2):{" "}
                                {config.roles_person2.persona || "Not set"}
                            </p>
                            <p>Role (Person 2): {config.roles_person2.role}</p>
                        </div>
                    )}
                    {config.dialogue_structure && (
                        <p className="mb-2">
                            Dialogue Structure:{" "}
                            {config.dialogue_structure.join(", ")}
                        </p>
                    )}
                    {config.engagement_techniques && (
                        <p className="mb-2">
                            Engagement Techniques:{" "}
                            {config.engagement_techniques.join(", ")}
                        </p>
                    )}
                    {config.user_instructions && (
                        <p className="mb-2">
                            User Instructions: {config.user_instructions}
                        </p>
                    )}
                    {config.output_language && (
                        <p className="mb-2">
                            Output Language: {config.output_language}
                        </p>
                    )}
                    <p className="mb-2">
                        Process every article separately. (higher quality,
                        longer process time):{" "}
                        {transcript.metadata?.longform ? "Yes" : "No"}
                    </p>
                    {!transcript.transcript_parent_id && (
                        <>
                            {transcript.generation_cronjob && cronjob ? (
                                <div className="mb-4">
                                    <p className="mb-2">
                                        Scheduled: {formatCronjob(cronjob)}
                                    </p>
                                    <button
                                        onClick={() => setCronjob("")}
                                        className="bg-red-500 text-white py-1 px-3 rounded"
                                    >
                                        Clear Schedule
                                    </button>
                                </div>
                            ) : (
                                <>
                                    <label className="font-semibold mb-1 block">
                                        Update Cycle:
                                    </label>
                                    <CronjobComponent
                                        value={cronjob}
                                        onChange={setCronjob}
                                    />
                                    <button
                                        onClick={() =>
                                            handleUpdateTranscript(cronjob)
                                        }
                                        className="bg-blue-500 text-white py-1 px-3 rounded"
                                    >
                                        Update
                                    </button>
                                </>
                            )}
                        </>
                    )}
                </div>
            )}
            {transcript.process_state === "done" && (
                <button
                    onClick={() => toggleTranscriptVisibility(transcript.id)}
                    className="w-full py-2 mb-4 flex items-center justify-center bg-blue-500 text-white rounded"
                >
                    <span className="mr-2">
                        {isTranscriptVisible ? (
                            <FaChevronDown className="inline-block" />
                        ) : (
                            <FaChevronRight className="inline-block" />
                        )}
                    </span>
                    <span>
                        {isTranscriptVisible
                            ? "Hide Transcript"
                            : "View Transcript"}
                    </span>
                </button>
            )}
            {isTranscriptVisible && (
                <div className="mt-4">
                    <p className="mb-2">
                        Word Count:{" "}
                        {
                            transcriptContent
                                .replace(/<\/?person\d+>/gi, "")
                                .split(/\s+/).length
                        }
                    </p>
                    {renderTranscript(transcriptContent)}
                </div>
            )}
            {transcript.process_state === "done" && (
                <button
                    onClick={toggleSourcesVisibility}
                    className="w-full py-2 mb-4 flex items-center justify-center bg-blue-500 text-white rounded"
                >
                    <span className="mr-2">
                        {isSourcesVisible ? (
                            <FaChevronDown className="inline-block" />
                        ) : (
                            <FaChevronRight className="inline-block" />
                        )}
                    </span>
                    <span>
                        {isSourcesVisible ? "Hide Sources" : "View Sources"}
                    </span>
                </button>
            )}
            {isSourcesVisible && (
                <div className="mt-4 border p-3 mb-4 rounded">
                    {renderSources()}
                </div>
            )}
            {audios &&
                audios
                    .filter((audio) => audio.transcript_id === transcript.id)
                    .map((audio) => (
                        <div key={audio.id} className="relative">
                            <button
                                onClick={() =>
                                    showConfirmationDialog(
                                        "Are you sure you want to delete this audio? This action cannot be undone.",
                                        () => handleDeleteAudio(audio.id)
                                    )
                                }
                                className="absolute top-1 right-1 p-2 text-red-500 hover:text-red-700"
                                aria-label="Delete Audio"
                            >
                                <FaTrash />
                            </button>
                            <AudioDetailDisplay
                                audio={audio}
                                audioUrl={audioUrls[audio.id]}
                            />
                        </div>
                    ))}
        </div>
    );
};

export default TranscriptDetailDisplay;
