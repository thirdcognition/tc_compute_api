import { useState, useEffect } from "react";
import SectionCard from "./components/SectionCard.jsx";
import TTSConfigSection from "./components/TTSConfigSection.jsx";
import { Button, Accordion } from "react-bootstrap";
import { handleCreateAudio } from "./helpers/panel.js";

function AudioDetailEdit({
    panelId,
    transcriptData,
    audioData, // Add audioData prop
    taskStatus,
    initiatePolling,
    visible // Controls the outer Accordion visibility
}) {
    // --- State ---
    const [transcriptId, setTranscriptId] = useState(null);
    const [audioId, setAudioId] = useState(null); // State for selected audio ID
    // Parent state to hold the final config derived from TTSConfigSection via onChange
    const [ttsModel, setTtsModel] = useState("elevenlabs");
    const [ttsConfig, setTtsConfig] = useState({});
    const [personRoles, setPersonRoles] = useState({});
    const [baseAudioDetails, setBaseAudioDetails] = useState({});
    const [activeMetadata, setActiveMetadata] = useState({});

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

    // Find the selected audio object
    const selectedAudio = audioData?.find((a) => a.id === audioId);

    // On transcript selection, extract all relevant details for audio creation
    useEffect(() => {
        if (selectedTranscript || selectedAudio) {
            setTranscriptId(selectedTranscript.id);

            const metadata =
                (selectedAudio ?? selectedTranscript).metadata || {};
            const conversationConfig = metadata.conversation_config || {};

            setTtsModel(metadata.tts_model || "elevenlabs");
            setTtsConfig(metadata.tts_config || {});
            setPersonRoles(conversationConfig.person_roles || {});

            setActiveMetadata(metadata);

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
    }, [transcriptData, transcriptId, audioData, audioId]); // Rerun when transcript changes

    // Determine the metadata source to pass to TTSConfigSection
    // Use audio metadata if selected, otherwise fall back to transcript metadata
    // const activeMetadata = (selectedAudio ?? selectedTranscript)?.metadata;

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

    const ttsChange = ({
        ttsModel: newTtsModel,
        ttsConfig: newTtsConfig,
        personRoles: newPersonRoles
    }) => {
        setTtsModel(newTtsModel);
        setTtsConfig(newTtsConfig);
        setPersonRoles(newPersonRoles);
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
                            {transcriptData // Keep existing transcript selector logic
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

                {/* Audio Selector (only if audio data available) */}
                {audioData && audioData.length > 0 && selectedTranscript && (
                    <SectionCard title="Load Settings from Previous Audio (Optional)">
                        <select
                            value={audioId || ""}
                            onChange={(e) => setAudioId(e.target.value)}
                            className="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="">
                                -- Use Transcript Settings --
                            </option>
                            {audioData
                                .reduce((unique, current) => {
                                    if (
                                        !unique.some(
                                            (item) =>
                                                item.title === current.title
                                        )
                                    ) {
                                        unique.push(current);
                                    }
                                    return unique;
                                }, [])
                                // .filter((a) => a.transcript_id === transcriptId)
                                // .filter((a) => a.process_state === "done") // Filter for completed audio
                                .sort(
                                    (a, b) =>
                                        new Date(b.created_at) -
                                        new Date(a.created_at)
                                ) // Sort by creation date, newest first
                                .sort((a, b) =>
                                    b.transcript_id.localeCompare(
                                        a.transcript_id
                                    )
                                ) // Sort by creation date, newest first
                                .map((a, index) => (
                                    <option key={a.id} value={a.id}>
                                        Audio {audioData.length - index}:{" "}
                                        {a.title || "No title"} - Created:{" "}
                                        {new Date(
                                            a.created_at
                                        ).toLocaleString()}
                                    </option>
                                ))}
                        </select>
                        <p className="text-xs text-gray-500 mt-1">
                            Select an audio file to reuse its TTS model,
                            configuration, and speaker settings.
                        </p>
                    </SectionCard>
                )}

                {/* TTS Provider, TTS Language Configurations, and Person Roles */}
                <TTSConfigSection
                    key={
                        audioId
                            ? "audio_tts_config_" + audioId
                            : "transcript_tts_config_" + transcriptId
                    }
                    // Pass the metadata from the selected audio OR transcript
                    // TTSConfigSection will internally derive its state from this
                    metadata={activeMetadata}
                    allowedLanguages={
                        selectedAudio?.lang ?? selectedTranscript?.lang ?? "en"
                    }
                    canEditRoles={false}
                    disableRoleFields={true}
                    onChange={ttsChange}
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
