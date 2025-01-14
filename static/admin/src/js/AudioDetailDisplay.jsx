import { useState } from "react";
import { processStateIcon } from "./helpers/ui.js";

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
        <div className="audio-detail-display border p-3 mb-4 rounded">
            <h6 className="font-bold mb-2">{audio.title}</h6>
            <p className="mb-2 flex items-center">
                <span className="mr-2">
                    {processStateIcon(audio.process_state)}
                </span>
                <span className="mr-2">📅</span>
                <span className="mr-2">
                    {new Date(audio.created_at).toLocaleString()}
                </span>
                <span className="mr-2">🕒</span>
                <span>{new Date(audio.updated_at).toLocaleString()}</span>
            </p>
            {audio.process_fail_message && (
                <p className="mb-2 text-red-500">
                    Error: {audio.process_fail_message}
                </p>
            )}
            <div className="flex items-center mb-2">
                <audio controls src={audioUrl} className="h-8" />
                <button onClick={handleDownload} className="ml-2">
                    ⇩
                </button>
            </div>
            <button
                onClick={() => setShowDetails(!showDetails)}
                className="w-full py-2 mb-4 flex items-center justify-center bg-blue-500 text-white rounded"
            >
                <span className="mr-2">{showDetails ? "▼" : "▶"}</span>
                <span>
                    {showDetails ? "Hide Details" : "Show More Details"}
                </span>
            </button>
            {showDetails && (
                <div className="border p-3 mb-4 rounded">
                    {ttsConfig.default_tts_model && (
                        <p className="mb-2">
                            Default TTS Model: {ttsConfig.default_tts_model}
                        </p>
                    )}
                    {elevenlabsConfig.default_voices?.question && (
                        <p className="mb-2">
                            ElevenLabs Question Voice:{" "}
                            {elevenlabsConfig.default_voices.question}
                        </p>
                    )}
                    {elevenlabsConfig.default_voices?.answer && (
                        <p className="mb-2">
                            ElevenLabs Answer Voice:{" "}
                            {elevenlabsConfig.default_voices.answer}
                        </p>
                    )}
                    {geminiConfig.default_voices?.question && (
                        <p className="mb-2">
                            Gemini Question Voice:{" "}
                            {geminiConfig.default_voices.question}
                        </p>
                    )}
                    {geminiConfig.default_voices?.answer && (
                        <p className="mb-2">
                            Gemini Answer Voice:{" "}
                            {geminiConfig.default_voices.answer}
                        </p>
                    )}
                </div>
            )}
        </div>
    );
};

export default AudioDetailDisplay;
