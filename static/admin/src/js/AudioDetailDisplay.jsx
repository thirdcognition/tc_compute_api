import { useState } from "react";
import { Button, Card } from "react-bootstrap"; // Keep Card for speaker display
import { FaDownload } from "react-icons/fa";

// Helpers and Options
import { getLangName, sortLangCodes } from "./helpers/languageHelpers.js"; // Use new helper
import { downloadAudio, getHostsForLang } from "./helpers/audioHelpers.js"; // Import download & getHostsForLang helper

// Shared Components
import StatusHeader from "./components/StatusHeader.jsx";
import ErrorMessage from "./components/ErrorMessage.jsx";
import SectionCard from "./components/SectionCard.jsx";
import ObjectDisplay from "./components/ObjectDisplay.jsx";
import DetailAccordion from "./components/DetailAccordion.jsx";

// --- Main Component ---
const AudioDetailDisplay = ({ audio, audioUrl }) => {
    // --- State ---
    // No local state needed for display logic anymore

    // --- Derived Data ---
    const ttsConfig = audio.metadata?.tts_config || {};
    const conversationConfig = audio.metadata?.conversation_config || {};
    const personRoles = conversationConfig.person_roles || {}; // Expects { roleIdx: { name, role, persona, voice_config: { lang: {...} } } }

    // --- Handlers ---
    // Moved handleDownload to audioHelpers.js
    // Moved getHostsForLang to audioHelpers.js

    // --- Render Functions for DetailAccordion ---

    const renderLanguageHeader = (lang) => (
        <span className="font-semibold">{getLangName(lang)}</span>
    );

    const renderLanguageBody = (lang) => {
        const hosts = getHostsForLang(lang, personRoles); // Use imported helper, pass personRoles
        const langTtsConfig = ttsConfig[lang] || {};

        return (
            <>
                {/* Display TTS Config for the language */}
                <SectionCard title="TTS Configuration" className="mb-3 ms-3">
                    <ObjectDisplay data={langTtsConfig} />
                </SectionCard>

                {/* Display Speaker Configs */}
                <h6 className="ms-3 mb-2">Speaker Configurations</h6>
                {hosts.length === 0 ? (
                    <Card className="ms-3">
                        <Card.Body>
                            <Card.Text className="text-muted">
                                No speaker configurations defined for this
                                language.
                            </Card.Text>
                        </Card.Body>
                    </Card>
                ) : (
                    hosts.map(({ roleIdx, host, voiceConfig }) => (
                        <Card key={roleIdx} className="mb-3 ms-3">
                            <Card.Header as="h6">
                                {host.name
                                    ? `${host.name}${host.role ? ` (${host.role})` : ""}`
                                    : `Host ${roleIdx}`}
                            </Card.Header>
                            <Card.Body>
                                {host.persona && (
                                    <Card.Subtitle className="mb-2 text-muted">
                                        Persona: {host.persona}
                                    </Card.Subtitle>
                                )}
                                <ObjectDisplay data={voiceConfig} />
                            </Card.Body>
                        </Card>
                    ))
                )}
            </>
        );
    };

    // --- Main Render ---
    const sortedLanguages = sortLangCodes(Object.keys(ttsConfig));

    return (
        <>
            {/* Status Header */}
            <StatusHeader item={audio} />

            {/* Error Message */}
            <ErrorMessage message={audio.process_state_message} />

            {/* Audio Player and Download */}
            {audio.process_state === "done" && audioUrl && (
                <div className="d-flex align-items-center justify-content-center mb-4 w-100">
                    <audio
                        controls
                        src={audioUrl}
                        className="me-2"
                        style={{ height: "32px" }}
                    />
                    <Button
                        variant="secondary"
                        onClick={() => downloadAudio(audioUrl, audio)} // Use imported helper
                        size="sm"
                        title="Download Audio"
                    >
                        <FaDownload />
                    </Button>
                </div>
            )}
            {audio.process_state === "processing" && (
                <p className="text-center text-muted mb-4">
                    Audio processing...
                </p>
            )}
            {audio.process_state === "pending" && (
                <p className="text-center text-muted mb-4">Audio pending...</p>
            )}

            {/* Language Configurations Accordion */}
            {sortedLanguages.length > 0 ? (
                <DetailAccordion
                    items={sortedLanguages}
                    itemKey={(lang) => lang}
                    renderHeader={renderLanguageHeader}
                    renderBody={renderLanguageBody}
                    defaultActiveKey={sortedLanguages[0]} // Open first language
                    className="mb-3"
                />
            ) : (
                <SectionCard title="Configurations">
                    <p className="text-muted">
                        No TTS or Speaker configurations found in metadata.
                    </p>
                </SectionCard>
            )}
        </>
    );
};

export default AudioDetailDisplay;
