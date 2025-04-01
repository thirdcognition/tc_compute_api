import { useState, useEffect } from "react";
import { FaTimes } from "react-icons/fa";
import { Form, Button, Accordion, Card } from "react-bootstrap";
import { defaultTtsModelOptions, outputLanguageOptions } from "./options.js";
import { handleCreateAudio } from "./helpers/panel.js";

function AudioDetailEdit({
    panelId,
    transcriptData,
    taskStatus,
    initiatePolling,
    visible,
    returnData
}) {
    const [ttsModel, setTtsModel] = useState("elevenlabs");
    const [defaultVoiceQuestion, setDefaultVoiceQuestion] = useState("");
    const [defaultVoiceAnswer, setDefaultVoiceAnswer] = useState("");
    const [transcriptId, setTranscriptId] = useState(null);
    const [languageDetails, setLanguageDetails] = useState({});
    const [selectedLanguage, setSelectedLanguage] = useState("");

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
            setTranscript(transcriptData[0].id);
        }
    }, [transcriptData]);

    const setTranscript = (_transcriptId) => {
        const matchedTranscript = transcriptData.find(
            (transcript) => transcript.id === _transcriptId
        );
        if (matchedTranscript) {
            setTranscriptId(matchedTranscript.id);
            const metadata = matchedTranscript.metadata;
            if (metadata.tts_model) {
                setTtsModel(metadata.tts_model);
                if (
                    metadata.conversation_config &&
                    metadata.conversation_config.text_to_speech &&
                    metadata.conversation_config.text_to_speech[
                        metadata.tts_model
                    ]
                ) {
                    const tts = metadata.conversation_config.text_to_speech;
                    const defaults = tts[metadata.tts_model];
                    const availLangs = Object.keys(outputLanguageOptions);
                    const languages = Object.keys(tts)
                        .filter((key) => availLangs.includes(key))
                        .reduce((obj, key) => {
                            obj[key] = tts[key];
                            return obj;
                        }, {});
                    setDefaultVoiceAnswer(defaults.default_voices.answer);
                    setDefaultVoiceQuestion(defaults.default_voices.question);
                    setLanguageDetails(languages);
                }
            } else {
                setTtsModel("elevenlabs");
                setDefaultVoiceQuestion("");
                setDefaultVoiceAnswer("");
                setLanguageDetails({});
            }
        }
    };

    useEffect(() => {
        if (!ttsModel) {
            setTtsModel(defaultTtsModelOptions[0].value);
        }
    }, [ttsModel]);

    const handleAddLanguage = () => {
        if (selectedLanguage && !languageDetails[selectedLanguage]) {
            setLanguageDetails((prev) => ({
                ...prev,
                [selectedLanguage]: { question: "", answer: "" }
            }));
        }
    };

    const handleRemoveLanguage = (language) => {
        setLanguageDetails((prev) => {
            const updated = { ...prev };
            delete updated[language];
            return updated;
        });
        // }
    };

    const handleLanguageChange = (language, field, value) => {
        setLanguageDetails((prev) => ({
            ...prev,
            [language]: { ...prev[language], [field]: value }
        }));
    };

    const handleAudioSubmit = async (e) => {
        e.preventDefault();
        if (returnData) {
            returnData({
                ttsModel,
                defaultVoiceQuestion,
                defaultVoiceAnswer,
                languages: languageDetails
            });
        } else {
            if (!transcriptId) {
                console.error("Transcript ID is not selected.");
                return;
            }
            // console.log("PanelId", panelId, "TranscriptId", transcriptId);
            if (panelId && transcriptId) {
                handleCreateAudio({
                    panelId,
                    transcriptId,
                    ttsModel,
                    defaultVoiceQuestion,
                    defaultVoiceAnswer,
                    languages: languageDetails
                }).then(({ taskId, success }) => {
                    if (success && taskId) {
                        initiatePolling(taskId, "audio");
                    }
                });
            }
        }
    };

    return (
        <Form onSubmit={handleAudioSubmit}>
            <Accordion defaultActiveKey={visible ? "0" : null}>
                <Accordion.Item eventKey="0">
                    <Accordion.Header>
                        {transcriptData ? "Create Audio" : "Select voices"}
                    </Accordion.Header>
                    <Accordion.Body>
                        {transcriptData && transcriptData.length > 1 && (
                            <>
                                <Card className="mb-4">
                                    <Card.Body>
                                        <Card.Title className="font-bold text-lg">
                                            Select Transcript
                                        </Card.Title>

                                        <select
                                            id="transcriptSelect"
                                            value={transcriptId}
                                            onChange={(e) =>
                                                setTranscript(e.target.value)
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
                                                .map((transcript, index) => (
                                                    <option
                                                        key={transcript.id}
                                                        value={transcript.id}
                                                    >
                                                        Transcript{" "}
                                                        {transcriptData.length -
                                                            index}
                                                        : {transcript.title}
                                                    </option>
                                                ))}
                                        </select>
                                    </Card.Body>
                                </Card>
                            </>
                        )}
                        <Card className="mb-4">
                            <Card.Body>
                                <Card.Title className="font-bold text-lg">
                                    TTS Model:
                                </Card.Title>
                                <Form.Group
                                    controlId="ttsModel"
                                    className="flex-1"
                                >
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
                            </Card.Body>
                        </Card>

                        <Card className="mb-4">
                            <Card.Body>
                                <Card.Title className="font-bold text-lg">
                                    Default Voices
                                </Card.Title>
                                <div className="d-flex gap-3">
                                    <Form.Group
                                        controlId="defaultVoiceQuestion"
                                        className="flex-grow-1"
                                    >
                                        <Form.Label>Question:</Form.Label>
                                        <Form.Control
                                            type="text"
                                            placeholder="Enter default voice for questions..."
                                            value={defaultVoiceQuestion}
                                            onChange={(e) =>
                                                setDefaultVoiceQuestion(
                                                    e.target.value
                                                )
                                            }
                                            className="w-full"
                                        />
                                    </Form.Group>
                                    <Form.Group
                                        controlId="defaultVoiceAnswer"
                                        className="flex-grow-1"
                                    >
                                        <Form.Label>Answer:</Form.Label>
                                        <Form.Control
                                            type="text"
                                            placeholder="Enter default voice for answers..."
                                            value={defaultVoiceAnswer}
                                            onChange={(e) =>
                                                setDefaultVoiceAnswer(
                                                    e.target.value
                                                )
                                            }
                                            className="w-full"
                                        />
                                    </Form.Group>
                                </div>
                            </Card.Body>
                        </Card>

                        {Object.entries(languageDetails).map(
                            ([language, details]) => (
                                <Card key={language} className="mb-4">
                                    <Card.Body>
                                        <Card.Title className="font-bold text-lg">
                                            {language}
                                            <Button
                                                variant="danger"
                                                className="mt-3 absolute right-2 -top-2"
                                                onClick={() =>
                                                    handleRemoveLanguage(
                                                        language
                                                    )
                                                }
                                            >
                                                <FaTimes className="inline-block" />
                                            </Button>
                                        </Card.Title>
                                        <div className="d-flex gap-3">
                                            <Form.Group
                                                controlId={`voiceQuestion-${language}`}
                                                className="flex-grow-1"
                                            >
                                                <Form.Label>
                                                    Question:
                                                </Form.Label>
                                                <Form.Control
                                                    type="text"
                                                    placeholder="Enter voice for questions..."
                                                    value={details.question}
                                                    onChange={(e) =>
                                                        handleLanguageChange(
                                                            language,
                                                            "question",
                                                            e.target.value
                                                        )
                                                    }
                                                    className="w-full"
                                                />
                                            </Form.Group>
                                            <Form.Group
                                                controlId={`voiceAnswer-${language}`}
                                                className="flex-grow-1"
                                            >
                                                <Form.Label>Answer:</Form.Label>
                                                <Form.Control
                                                    type="text"
                                                    placeholder="Enter voice for answers..."
                                                    value={details.answer}
                                                    onChange={(e) =>
                                                        handleLanguageChange(
                                                            language,
                                                            "answer",
                                                            e.target.value
                                                        )
                                                    }
                                                    className="w-full"
                                                />
                                            </Form.Group>
                                        </div>
                                    </Card.Body>
                                </Card>
                            )
                        )}
                        <Card className="mb-4">
                            <Card.Body>
                                <Card.Title className="font-bold text-lg">
                                    Add Language
                                </Card.Title>
                                <Form.Group controlId="languageSelect">
                                    <Form.Label>Select Language:</Form.Label>
                                    <Form.Control
                                        as="select"
                                        value={selectedLanguage}
                                        onChange={(e) =>
                                            setSelectedLanguage(e.target.value)
                                        }
                                    >
                                        <option value="">
                                            Select a language
                                        </option>
                                        {Object.entries(
                                            outputLanguageOptions
                                        ).map(([langId, language]) => (
                                            <option key={langId} value={langId}>
                                                {language}
                                            </option>
                                        ))}
                                    </Form.Control>
                                </Form.Group>
                                <Button
                                    variant="secondary"
                                    className="mt-2"
                                    onClick={handleAddLanguage}
                                >
                                    Add Language
                                </Button>
                            </Card.Body>
                        </Card>
                        {transcriptData && (
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
                        )}
                        {returnData && (
                            <Button
                                onClick={handleAudioSubmit}
                                className="w-full py-2 mt-3"
                            >
                                Save
                            </Button>
                        )}
                    </Accordion.Body>
                </Accordion.Item>
            </Accordion>
        </Form>
    );
}

export default AudioDetailEdit;
