import { useState, useEffect } from "react";
import { handleCreateTranscript } from "./helpers/panel.js";
import { Form, Card, Button, Accordion } from "react-bootstrap";
import {
    conversationStyleOptions,
    rolesPerson1Options,
    rolesPerson2Options,
    dialogueStructureOptions,
    engagementTechniquesOptions
} from "./options.js";
import { getWordCountDescription } from "./helpers/ui.js";
import CronjobComponent from "./components/CronjobComponent.jsx";
import { FaTimes } from "react-icons/fa";

function TranscriptDetailEdit({
    panelId,
    discussionData,
    taskStatus,
    initiatePolling,
    visible
}) {
    const [wordCount, setWordCount] = useState(1000);
    const [maxWordCount, setMaxWordCount] = useState(2500); // Dynamically updated max
    const [creativity] = useState(0.7);
    const [conversationStyle, setConversationStyle] = useState([
        "engaging",
        "fast-paced",
        "enthusiastic"
    ]);
    const [rolesPerson1, setRolesPerson1] = useState({
        name: "Elton",
        persona: "",
        role: "main summarizer"
    });
    const [rolesPerson2, setRolesPerson2] = useState({
        name: "Julia",
        persona: "",
        role: "questioner/clarifier"
    });
    const [dialogueStructure, setDialogueStructure] = useState([
        "Introduction",
        "Main Content Summary"
    ]);
    const [engagementTechniques, setEngagementTechniques] = useState([
        "rhetorical questions",
        "anecdotes",
        "analogies",
        "humor"
    ]);
    const [userInstructions, setUserInstructions] = useState("");
    const [outputLanguage, setOutputLanguage] = useState("English");
    const [cronjob, setCronjob] = useState(""); // Default to empty string if not defined
    const [longForm, setLongForm] = useState(false);

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
        return Math.max(
            totalArticles + linksArray.length,
            data?.metadata?.news_items || 1,
            1
        );
    };

    const updateMaxWordCount = () => {
        if (discussionData) {
            const articleCount = calculateArticleCount(discussionData);
            const newMaxWordCount =
                articleCount * (longForm || articleCount === 1 ? 500 : 300);
            setMaxWordCount(newMaxWordCount);
            if (wordCount > newMaxWordCount) {
                setWordCount(newMaxWordCount);
            }
        }
    };

    useEffect(updateMaxWordCount, [discussionData, wordCount, longForm]);

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
                cronjob
            }).then(({ taskId, success }) => {
                if (success && taskId) {
                    initiatePolling(taskId, "transcript");
                }
            });
        }
    };

    return (
        <>
            <Form onSubmit={handleTranscriptSubmit}>
                <Accordion defaultActiveKey={visible ? "0" : null}>
                    <Accordion.Item eventKey="0">
                        <Accordion.Header>Create Transcript</Accordion.Header>
                        <Accordion.Body>
                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title className="font-bold text-lg">
                                        Update Cycle:
                                    </Card.Title>
                                    <Form.Group controlId="cronjob">
                                        <CronjobComponent
                                            value={cronjob}
                                            onChange={setCronjob}
                                        />
                                    </Form.Group>
                                </Card.Body>
                            </Card>

                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title className="font-bold text-lg">
                                        Requested length:
                                    </Card.Title>
                                    <Form.Group controlId="wordCount">
                                        <Form.Control
                                            type="range"
                                            min={100}
                                            max={maxWordCount}
                                            step={100}
                                            value={wordCount}
                                            onChange={(e) =>
                                                setWordCount(e.target.value)
                                            }
                                            className="w-full"
                                        />
                                        <div>
                                            {getWordCountDescription(
                                                wordCount,
                                                maxWordCount
                                            )}
                                        </div>
                                    </Form.Group>
                                </Card.Body>
                            </Card>

                            {calculateArticleCount(discussionData) > 1 && (
                                <Card className="mb-4">
                                    <Card.Body>
                                        <Card.Title className="font-bold text-lg">
                                            Process Articles:
                                        </Card.Title>
                                        <Form.Group controlId="longForm">
                                            <div className="flex items-center mb-2.5">
                                                <label className="mr-2.5">
                                                    <input
                                                        type="checkbox"
                                                        checked={longForm}
                                                        onChange={(e) =>
                                                            setLongForm(
                                                                e.target.checked
                                                            )
                                                        }
                                                    />
                                                    {
                                                        " Process every article separately. (higher quality, longer process time)"
                                                    }
                                                </label>
                                            </div>
                                        </Form.Group>
                                    </Card.Body>
                                </Card>
                            )}

                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title className="font-bold text-lg">
                                        Conversation Style:
                                    </Card.Title>
                                    <Form.Group controlId="conversationStyle">
                                        <Form.Control
                                            as="select"
                                            multiple
                                            value={conversationStyle}
                                            onChange={(e) =>
                                                setConversationStyle(
                                                    [
                                                        ...e.target
                                                            .selectedOptions
                                                    ].map(
                                                        (option) => option.value
                                                    )
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
                                </Card.Body>
                            </Card>

                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title className="font-bold text-lg">
                                        Person 1
                                    </Card.Title>
                                    <Form.Group
                                        controlId="rolesPerson1Name"
                                        className="mb-3"
                                    >
                                        <Form.Label>Name:</Form.Label>
                                        <Form.Control
                                            type="text"
                                            value={rolesPerson1.name || "Elton"}
                                            onChange={(e) =>
                                                setRolesPerson1({
                                                    ...rolesPerson1,
                                                    name: e.target.value
                                                })
                                            }
                                            className="w-full"
                                        />
                                    </Form.Group>
                                    <Form.Group
                                        controlId="rolesPerson1Persona"
                                        className="mb-3"
                                    >
                                        <Form.Label>Persona:</Form.Label>
                                        <Form.Control
                                            type="text"
                                            value={rolesPerson1.persona || ""}
                                            onChange={(e) =>
                                                setRolesPerson1({
                                                    ...rolesPerson1,
                                                    persona: e.target.value
                                                })
                                            }
                                            className="w-full"
                                        />
                                    </Form.Group>
                                    <Form.Group
                                        controlId="rolesPerson1Role"
                                        className="mb-3"
                                    >
                                        <Form.Label>Role:</Form.Label>
                                        <Form.Control
                                            as="select"
                                            value={rolesPerson1.role}
                                            onChange={(e) =>
                                                setRolesPerson1({
                                                    ...rolesPerson1,
                                                    role: e.target.value
                                                })
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
                                </Card.Body>
                            </Card>

                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title className="font-bold text-lg">
                                        Person 2
                                    </Card.Title>
                                    <Form.Group
                                        controlId="rolesPerson2Name"
                                        className="mb-3"
                                    >
                                        <Form.Label>Name:</Form.Label>
                                        <Form.Control
                                            type="text"
                                            value={rolesPerson2.name || "Julia"}
                                            onChange={(e) =>
                                                setRolesPerson2({
                                                    ...rolesPerson2,
                                                    name: e.target.value
                                                })
                                            }
                                            className="w-full"
                                        />
                                    </Form.Group>
                                    <Form.Group
                                        controlId="rolesPerson2Persona"
                                        className="mb-3"
                                    >
                                        <Form.Label>Persona:</Form.Label>
                                        <Form.Control
                                            type="text"
                                            value={rolesPerson2.persona || ""}
                                            onChange={(e) =>
                                                setRolesPerson2({
                                                    ...rolesPerson2,
                                                    persona: e.target.value
                                                })
                                            }
                                            className="w-full"
                                        />
                                    </Form.Group>
                                    <Form.Group
                                        controlId="rolesPerson2Role"
                                        className="mb-3"
                                    >
                                        <Form.Label>Role:</Form.Label>
                                        <Form.Control
                                            as="select"
                                            value={rolesPerson2.role}
                                            onChange={(e) =>
                                                setRolesPerson2({
                                                    ...rolesPerson2,
                                                    role: e.target.value
                                                })
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
                                </Card.Body>
                            </Card>

                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title className="font-bold text-lg">
                                        Dialogue Structure:
                                    </Card.Title>
                                    <Form.Group controlId="dialogueStructure">
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
                                                                ] =
                                                                    e.target.value;
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
                                                                        key={
                                                                            option
                                                                        }
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
                                                                        (
                                                                            _,
                                                                            i
                                                                        ) =>
                                                                            i !==
                                                                            index
                                                                    );
                                                                setDialogueStructure(
                                                                    newStructure
                                                                );
                                                            }}
                                                            className="remove-item-button"
                                                        >
                                                            <FaTimes className="inline-block" />
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
                                </Card.Body>
                            </Card>

                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title className="font-bold text-lg">
                                        Engagement Techniques:
                                    </Card.Title>
                                    <Form.Group controlId="engagementTechniques">
                                        <Form.Control
                                            as="select"
                                            multiple
                                            value={engagementTechniques}
                                            onChange={(e) =>
                                                setEngagementTechniques(
                                                    [
                                                        ...e.target
                                                            .selectedOptions
                                                    ].map(
                                                        (option) => option.value
                                                    )
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
                                </Card.Body>
                            </Card>

                            <Card className="mb-4">
                                <Card.Body>
                                    <Card.Title className="font-bold text-lg">
                                        User Instructions:
                                    </Card.Title>
                                    <Form.Group controlId="userInstructions">
                                        <Form.Control
                                            type="text"
                                            placeholder="Provide specific instructions here..."
                                            value={userInstructions}
                                            onChange={(e) =>
                                                setUserInstructions(
                                                    e.target.value
                                                )
                                            }
                                            className="w-full"
                                        />
                                    </Form.Group>
                                </Card.Body>
                            </Card>

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
                        </Accordion.Body>
                    </Accordion.Item>
                </Accordion>
            </Form>
        </>
    );
}

export default TranscriptDetailEdit;
