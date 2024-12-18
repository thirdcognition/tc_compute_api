const { useState } = React;

const AudioDetailDisplay = ({ audio, audioUrl }) => {
    const [showDetails, setShowDetails] = useState(false);
    const ttsConfig = audio.metadata?.conversation_config?.text_to_speech || {};
    const elevenlabsConfig = ttsConfig.elevenlabs || {};
    const geminiConfig = ttsConfig.gemini || {};

    const processStateIcon = (state) => {
        switch (state) {
            case "none":
                return "○"; // UML symbol for none
            case "waiting":
                return "⏳"; // UML symbol for waiting
            case "processing":
                return "⚙️"; // UML symbol for processing
            case "failed":
                return "❌"; // UML symbol for failed
            case "done":
                return "✔️"; // UML symbol for done
            default:
                return "";
        }
    };

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

    return React.createElement(
        "div",
        { className: "audio-detail-display border p-3 mb-4 rounded" },
        React.createElement("h6", { className: "font-bold mb-2" }, audio.title),
        React.createElement(
            "p",
            { className: "mb-2 flex items-center" },
            React.createElement(
                "span",
                { className: "mr-2" },
                processStateIcon(audio.process_state)
            ),
            React.createElement(
                "span",
                { className: "mr-2" },
                "📅" // UML symbol for Created At
            ),
            React.createElement(
                "span",
                { className: "mr-2" },
                new Date(audio.created_at).toLocaleString()
            ),
            React.createElement(
                "span",
                { className: "mr-2" },
                "🕒" // UML symbol for Updated At
            ),
            React.createElement(
                "span",
                null,
                new Date(audio.updated_at).toLocaleString()
            )
        ),
        audio.process_fail_message &&
            React.createElement(
                "p",
                { className: "mb-2 text-red-500" },
                `Error: ${audio.process_fail_message}`
            ),
        React.createElement(
            "div",
            { className: "flex items-center mb-2" },
            React.createElement("audio", {
                controls: true,
                src: audioUrl,
                className: "h-8"
            }),
            React.createElement(
                "button",
                {
                    onClick: handleDownload,
                    className: "ml-2"
                },
                "⇩" // UML symbol for download
            )
        ),
        React.createElement(
            "button",
            {
                onClick: () => setShowDetails(!showDetails),
                className:
                    "w-full py-2 mb-4 flex items-center justify-center bg-blue-500 text-white rounded"
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
                ttsConfig.default_tts_model &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Default TTS Model: ${ttsConfig.default_tts_model}`
                    ),
                elevenlabsConfig.default_voices?.question &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `ElevenLabs Question Voice: ${elevenlabsConfig.default_voices.question}`
                    ),
                elevenlabsConfig.default_voices?.answer &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `ElevenLabs Answer Voice: ${elevenlabsConfig.default_voices.answer}`
                    ),
                geminiConfig.default_voices?.question &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Gemini Question Voice: ${geminiConfig.default_voices.question}`
                    ),
                geminiConfig.default_voices?.answer &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Gemini Answer Voice: ${geminiConfig.default_voices.answer}`
                    )
            )
    );
};

export default AudioDetailDisplay;
