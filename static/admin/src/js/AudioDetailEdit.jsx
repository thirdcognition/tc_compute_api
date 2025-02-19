import { useState, useEffect } from "react";
import { Form, Button, Accordion } from "react-bootstrap";
import { defaultTtsModelOptions } from "./options.js";
import { handleCreateAudio } from "./helpers/panel.js";

function AudioDetailEdit({
    panelId,
    transcriptData,
    taskStatus,
    initiatePolling,
    visible
}) {
    const [ttsModel, setTtsModel] = useState("elevenlabs");
    const [defaultVoiceQuestion, setDefaultVoiceQuestion] = useState("");
    const [defaultVoiceAnswer, setDefaultVoiceAnswer] = useState("");
    const [transcriptId, setTranscriptId] = useState(null);

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
        <Form onSubmit={handleAudioSubmit}>
            <Accordion defaultActiveKey={visible ? "0" : null}>
                <Accordion.Item eventKey="0">
                    <Accordion.Header>Create Audio</Accordion.Header>
                    <Accordion.Body>
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
                        <div className="flex gap-4">
                            <Form.Group controlId="ttsModel" className="flex-1">
                                <Form.Label className="font-semibold">
                                    TTS Model:
                                </Form.Label>
                                <Form.Control
                                    as="select"
                                    value={
                                        ttsModel ||
                                        defaultTtsModelOptions[0].value
                                    }
                                    onChange={(e) =>
                                        setTtsModel(e.target.value)
                                    }
                                    className="w-full"
                                >
                                    {defaultTtsModelOptions.map((model) => (
                                        <option
                                            value={model.value}
                                            key={model.value}
                                            disabled={
                                                model.disabled
                                                    ? true
                                                    : undefined
                                            }
                                        >
                                            {model.label}
                                        </option>
                                    ))}
                                </Form.Control>
                            </Form.Group>
                            <Form.Group
                                controlId="defaultVoiceQuestion"
                                className="flex-1"
                            >
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
                            <Form.Group
                                controlId="defaultVoiceAnswer"
                                className="flex-1"
                            >
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
                        </div>
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
                    </Accordion.Body>
                </Accordion.Item>
            </Accordion>
        </Form>
    );
}

export default AudioDetailEdit;
