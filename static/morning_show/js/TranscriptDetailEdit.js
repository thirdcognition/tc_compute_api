// TranscriptDetailEdit.js
const { useState } = React;
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
    wordCount,
    setWordCount,
    creativity,
    setCreativity,
    conversationStyle,
    setConversationStyle,
    rolesPerson1,
    setRolesPerson1,
    rolesPerson2,
    setRolesPerson2,
    dialogueStructure,
    setDialogueStructure,
    engagementTechniques,
    setEngagementTechniques,
    userInstructions,
    setUserInstructions,
    outputLanguage,
    setOutputLanguage
}) {
    const [showDetails, setShowDetails] = useState(false);

    return React.createElement(
        React.Fragment,
        null,
        React.createElement(
            Form.Group,
            { controlId: "wordCount", className: "mb-4" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Word Count (~1 min per 100 words):"
            ),
            React.createElement(Form.Control, {
                type: "range",
                min: 100,
                max: 2000,
                step: 100,
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
            Button,
            {
                onClick: () => setShowDetails(!showDetails),
                className: "w-full py-2 mb-4 flex items-center" // Styled button
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
                "div",
                { className: "border p-3 mb-4 rounded" }, // Container without transition
                React.createElement(
                    React.Fragment,
                    null,
                    React.createElement(
                        Form.Group,
                        { controlId: "conversationStyle", className: "mb-4" },
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
                                        [...e.target.selectedOptions].map(
                                            (option) => option.value
                                        )
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
                        { controlId: "rolesPerson1", className: "mb-4" },
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
                        { controlId: "rolesPerson2", className: "mb-4" },
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
                        { controlId: "dialogueStructure", className: "mb-4" },
                        React.createElement(
                            Form.Label,
                            { className: "font-semibold" },
                            "Dialogue Structure:"
                        ),
                        React.createElement(
                            "div",
                            { className: "dialogue-structure-container" },
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
                                        dialogueStructureOptions.map((option) =>
                                            React.createElement(
                                                "option",
                                                { value: option, key: option },
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
                                                        (_, i) => i !== index
                                                    );
                                                setDialogueStructure(
                                                    newStructure
                                                );
                                            },
                                            className: "remove-item-button"
                                        },
                                        "✖" // UML symbol for remove
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
                                        [...e.target.selectedOptions].map(
                                            (option) => option.value
                                        )
                                    ),
                                className: "w-full h-40"
                            },
                            engagementTechniquesOptions.map((technique) =>
                                React.createElement(
                                    "option",
                                    { value: technique, key: technique },
                                    technique
                                )
                            )
                        )
                    ),
                    React.createElement(
                        Form.Group,
                        { controlId: "userInstructions", className: "mb-4" },
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
                        { controlId: "outputLanguage", className: "mb-4" },
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
            )
    );
}

export default TranscriptDetailEdit;
