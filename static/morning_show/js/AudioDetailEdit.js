// AudioDetailEdit.js
const { useState, useEffect } = React;
const { Form, Button } = ReactBootstrap;
import { defaultTtsModelOptions } from "./options.js";
import { handleCreateAudio } from "./helpers/panel.js";

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
        if (transcriptData && transcriptData.length === 1) {
            setTranscriptId(transcriptData[0].id);
        }
    }, [transcriptData]);

    const handleAudioSubmit = async (e) => {
        e.preventDefault();
        if (panelId && transcriptId) {
            handleCreateAudio({
                panelId,
                transcriptId,
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

    return React.createElement(
        React.Fragment,
        null,
        React.createElement(
            "div",
            { className: "audio-container border p-3 mb-4 rounded" },
            React.createElement(
                "h3",
                { className: "font-bold mb-3" },
                "Create Audio"
            ),
            React.createElement(
                Form,
                { onSubmit: handleAudioSubmit },
                React.createElement(
                    "div",
                    { className: "mt-3" },
                    transcriptData &&
                        transcriptData.length > 1 &&
                        React.createElement(
                            "label",
                            { htmlFor: "transcriptSelect" },
                            "Select Transcript"
                        ),
                    transcriptData &&
                        transcriptData.length > 1 &&
                        React.createElement(
                            "select",
                            {
                                id: "transcriptSelect",
                                value: transcriptId || "",
                                onChange: (e) =>
                                    setTranscriptId(e.target.value),
                                className: "form-select"
                            },
                            transcriptData.map((transcript) =>
                                React.createElement(
                                    "option",
                                    {
                                        key: transcript.id,
                                        value: transcript.id
                                    },
                                    transcript.title
                                )
                            )
                        )
                ),
                React.createElement(
                    Form.Group,
                    { controlId: "ttsModel", className: "mb-3" },
                    React.createElement(
                        Form.Label,
                        { className: "font-semibold" },
                        "TTS Model:"
                    ),
                    React.createElement(
                        Form.Control,
                        {
                            as: "select",
                            value: ttsModel,
                            onChange: (e) => setTtsModel(e.target.value),
                            className: "w-full"
                        },
                        defaultTtsModelOptions.map((model) =>
                            React.createElement(
                                "option",
                                {
                                    value: model.value,
                                    key: model.value,
                                    disabled: model.disabled ? true : undefined
                                },
                                model.label
                            )
                        )
                    )
                ),
                React.createElement(
                    Button,
                    {
                        onClick: () => setShowDetails(!showDetails),
                        className: "w-full py-2 mb-4 flex items-center"
                    },
                    React.createElement(
                        "span",
                        { className: "mr-2" },
                        showDetails ? "▼" : "▶"
                    ),
                    React.createElement(
                        "span",
                        null,
                        showDetails ? "Hide Details" : "Show More Details"
                    )
                ),
                showDetails &&
                    React.createElement(
                        React.Fragment,
                        null,
                        React.createElement(
                            Form.Group,
                            { controlId: "defaultVoiceQuestion" },
                            React.createElement(
                                Form.Label,
                                { className: "font-semibold" },
                                "Default Voice for Question:"
                            ),
                            React.createElement(Form.Control, {
                                type: "text",
                                placeholder:
                                    "Enter default voice for questions...",
                                value: defaultVoiceQuestion,
                                onChange: (e) =>
                                    setDefaultVoiceQuestion(e.target.value),
                                className: "w-full"
                            })
                        ),
                        React.createElement(
                            Form.Group,
                            { controlId: "defaultVoiceAnswer" },
                            React.createElement(
                                Form.Label,
                                { className: "font-semibold" },
                                "Default Voice for Answer:"
                            ),
                            React.createElement(Form.Control, {
                                type: "text",
                                placeholder:
                                    "Enter default voice for answers...",
                                value: defaultVoiceAnswer,
                                onChange: (e) =>
                                    setDefaultVoiceAnswer(e.target.value),
                                className: "w-full"
                            })
                        )
                    ),
                React.createElement(
                    Button,
                    {
                        variant: "primary",
                        type: "submit",
                        className: "w-full py-2 mt-3",
                        disabled:
                            !transcriptData ||
                            (taskStatus !== "idle" &&
                                taskStatus !== "failure" &&
                                taskStatus !== "success")
                    },
                    "Create Audio"
                )
            )
        )
    );
}

export default AudioDetailEdit;
