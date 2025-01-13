// TranscriptDetailEdit.js
const { useState } = React;
import { handleCreateTranscript } from "./helpers/panel.js";
const { Form, Button } = ReactBootstrap;
import {
    conversationStyleOptions,
    rolesPerson1Options,
    rolesPerson2Options,
    dialogueStructureOptions,
    engagementTechniquesOptions,
    outputLanguageOptions
} from "./options.js";

function TranscriptDetailEdit({
    panelId,
    discussionData,
    taskStatus,
    initiatePolling
}) {
    const [showDetails, setShowDetails] = useState(false);
    const [wordCount, setWordCount] = useState(200);
    const [creativity, setCreativity] = useState(1);
    const [conversationStyle, setConversationStyle] = useState([
        "engaging",
        "fast-paced",
        "enthusiastic"
    ]);
    const [rolesPerson1, setRolesPerson1] = useState("main summarizer");
    const [rolesPerson2, setRolesPerson2] = useState("questioner/clarifier");
    const [dialogueStructure, setDialogueStructure] = useState([
        "Introduction",
        "Main Content Summary",
        "Conclusion"
    ]);
    const [engagementTechniques, setEngagementTechniques] = useState([
        "rhetorical questions",
        "anecdotes",
        "analogies",
        "humor"
    ]);
    const [userInstructions, setUserInstructions] = useState("");
    const [outputLanguage, setOutputLanguage] = useState("English");
    const [updateCycle, setUpdateCycle] = useState(0); // Default to 0 if not defined
    const [longForm, setLongForm] = useState(false);

    const formatUpdateCycle = (seconds) => {
        if (seconds === 0) return "Not set";
        const days = Math.floor(seconds / (24 * 3600));
        const hours = (seconds % (24 * 3600)) / 3600;
        return `${days}d ${hours}h`;
    };

    const handleTranscriptSubmit = async (e) => {
        e.preventDefault();
        if (panelId) {
            handleCreateTranscript({
                panelId,
                discussionData,
                wordCount,
                creativity,
                conversationStyle,
                rolesPerson1,
                rolesPerson2,
                dialogueStructure,
                engagementTechniques,
                userInstructions,
                outputLanguage,
                longForm,
                updateCycle
            }).then(({ taskId, success }) => {
                if (success && taskId) {
                    initiatePolling(taskId, "transcript");
                }
            });
        }
    };

    return React.createElement(
        React.Fragment,
        null,
        React.createElement(
            "div",
            { className: "transcript-container border p-3 mb-4 rounded" },
            React.createElement(
                "h3",
                { className: "font-bold mb-3" },
                "Create Transcript"
            ),
            React.createElement(
                Form,
                { onSubmit: handleTranscriptSubmit },
                React.createElement(
                    Form.Group,
                    { controlId: "updateCycle", className: "mb-4" },
                    React.createElement(
                        Form.Label,
                        { className: "font-semibold" },
                        "Update Cycle:"
                    ),
                    React.createElement(Form.Control, {
                        type: "range",
                        min: 0,
                        max: 3600,
                        step: 180,
                        value: updateCycle,
                        onChange: (e) => setUpdateCycle(Number(e.target.value)),
                        className: "w-full"
                    }),
                    React.createElement(
                        "div",
                        { className: "mt-2" },
                        formatUpdateCycle(updateCycle)
                    )
                ),
                React.createElement(
                    Form.Group,
                    { controlId: "wordCount", className: "mb-4" },
                    React.createElement(
                        Form.Label,
                        { className: "font-semibold" },
                        "Requested Word Count (~1 min per 100 words):"
                    ),
                    React.createElement(Form.Control, {
                        type: "range",
                        min: 50,
                        max: 10000,
                        step: 50,
                        value: wordCount,
                        onChange: (e) => setWordCount(e.target.value),
                        className: "w-full"
                    }),
                    React.createElement("div", null, `${wordCount} words`)
                ),
                React.createElement(
                    Form.Group,
                    { controlId: "creativity", className: "mb-4" },
                    React.createElement(
                        Form.Label,
                        { className: "font-semibold" },
                        "Creativity:"
                    ),
                    React.createElement(Form.Control, {
                        type: "range",
                        min: 0,
                        max: 1,
                        step: 0.1,
                        value: creativity,
                        onChange: (e) => setCreativity(e.target.value),
                        className: "w-full"
                    }),
                    React.createElement("div", null, `${creativity}`)
                ),
                React.createElement(
                    Form.Group,
                    { controlId: "longForm", className: "mb-4" },
                    React.createElement(
                        "div",
                        {
                            style: {
                                display: "flex",
                                alignItems: "center",
                                marginBottom: "10px"
                            }
                        },
                        React.createElement(
                            "label",
                            { style: { marginRight: "10px" } },
                            React.createElement("input", {
                                type: "checkbox",
                                checked: longForm,
                                onChange: (e) => setLongForm(e.target.checked)
                            }),
                            " Long Form"
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
                        "div",
                        { className: "border p-3 mb-4 rounded" },
                        React.createElement(
                            React.Fragment,
                            null,
                            React.createElement(
                                Form.Group,
                                {
                                    controlId: "conversationStyle",
                                    className: "mb-4"
                                },
                                React.createElement(
                                    Form.Label,
                                    { className: "font-semibold" },
                                    "Conversation Style:"
                                ),
                                React.createElement(
                                    Form.Control,
                                    {
                                        as: "select",
                                        multiple: true,
                                        value: conversationStyle,
                                        onChange: (e) =>
                                            setConversationStyle(
                                                [
                                                    ...e.target.selectedOptions
                                                ].map((option) => option.value)
                                            ),
                                        className: "w-full h-40"
                                    },
                                    conversationStyleOptions.map((style) =>
                                        React.createElement(
                                            "option",
                                            { value: style, key: style },
                                            style
                                        )
                                    )
                                )
                            ),
                            React.createElement(
                                Form.Group,
                                {
                                    controlId: "rolesPerson1",
                                    className: "mb-4"
                                },
                                React.createElement(
                                    Form.Label,
                                    { className: "font-semibold" },
                                    "Role for Person 1:"
                                ),
                                React.createElement(
                                    Form.Control,
                                    {
                                        as: "select",
                                        value: rolesPerson1,
                                        onChange: (e) =>
                                            setRolesPerson1(e.target.value),
                                        className: "w-full"
                                    },
                                    rolesPerson1Options.map((role) =>
                                        React.createElement(
                                            "option",
                                            { value: role, key: role },
                                            role
                                        )
                                    )
                                )
                            ),
                            React.createElement(
                                Form.Group,
                                {
                                    controlId: "rolesPerson2",
                                    className: "mb-4"
                                },
                                React.createElement(
                                    Form.Label,
                                    { className: "font-semibold" },
                                    "Role for Person 2:"
                                ),
                                React.createElement(
                                    Form.Control,
                                    {
                                        as: "select",
                                        value: rolesPerson2,
                                        onChange: (e) =>
                                            setRolesPerson2(e.target.value),
                                        className: "w-full"
                                    },
                                    rolesPerson2Options.map((role) =>
                                        React.createElement(
                                            "option",
                                            { value: role, key: role },
                                            role
                                        )
                                    )
                                )
                            ),
                            React.createElement(
                                Form.Group,
                                {
                                    controlId: "dialogueStructure",
                                    className: "mb-4"
                                },
                                React.createElement(
                                    Form.Label,
                                    { className: "font-semibold" },
                                    "Dialogue Structure:"
                                ),
                                React.createElement(
                                    "div",
                                    {
                                        className:
                                            "dialogue-structure-container"
                                    },
                                    dialogueStructure.map((structure, index) =>
                                        React.createElement(
                                            "div",
                                            {
                                                key: index,
                                                className:
                                                    "dialogue-item flex items-center mb-2"
                                            },
                                            React.createElement(
                                                Form.Control,
                                                {
                                                    as: "select",
                                                    value: structure,
                                                    onChange: (e) => {
                                                        const newStructure = [
                                                            ...dialogueStructure
                                                        ];
                                                        newStructure[index] =
                                                            e.target.value;
                                                        setDialogueStructure(
                                                            newStructure
                                                        );
                                                    },
                                                    className: "flex-grow mr-2"
                                                },
                                                dialogueStructureOptions.map(
                                                    (option) =>
                                                        React.createElement(
                                                            "option",
                                                            {
                                                                value: option,
                                                                key: option
                                                            },
                                                            option
                                                        )
                                                )
                                            ),
                                            React.createElement(
                                                Button,
                                                {
                                                    variant: "danger",
                                                    onClick: () => {
                                                        const newStructure =
                                                            dialogueStructure.filter(
                                                                (_, i) =>
                                                                    i !== index
                                                            );
                                                        setDialogueStructure(
                                                            newStructure
                                                        );
                                                    },
                                                    className:
                                                        "remove-item-button"
                                                },
                                                "✖"
                                            )
                                        )
                                    ),
                                    React.createElement(
                                        Button,
                                        {
                                            onClick: () =>
                                                setDialogueStructure([
                                                    ...dialogueStructure,
                                                    ""
                                                ]),
                                            className: "add-item-button mt-2"
                                        },
                                        "Add Item"
                                    )
                                )
                            ),
                            React.createElement(
                                Form.Group,
                                {
                                    controlId: "engagementTechniques",
                                    className: "mb-4"
                                },
                                React.createElement(
                                    Form.Label,
                                    { className: "font-semibold" },
                                    "Engagement Techniques:"
                                ),
                                React.createElement(
                                    Form.Control,
                                    {
                                        as: "select",
                                        multiple: true,
                                        value: engagementTechniques,
                                        onChange: (e) =>
                                            setEngagementTechniques(
                                                [
                                                    ...e.target.selectedOptions
                                                ].map((option) => option.value)
                                            ),
                                        className: "w-full h-40"
                                    },
                                    engagementTechniquesOptions.map(
                                        (technique) =>
                                            React.createElement(
                                                "option",
                                                {
                                                    value: technique,
                                                    key: technique
                                                },
                                                technique
                                            )
                                    )
                                )
                            ),
                            React.createElement(
                                Form.Group,
                                {
                                    controlId: "userInstructions",
                                    className: "mb-4"
                                },
                                React.createElement(
                                    Form.Label,
                                    { className: "font-semibold" },
                                    "User Instructions:"
                                ),
                                React.createElement(Form.Control, {
                                    type: "text",
                                    placeholder:
                                        "Provide specific instructions here...",
                                    value: userInstructions,
                                    onChange: (e) =>
                                        setUserInstructions(e.target.value),
                                    className: "w-full"
                                })
                            ),
                            React.createElement(
                                Form.Group,
                                {
                                    controlId: "outputLanguage",
                                    className: "mb-4"
                                },
                                React.createElement(
                                    Form.Label,
                                    { className: "font-semibold" },
                                    "Output Language (Note: Selected voice models should align with the language):"
                                ),
                                React.createElement(
                                    Form.Control,
                                    {
                                        as: "select",
                                        value: outputLanguage,
                                        onChange: (e) =>
                                            setOutputLanguage(e.target.value),
                                        className: "w-full"
                                    },
                                    outputLanguageOptions.map((language) =>
                                        React.createElement(
                                            "option",
                                            { value: language, key: language },
                                            language
                                        )
                                    )
                                )
                            )
                        )
                    ),
                React.createElement(
                    Button,
                    {
                        variant: "primary",
                        type: "submit",
                        className: "w-full py-2 mt-3",
                        disabled:
                            !panelId ||
                            (taskStatus !== "idle" &&
                                taskStatus !== "failure" &&
                                taskStatus !== "success")
                    },
                    "Create Transcript"
                )
            )
        )
    );
}

export default TranscriptDetailEdit;
