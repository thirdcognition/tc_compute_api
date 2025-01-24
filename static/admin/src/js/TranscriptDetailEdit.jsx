import { useState, useEffect } from "react";
import { handleCreateTranscript } from "./helpers/panel.js";
import { Form, Button } from "react-bootstrap";
import {
    conversationStyleOptions,
    rolesPerson1Options,
    rolesPerson2Options,
    dialogueStructureOptions,
    engagementTechniquesOptions,
    outputLanguageOptions
} from "./options.js";
import { formatUpdateCycle, getWordCountDescription } from "./helpers/ui.js";

function TranscriptDetailEdit({
    panelId,
    discussionData,
    taskStatus,
    initiatePolling
}) {
    const [showDetails, setShowDetails] = useState(false);
    const [wordCount, setWordCount] = useState(2500);
    const [maxWordCount, setMaxWordCount] = useState(20000); // Dynamically updated max
    const [duration, setDuration] = useState(20); // Duration in minutes
    const [creativity] = useState(0.7);
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

    // Utility function to calculate article count
    const calculateArticleCount = (data) => {
        const linksArray = data?.metadata?.input_source || [];
        const googleNewsArray = data?.metadata?.google_news || [];
        const yleNewsArray = data?.metadata?.yle_news || [];
        const techCrunchNewsArray = data?.metadata?.techcrunch_news || [];
        const hackerNewsArray = data?.metadata?.hackernews || [];
        const newsSources = [
            googleNewsArray,
            yleNewsArray,
            techCrunchNewsArray,
            hackerNewsArray
        ];
        let totalArticles = 0;
        newsSources.forEach((sourceArray) => {
            totalArticles +=
                sourceArray.reduce((val, config) => val + config.articles, 0) ||
                0;
        });
        return Math.max(totalArticles + linksArray.length, 1);
    };

    // Effect to update maxWordCount and duration based on article count
    useEffect(() => {
        if (discussionData) {
            const articleCount = calculateArticleCount(discussionData);
            const newMaxWordCount = articleCount * 500;
            setMaxWordCount(newMaxWordCount);
            setDuration(newMaxWordCount / 500); // Calculate duration
            if (wordCount > newMaxWordCount) {
                setWordCount(newMaxWordCount); // Adjust wordCount if it exceeds max
            }
        }
    }, [discussionData, wordCount]);

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

    return (
        <>
            <div className="transcript-container border p-3 mb-4 rounded">
                <h3 className="font-bold mb-3">Create Transcript</h3>
                <Form onSubmit={handleTranscriptSubmit}>
                    <Form.Group controlId="updateCycle" className="mb-4">
                        <Form.Label className="font-semibold">
                            Update Cycle:
                        </Form.Label>
                        <Form.Control
                            type="range"
                            min={0}
                            max={3600 * 24 * 14}
                            step={3600}
                            value={updateCycle}
                            onChange={(e) =>
                                setUpdateCycle(Number(e.target.value))
                            }
                            className="w-full"
                        />
                        <div className="mt-2">
                            {formatUpdateCycle(updateCycle)}
                        </div>
                    </Form.Group>
                    <Form.Group controlId="wordCount" className="mb-4">
                        <Form.Label className="font-semibold">
                            Requested length (up to around {duration.toFixed(0)}{" "}
                            min):
                        </Form.Label>
                        <Form.Control
                            type="range"
                            min={100}
                            max={maxWordCount}
                            step={100}
                            value={wordCount}
                            onChange={(e) => setWordCount(e.target.value)}
                            className="w-full"
                        />
                        <div>
                            {getWordCountDescription(wordCount, maxWordCount)}
                        </div>
                    </Form.Group>
                    {/* <Form.Group controlId="creativity" className="mb-4">
                        <Form.Label className="font-semibold">
                            Creativity:
                        </Form.Label>
                        <Form.Control
                            type="range"
                            min={0}
                            max={1}
                            step={0.1}
                            value={creativity}
                            onChange={(e) => setCreativity(e.target.value)}
                            className="w-full"
                        />
                        <div>{`${creativity}`}</div>
                    </Form.Group> */}
                    <Form.Group controlId="longForm" className="mb-4">
                        <div className="flex items-center mb-2.5">
                            <label className="mr-2.5">
                                <input
                                    type="checkbox"
                                    checked={longForm}
                                    onChange={(e) =>
                                        setLongForm(e.target.checked)
                                    }
                                />
                                {
                                    " Process every article separately. (higher quality, longer process time)"
                                }
                            </label>
                        </div>
                    </Form.Group>
                    <Button
                        onClick={() => setShowDetails(!showDetails)}
                        className="w-full py-2 mb-4 flex items-center justify-center bg-blue-500 text-white rounded"
                    >
                        <span className="mr-2">{showDetails ? "▼" : "▶"}</span>
                        <span>
                            {showDetails ? "Hide Details" : "Show More Details"}
                        </span>
                    </Button>
                    {showDetails && (
                        <div className="border p-3 mb-4 rounded">
                            <>
                                <Form.Group
                                    controlId="conversationStyle"
                                    className="mb-4"
                                >
                                    <Form.Label className="font-semibold">
                                        Conversation Style:
                                    </Form.Label>
                                    <Form.Control
                                        as="select"
                                        multiple
                                        value={conversationStyle}
                                        onChange={(e) =>
                                            setConversationStyle(
                                                [
                                                    ...e.target.selectedOptions
                                                ].map((option) => option.value)
                                            )
                                        }
                                        className="w-full h-40"
                                    >
                                        {conversationStyleOptions.map(
                                            (style) => (
                                                <option
                                                    value={style}
                                                    key={style}
                                                >
                                                    {style}
                                                </option>
                                            )
                                        )}
                                    </Form.Control>
                                </Form.Group>
                                <Form.Group
                                    controlId="rolesPerson1"
                                    className="mb-4"
                                >
                                    <Form.Label className="font-semibold">
                                        Role for Person 1:
                                    </Form.Label>
                                    <Form.Control
                                        as="select"
                                        value={rolesPerson1}
                                        onChange={(e) =>
                                            setRolesPerson1(e.target.value)
                                        }
                                        className="w-full"
                                    >
                                        {rolesPerson1Options.map((role) => (
                                            <option value={role} key={role}>
                                                {role}
                                            </option>
                                        ))}
                                    </Form.Control>
                                </Form.Group>
                                <Form.Group
                                    controlId="rolesPerson2"
                                    className="mb-4"
                                >
                                    <Form.Label className="font-semibold">
                                        Role for Person 2:
                                    </Form.Label>
                                    <Form.Control
                                        as="select"
                                        value={rolesPerson2}
                                        onChange={(e) =>
                                            setRolesPerson2(e.target.value)
                                        }
                                        className="w-full"
                                    >
                                        {rolesPerson2Options.map((role) => (
                                            <option value={role} key={role}>
                                                {role}
                                            </option>
                                        ))}
                                    </Form.Control>
                                </Form.Group>
                                <Form.Group
                                    controlId="dialogueStructure"
                                    className="mb-4"
                                >
                                    <Form.Label className="font-semibold">
                                        Dialogue Structure:
                                    </Form.Label>
                                    <div className="dialogue-structure-container">
                                        {dialogueStructure.map(
                                            (structure, index) => (
                                                <div
                                                    key={index}
                                                    className="dialogue-item flex items-center mb-2"
                                                >
                                                    <Form.Control
                                                        as="select"
                                                        value={structure}
                                                        onChange={(e) => {
                                                            const newStructure =
                                                                [
                                                                    ...dialogueStructure
                                                                ];
                                                            newStructure[
                                                                index
                                                            ] = e.target.value;
                                                            setDialogueStructure(
                                                                newStructure
                                                            );
                                                        }}
                                                        className="flex-grow mr-2"
                                                    >
                                                        {dialogueStructureOptions.map(
                                                            (option) => (
                                                                <option
                                                                    value={
                                                                        option
                                                                    }
                                                                    key={option}
                                                                >
                                                                    {option}
                                                                </option>
                                                            )
                                                        )}
                                                    </Form.Control>
                                                    <Button
                                                        variant="danger"
                                                        onClick={() => {
                                                            const newStructure =
                                                                dialogueStructure.filter(
                                                                    (_, i) =>
                                                                        i !==
                                                                        index
                                                                );
                                                            setDialogueStructure(
                                                                newStructure
                                                            );
                                                        }}
                                                        className="remove-item-button"
                                                    >
                                                        ✖
                                                    </Button>
                                                </div>
                                            )
                                        )}
                                        <Button
                                            onClick={() =>
                                                setDialogueStructure([
                                                    ...dialogueStructure,
                                                    ""
                                                ])
                                            }
                                            className="add-item-button mt-2"
                                        >
                                            Add Item
                                        </Button>
                                    </div>
                                </Form.Group>
                                <Form.Group
                                    controlId="engagementTechniques"
                                    className="mb-4"
                                >
                                    <Form.Label className="font-semibold">
                                        Engagement Techniques:
                                    </Form.Label>
                                    <Form.Control
                                        as="select"
                                        multiple
                                        value={engagementTechniques}
                                        onChange={(e) =>
                                            setEngagementTechniques(
                                                [
                                                    ...e.target.selectedOptions
                                                ].map((option) => option.value)
                                            )
                                        }
                                        className="w-full h-40"
                                    >
                                        {engagementTechniquesOptions.map(
                                            (technique) => (
                                                <option
                                                    value={technique}
                                                    key={technique}
                                                >
                                                    {technique}
                                                </option>
                                            )
                                        )}
                                    </Form.Control>
                                </Form.Group>
                                <Form.Group
                                    controlId="userInstructions"
                                    className="mb-4"
                                >
                                    <Form.Label className="font-semibold">
                                        User Instructions:
                                    </Form.Label>
                                    <Form.Control
                                        type="text"
                                        placeholder="Provide specific instructions here..."
                                        value={userInstructions}
                                        onChange={(e) =>
                                            setUserInstructions(e.target.value)
                                        }
                                        className="w-full"
                                    />
                                </Form.Group>
                                <Form.Group
                                    controlId="outputLanguage"
                                    className="mb-4"
                                >
                                    <Form.Label className="font-semibold">
                                        Output Language (Note: Selected voice
                                        models should align with the language):
                                    </Form.Label>
                                    <Form.Control
                                        as="select"
                                        value={outputLanguage}
                                        onChange={(e) =>
                                            setOutputLanguage(e.target.value)
                                        }
                                        className="w-full"
                                    >
                                        {outputLanguageOptions.map(
                                            (language) => (
                                                <option
                                                    value={language}
                                                    key={language}
                                                >
                                                    {language}
                                                </option>
                                            )
                                        )}
                                    </Form.Control>
                                </Form.Group>
                            </>
                        </div>
                    )}
                    <Button
                        variant="primary"
                        type="submit"
                        className="w-full py-2 mt-3"
                        disabled={
                            !panelId ||
                            (taskStatus !== "idle" &&
                                taskStatus !== "failure" &&
                                taskStatus !== "success")
                        }
                    >
                        Create Transcript
                    </Button>
                </Form>
            </div>
        </>
    );
}

export default TranscriptDetailEdit;
