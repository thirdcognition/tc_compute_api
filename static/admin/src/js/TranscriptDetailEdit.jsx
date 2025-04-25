import { useState, useEffect } from "react";
import { Form, Button, Accordion } from "react-bootstrap";
import { handleCreateTranscript } from "./helpers/panel.js";
import { getWordCountDescription } from "./helpers/ui.js";
import {
    conversationStyleOptions,
    dialogueStructureOptions,
    engagementTechniquesOptions,
    outputLanguageOptions,
    defaultConversationStyle,
    defaultDialogueStructure,
    defaultEngagementTechniques
} from "./options.js";
import CronjobComponent from "./components/CronjobComponent.jsx";
import SectionCard from "./components/SectionCard.jsx";
import TTSConfigSection from "./components/TTSConfigSection.jsx";
import ItemListEditor from "./components/ItemListEditor.jsx";
import { calculateArticleCount } from "./helpers/transcriptHelpers.js";

function TranscriptDetailEdit({
    panelId,
    discussionData,
    transcriptData,
    taskStatus,
    initiatePolling,
    visible
}) {
    // --- State Variables ---
    const [wordCount, setWordCount] = useState(1000);
    const [maxWordCount, setMaxWordCount] = useState(2500);
    const [creativity] = useState(0.7);
    const [conversationStyle, setConversationStyle] = useState(
        defaultConversationStyle
    );
    const [dialogueStructure, setDialogueStructure] = useState(
        defaultDialogueStructure
    );
    const [engagementTechniques, setEngagementTechniques] = useState(
        defaultEngagementTechniques
    );
    const [userInstructions, setUserInstructions] = useState("");
    const [outputLanguage, setOutputLanguage] = useState("en");
    const [cronjob, setCronjob] = useState("");
    const [longForm, setLongForm] = useState(false);
    const [shortIntroAndConclusion, setShortIntroAndConclusion] =
        useState(false);
    const [disableIntroAndConclusion, setDisableIntroAndConclusion] =
        useState(false);
    const [selectedTranscript, setSelectedTranscript] = useState(null);
    // TTS/roles state managed by TTSConfigSection
    const [ttsModel, setTtsModel] = useState("elevenlabs");
    const [ttsConfig, setTtsConfig] = useState({});
    const [personRoles, setPersonRoles] = useState({});

    // --- Allowed Languages ---
    const allowedLanguages = (() => {
        const langs = discussionData?.metadata?.languages;
        if (Array.isArray(langs) && langs.length > 0) {
            return langs;
        }
        return ["en"];
    })();

    // --- Effects ---
    useEffect(() => {
        if (discussionData) {
            const articleCount = calculateArticleCount(discussionData);
            const newMaxWordCount =
                articleCount === 1
                    ? 1000
                    : articleCount * (longForm ? 500 : 300);
            setMaxWordCount(newMaxWordCount);
            if (wordCount > newMaxWordCount) {
                setWordCount(newMaxWordCount);
            }
        }
    }, [discussionData, wordCount, longForm]);

    // --- Transcript Copy Handler ---
    const applyTranscriptSettings = (transcript) => {
        if (transcript) {
            const metadata = transcript.metadata || {};
            const conversationConfig = metadata.conversation_config || {};

            setWordCount(conversationConfig.word_count || 1000);
            setConversationStyle(
                conversationConfig.conversation_style ||
                    defaultConversationStyle
            );
            setDialogueStructure(
                conversationConfig.dialogue_structure ||
                    defaultDialogueStructure
            );
            setEngagementTechniques(
                conversationConfig.engagement_techniques ||
                    defaultEngagementTechniques
            );
            setUserInstructions(conversationConfig.user_instructions || "");
            setOutputLanguage(conversationConfig.output_language || "en");
            setShortIntroAndConclusion(
                conversationConfig.short_intro_and_conclusion || false
            );
            setDisableIntroAndConclusion(
                conversationConfig.disable_intro_and_conclusion || false
            );
            setLongForm(metadata.longform || false);
            setTtsModel(metadata.tts_model || "elevenlabs");
            setTtsConfig(metadata.tts_config || {});
            setPersonRoles(conversationConfig.person_roles || {});
        }
    };

    // --- Dialogue Structure Handlers ---
    const handleAddDialogueStructure = () => {
        setDialogueStructure([
            ...dialogueStructure,
            dialogueStructureOptions[0] || ""
        ]);
    };

    const handleRemoveDialogueStructure = (indexToRemove) => {
        setDialogueStructure(
            dialogueStructure.filter((_, i) => i !== indexToRemove)
        );
    };

    const handleDialogueStructureChange = (index, value) => {
        const newStructure = [...dialogueStructure];
        newStructure[index] = value;
        setDialogueStructure(newStructure);
    };

    // --- Form Submit Handler ---
    const handleTranscriptSubmit = async (e) => {
        e.preventDefault();
        if (panelId) {
            handleCreateTranscript({
                panelId,
                discussionData,
                wordCount,
                creativity,
                conversationStyle,
                personRoles,
                dialogueStructure,
                engagementTechniques,
                userInstructions,
                outputLanguage,
                longForm,
                cronjob,
                shortIntroAndConclusion,
                disableIntroAndConclusion,
                ttsModel,
                ttsConfig
            }).then(({ taskId, success }) => {
                if (success && taskId) {
                    initiatePolling(taskId, "transcript");
                }
            });
        }
    };

    // --- Render Functions ---
    const renderDialogueStructureSelect = (structure, index) => (
        <Form.Control
            as="select"
            value={structure}
            onChange={(e) =>
                handleDialogueStructureChange(index, e.target.value)
            }
            className="w-full"
        >
            {dialogueStructureOptions.map((option) => (
                <option value={option} key={option}>
                    {option}
                </option>
            ))}
        </Form.Control>
    );

    // --- Main Render ---
    return (
        <Form onSubmit={handleTranscriptSubmit}>
            <Accordion defaultActiveKey={visible ? "0" : null}>
                <Accordion.Item eventKey="0">
                    <Accordion.Header>Create Transcript</Accordion.Header>
                    <Accordion.Body>
                        {/* Transcript Selector */}
                        <SectionCard title="Select Transcript to Copy Settings">
                            <Form.Group controlId="transcriptSelect">
                                <Form.Control
                                    as="select"
                                    value={selectedTranscript?.id || ""}
                                    onChange={(e) => {
                                        const selected = transcriptData?.find(
                                            (t) => t.id === e.target.value
                                        );
                                        if (selected) {
                                            setSelectedTranscript(selected);
                                            applyTranscriptSettings(selected);
                                        } else {
                                            setSelectedTranscript(null);
                                        }
                                    }}
                                    className="w-full"
                                >
                                    <option value="">
                                        -- Select Transcript --
                                    </option>
                                    {transcriptData &&
                                        transcriptData
                                            .filter(
                                                (t) =>
                                                    t.process_state ===
                                                        "done" &&
                                                    !t.transcript_parent_id
                                            )
                                            .sort(
                                                (a, b) =>
                                                    new Date(b.created_at) -
                                                    new Date(a.created_at)
                                            )
                                            .map((t, index) => (
                                                <option key={t.id} value={t.id}>
                                                    Transcript{" "}
                                                    {transcriptData.length -
                                                        index}
                                                    : {t.title}
                                                </option>
                                            ))}
                                </Form.Control>
                            </Form.Group>
                        </SectionCard>

                        {/* Cronjob */}
                        <SectionCard title="Update Cycle">
                            <CronjobComponent
                                value={cronjob}
                                onChange={setCronjob}
                            />
                        </SectionCard>

                        {/* Length */}
                        <SectionCard title="Requested length">
                            <Form.Group controlId="wordCount">
                                <Form.Control
                                    type="range"
                                    min={100}
                                    max={maxWordCount}
                                    step={100}
                                    value={wordCount}
                                    onChange={(e) =>
                                        setWordCount(Number(e.target.value))
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
                        </SectionCard>

                        {/* Processing Options (Only if multiple articles) */}
                        {calculateArticleCount(discussionData) > 1 && (
                            <SectionCard title="Transcript processing options">
                                <Form.Group
                                    controlId="longForm"
                                    className="mb-2"
                                >
                                    <Form.Check
                                        type="checkbox"
                                        label="Process every article separately (higher quality, longer process time)"
                                        checked={longForm}
                                        onChange={(e) =>
                                            setLongForm(e.target.checked)
                                        }
                                    />
                                </Form.Group>
                                <Form.Group
                                    controlId="disableIntroAndConclusion"
                                    className="mb-2"
                                >
                                    <Form.Check
                                        type="checkbox"
                                        label="Disable introduction and conclusion segments"
                                        checked={disableIntroAndConclusion}
                                        onChange={(e) => {
                                            setDisableIntroAndConclusion(
                                                e.target.checked
                                            );
                                            if (e.target.checked)
                                                setShortIntroAndConclusion(
                                                    false
                                                );
                                        }}
                                    />
                                </Form.Group>
                                <Form.Group
                                    controlId="shortIntroAndConclusion"
                                    className="mb-2"
                                >
                                    <Form.Check
                                        type="checkbox"
                                        label="Use short introduction and conclusion segments"
                                        checked={shortIntroAndConclusion}
                                        onChange={(e) =>
                                            setShortIntroAndConclusion(
                                                e.target.checked
                                            )
                                        }
                                        disabled={disableIntroAndConclusion}
                                    />
                                </Form.Group>
                            </SectionCard>
                        )}

                        {/* Conversation Style */}
                        <SectionCard title="Conversation Style">
                            <Form.Group controlId="conversationStyle">
                                <Form.Control
                                    as="select"
                                    multiple
                                    value={conversationStyle}
                                    onChange={(e) =>
                                        setConversationStyle(
                                            [...e.target.selectedOptions].map(
                                                (o) => o.value
                                            )
                                        )
                                    }
                                    className="w-full h-40"
                                >
                                    {conversationStyleOptions.map((style) => (
                                        <option value={style} key={style}>
                                            {style}
                                        </option>
                                    ))}
                                </Form.Control>
                            </Form.Group>
                        </SectionCard>

                        {/* TTS Provider, TTS Language Configurations, and Person Roles */}
                        <TTSConfigSection
                            allowedLanguages={allowedLanguages}
                            initialTtsModel={ttsModel}
                            initialTtsConfig={ttsConfig}
                            initialPersonRoles={personRoles}
                            canEditRoles={true}
                            disableRoleFields={false}
                            onChange={({
                                ttsModel: newTtsModel,
                                ttsConfig: newTtsConfig,
                                personRoles: newPersonRoles
                            }) => {
                                console.log("on change do", newPersonRoles);
                                setTtsModel(newTtsModel);
                                setTtsConfig(newTtsConfig);
                                setPersonRoles(newPersonRoles);
                            }}
                        />

                        {/* Dialogue Structure */}
                        <SectionCard title="Dialogue Structure">
                            <ItemListEditor
                                items={dialogueStructure}
                                onAddItem={handleAddDialogueStructure}
                                onRemoveItem={handleRemoveDialogueStructure}
                                renderItem={renderDialogueStructureSelect}
                                addButtonLabel="Add Structure Step"
                                renderItemHeader={null}
                            />
                        </SectionCard>

                        {/* Engagement Techniques */}
                        <SectionCard title="Engagement Techniques">
                            <Form.Group controlId="engagementTechniques">
                                <Form.Control
                                    as="select"
                                    multiple
                                    value={engagementTechniques}
                                    onChange={(e) =>
                                        setEngagementTechniques(
                                            [...e.target.selectedOptions].map(
                                                (o) => o.value
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
                        </SectionCard>

                        {/* User Instructions */}
                        <SectionCard title="User Instructions">
                            <Form.Group controlId="userInstructions">
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
                        </SectionCard>

                        {/* Output Language */}
                        <SectionCard title="Output Language">
                            <Form.Group controlId="outputLanguage">
                                <Form.Label className="font-semibold">
                                    Output Language (Note: Selected voice models
                                    should align):
                                </Form.Label>
                                <Form.Control
                                    as="select"
                                    value={outputLanguage}
                                    onChange={(e) =>
                                        setOutputLanguage(e.target.value)
                                    }
                                    className="w-full"
                                >
                                    {Object.entries(outputLanguageOptions).map(
                                        ([langId, language]) => (
                                            <option value={langId} key={langId}>
                                                {language}
                                            </option>
                                        )
                                    )}
                                </Form.Control>
                            </Form.Group>
                        </SectionCard>

                        {/* Submit Button */}
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
    );
}

export default TranscriptDetailEdit;
