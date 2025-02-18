import { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";
import { defaultTtsModelOptions } from "./options.js";
import { handleCreateAudio } from "./helpers/panel.js";
import { FaChevronDown, FaChevronRight } from "react-icons/fa";

function AudioDetailEdit({
    panelId,
    transcriptData,
    taskStatus,
    initiatePolling
}) {
    const [ttsModel, setTtsModel] = useState("elevenlabs");
    const [defaultVoiceQuestion, setDefaultVoiceQuestion] = useState("");
    const [defaultVoiceAnswer, setDefaultVoiceAnswer] = useState("");
    const [transcriptId, setTranscriptId] = useState(null);
    const [showDetails, setShowDetails] = useState(false);

    useEffect(() => {
        const selectedModel = defaultTtsModelOptions.find(
            (model) => model.value === ttsModel
        );
        if (selectedModel) {
            setDefaultVoiceQuestion(selectedModel.defaultVoices.question);
            setDefaultVoiceAnswer(selectedModel.defaultVoices.answer);
        }
    }, [ttsModel]);

    useEffect(() => {
        if (transcriptData && transcriptData.length > 0) {
            setTranscriptId(transcriptData[0].id);
        }
    }, [transcriptData]);

    useEffect(() => {
        if (!ttsModel) {
            setTtsModel(defaultTtsModelOptions[0].value);
        }
    }, [ttsModel]);

    const handleAudioSubmit = async (e) => {
        e.preventDefault();
        if (!transcriptId) {
            console.error("Transcript ID is not selected.");
            return;
        }
        console.log("PanelId", panelId, "TranscriptId", transcriptId);
        if (panelId && transcriptId) {
            handleCreateAudio({
                panelId,
                transcriptId, // Ensure UUID is passed as-is
                ttsModel,
                defaultVoiceQuestion,
                defaultVoiceAnswer
            }).then(({ taskId, success }) => {
                if (success && taskId) {
                    initiatePolling(taskId, "audio");
                }
            });
        }
    };

    return (
        <>
            <div className="audio-container border p-3 mb-4 rounded">
                <h3 className="font-bold mb-3">Create Audio</h3>
                <Form onSubmit={handleAudioSubmit}>
                    <div className="mt-3">
                        {transcriptData && transcriptData.length > 1 && (
                            <>
                                <label htmlFor="transcriptSelect">
                                    Select Transcript
                                </label>
                                <select
                                    id="transcriptSelect"
                                    value={transcriptId}
                                    onChange={(e) =>
                                        setTranscriptId(e.target.value)
                                    }
                                    className="form-select"
                                >
                                    {transcriptData
                                        .filter(
                                            (transcript) =>
                                                transcript.process_state ===
                                                "done"
                                        )
                                        .sort(
                                            (a, b) =>
                                                new Date(b.created_at) -
                                                new Date(a.created_at)
                                        )
                                        .map((transcript) => (
                                            <option
                                                key={transcript.id}
                                                value={transcript.id}
                                            >
                                                {transcript.title}
                                            </option>
                                        ))}
                                </select>
                            </>
                        )}
                    </div>
                    <Form.Group controlId="ttsModel" className="mb-3">
                        <Form.Label className="font-semibold">
                            TTS Model:
                        </Form.Label>
                        <Form.Control
                            as="select"
                            value={ttsModel || defaultTtsModelOptions[0].value}
                            onChange={(e) => setTtsModel(e.target.value)}
                            className="w-full"
                        >
                            {defaultTtsModelOptions.map((model) => (
                                <option
                                    value={model.value}
                                    key={model.value}
                                    disabled={model.disabled ? true : undefined}
                                >
                                    {model.label}
                                </option>
                            ))}
                        </Form.Control>
                    </Form.Group>
                    <Button
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
                    </Button>
                    {showDetails && (
                        <>
                            <Form.Group controlId="defaultVoiceQuestion">
                                <Form.Label className="font-semibold">
                                    Default Voice for Question:
                                </Form.Label>
                                <Form.Control
                                    type="text"
                                    placeholder="Enter default voice for questions..."
                                    value={defaultVoiceQuestion}
                                    onChange={(e) =>
                                        setDefaultVoiceQuestion(e.target.value)
                                    }
                                    className="w-full"
                                />
                            </Form.Group>
                            <Form.Group controlId="defaultVoiceAnswer">
                                <Form.Label className="font-semibold">
                                    Default Voice for Answer:
                                </Form.Label>
                                <Form.Control
                                    type="text"
                                    placeholder="Enter default voice for answers..."
                                    value={defaultVoiceAnswer}
                                    onChange={(e) =>
                                        setDefaultVoiceAnswer(e.target.value)
                                    }
                                    className="w-full"
                                />
                            </Form.Group>
                        </>
                    )}
                    <Button
                        variant="primary"
                        type="submit"
                        className="w-full py-2 mt-3"
                        disabled={
                            !transcriptData ||
                            (taskStatus !== "idle" &&
                                taskStatus !== "failure" &&
                                taskStatus !== "success")
                        }
                    >
                        Create Audio
                    </Button>
                </Form>
            </div>
        </>
    );
}

export default AudioDetailEdit;
