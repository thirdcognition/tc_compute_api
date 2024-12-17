// TextToSpeechConfig.js
const { useState } = React;
const { Form, Button } = ReactBootstrap;
import { defaultTtsModelOptions } from "./options.js";

function TextToSpeechConfig({
    ttsModel,
    setTtsModel,
    defaultVoiceQuestion,
    setDefaultVoiceQuestion,
    defaultVoiceAnswer,
    setDefaultVoiceAnswer
}) {
    const [showDetails, setShowDetails] = useState(false);

    return React.createElement(
        React.Fragment,
        null,
        React.createElement(
            Form.Group,
            { controlId: "ttsModel" },
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
                className: "w-full py-2 mb-4 flex items-center" // Updated button styling to match
            },
            React.createElement(
                "span",
                { className: "mr-2" },
                showDetails ? "▼" : "▶"
            ), // UML caret symbols with spacing
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
                        placeholder: "Enter default voice for questions...",
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
                        placeholder: "Enter default voice for answers...",
                        value: defaultVoiceAnswer,
                        onChange: (e) => setDefaultVoiceAnswer(e.target.value),
                        className: "w-full"
                    })
                )
            )
    );
}

export default TextToSpeechConfig;
