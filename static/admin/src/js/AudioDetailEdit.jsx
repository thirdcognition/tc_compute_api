import { useState, useEffect } from "react";
import SectionCard from "./components/SectionCard.jsx";
import TTSConfigSection from "./components/TTSConfigSection.jsx";
import { Button, Accordion } from "react-bootstrap";
import { handleCreateAudio } from "./helpers/panel.js";

function AudioDetailEdit({
    panelId,
    transcriptData,
    taskStatus,
    initiatePolling,
    visible // Controls the outer Accordion visibility
}) {
    // --- State ---
    const [transcriptId, setTranscriptId] = useState(null);
    const [ttsModel, setTtsModel] = useState("elevenlabs");
    const [ttsConfig, setTtsConfig] = useState({});
    const [personRoles, setPersonRoles] = useState({});
    const [baseAudioDetails, setBaseAudioDetails] = useState({});

    // Find the selected transcript and allowed languages
    const selectedTranscript =
        transcriptData?.find((t) => t.id === transcriptId) ||
        (transcriptData && transcriptData.length > 0
            ? transcriptData
                  .filter((t) => t.process_state === "done")
                  .sort(
                      (a, b) => new Date(b.created_at) - new Date(a.created_at)
                  )[0]
            : null);

    const allowedLanguages = (() => {
        const langs = selectedTranscript?.metadata?.languages;
        if (Array.isArray(langs) && langs.length > 0) {
            return langs;
        }
        return ["en"];
    })();

    // On transcript selection, extract all relevant details for audio creation
    useEffect(() => {
        if (selectedTranscript) {
            setTranscriptId(selectedTranscript.id);
            const metadata = selectedTranscript.metadata || {};
            const conversationConfig = metadata.conversation_config || {};

            setTtsModel(metadata.tts_model || "elevenlabs");
            setTtsConfig(metadata.tts_config || {});
            setPersonRoles(conversationConfig.person_roles || {});

            // Store all relevant details for audio creation (except ttsModel, ttsConfig, personRoles)
            setBaseAudioDetails({
                title: selectedTranscript.title,
                inputSource: selectedTranscript.input_source,
                inputText: selectedTranscript.input_text,
                displayTag: selectedTranscript.display_tag,
                podcastName: selectedTranscript.podcast_name,
                podcastTagline: selectedTranscript.podcast_tagline,
                creativity: conversationConfig.creativity,
                wordCount: conversationConfig.word_count,
                longForm: metadata.longform,
                outputLanguage: conversationConfig.output_language,
                conversationStyle: conversationConfig.conversation_style,
                dialogueStructure: conversationConfig.dialogue_structure,
                engagementTechniques: conversationConfig.engagement_techniques,
                userInstructions: conversationConfig.user_instructions,
                shortIntroAndConclusion:
                    conversationConfig.short_intro_and_conclusion,
                disableIntroAndConclusion:
                    conversationConfig.disable_intro_and_conclusion,
                cronjob: selectedTranscript.cronjob
                // Add any other fields needed for buildPanelRequestData
            });
        } else {
            setTranscriptId(null);
            setTtsModel("elevenlabs");
            setTtsConfig({});
            setPersonRoles({});
            setBaseAudioDetails({});
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [transcriptData, transcriptId]);

    // Handle submit button click
    const handleAudioSubmit = async () => {
        if (!transcriptId) {
            alert("Please select a transcript first.");
            return;
        }
        const configToSend = {
            ...baseAudioDetails,
            ttsModel,
            ttsConfig,
            personRoles,
            panelId,
            transcriptId
        };

        handleCreateAudio(configToSend).then(({ taskId, success }) => {
            if (success && taskId) {
                initiatePolling(taskId, "audio");
            } else {
                alert("Failed to initiate audio creation.");
            }
        });
    };

    // --- Main Render ---
    function renderContent() {
        return (
            <>
                {/* Transcript Selector (only if multiple transcripts available) */}
                {transcriptData && transcriptData.length > 1 && (
                    <SectionCard title="Select Transcript">
                        <select
                            value={transcriptId || ""}
                            onChange={(e) => setTranscriptId(e.target.value)}
                            className="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="" disabled>
                                -- Select a Transcript --
                            </option>
                            {transcriptData
                                .filter((t) => t.process_state === "done")
                                .sort(
                                    (a, b) =>
                                        new Date(b.created_at) -
                                        new Date(a.created_at)
                                )
                                .map((t, index) => (
                                    <option key={t.id} value={t.id}>
                                        Transcript{" "}
                                        {transcriptData.length - index}:{" "}
                                        {t.title}
                                    </option>
                                ))}
                        </select>
                    </SectionCard>
                )}

                {/* TTS Provider, TTS Language Configurations, and Person Roles */}
                <TTSConfigSection
                    allowedLanguages={allowedLanguages}
                    initialTtsModel={ttsModel}
                    initialTtsConfig={ttsConfig}
                    initialPersonRoles={personRoles}
                    canEditRoles={false}
                    disableRoleFields={true}
                    onChange={({
                        ttsModel: newTtsModel,
                        ttsConfig: newTtsConfig,
                        personRoles: newPersonRoles
                    }) => {
                        setTtsModel(newTtsModel);
                        setTtsConfig(newTtsConfig);
                        setPersonRoles(newPersonRoles);
                    }}
                />

                {/* Submit Button */}
                {transcriptId && (
                    <Button
                        variant="primary"
                        onClick={handleAudioSubmit}
                        className="w-full py-2 mt-3"
                        disabled={
                            !transcriptId ||
                            (taskStatus !== "idle" &&
                                taskStatus !== "failure" &&
                                taskStatus !== "success")
                        }
                    >
                        Create Audio
                    </Button>
                )}
            </>
        );
    }

    if (visible !== undefined) {
        return (
            <Accordion defaultActiveKey={visible ? "0" : null}>
                <Accordion.Item eventKey="0">
                    <Accordion.Header>
                        {transcriptData
                            ? "Create Audio"
                            : "Configure TTS & Speakers"}
                    </Accordion.Header>
                    <Accordion.Body>{renderContent()}</Accordion.Body>
                </Accordion.Item>
            </Accordion>
        );
    } else {
        return renderContent();
    }
}

export default AudioDetailEdit;
