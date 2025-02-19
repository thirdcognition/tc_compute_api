import { useState } from "react";
import { processStateIcon } from "./helpers/ui.js";
import { FaCalendarAlt, FaClock, FaDownload } from "react-icons/fa";
import { Button, Accordion } from "react-bootstrap";

const AudioDetailDisplay = ({ audio, audioUrl }) => {
    const [showDetails, setShowDetails] = useState(false);
    const ttsConfig = audio.metadata?.conversation_config?.text_to_speech || {};
    const elevenlabsConfig = ttsConfig.elevenlabs || {};
    const geminiConfig = ttsConfig.gemini || {};

    const handleDownload = async () => {
        try {
            const response = await fetch(audioUrl);
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `${audio.title || "audio"}.mp3`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Download failed", error);
        }
    };

    return (
        <>
            <p className="mb-3 flex items-between mr-6">
                <span className="mr-2">
                    {processStateIcon(audio.process_state)}
                </span>
                <div class="flex-1 self-center">
                    <span className="mr-2">
                        <FaCalendarAlt className="inline-block" />
                    </span>
                    <span className="mr-2">
                        {new Date(audio.created_at).toLocaleString()}
                    </span>
                </div>
                <div class="flex-1 self-center">
                    <span className="mr-2">
                        <FaClock className="inline-block" />
                    </span>
                    <span>{new Date(audio.updated_at).toLocaleString()}</span>
                </div>
            </p>
            {audio.process_state_message && (
                <p className="mb-2 text-red-500">
                    Error: {audio.process_state_message}
                </p>
            )}
            <div className="flex items-center justify-center mb-4 w-full">
                {audio.process_state === "done" && (
                    <>
                        <audio controls src={audioUrl} className="h-8" />
                        <Button
                            variant="secondary"
                            onClick={handleDownload}
                            className="ml-2"
                        >
                            <FaDownload className="inline-block" />
                        </Button>
                    </>
                )}
            </div>
            <div className="flex">
                {ttsConfig.default_tts_model && (
                    <p className="flex-1">
                        Default TTS Model: {ttsConfig.default_tts_model}
                    </p>
                )}
                {elevenlabsConfig.default_voices?.question && (
                    <p className="flex-1">
                        ElevenLabs Question Voice:{" "}
                        {elevenlabsConfig.default_voices.question}
                    </p>
                )}
                {elevenlabsConfig.default_voices?.answer && (
                    <p className="flex-1">
                        ElevenLabs Answer Voice:{" "}
                        {elevenlabsConfig.default_voices.answer}
                    </p>
                )}
                {geminiConfig.default_voices?.question && (
                    <p className="flex-1">
                        Gemini Question Voice:{" "}
                        {geminiConfig.default_voices.question}
                    </p>
                )}
                {geminiConfig.default_voices?.answer && (
                    <p className="flex-1">
                        Gemini Answer Voice:{" "}
                        {geminiConfig.default_voices.answer}
                    </p>
                )}
            </div>
        </>
    );
};

export default AudioDetailDisplay;
