import AudioDetailDisplay from "./AudioDetailDisplay.js";
const { useState } = React;

const TranscriptDetailDisplay = ({
    transcript,
    accessToken,
    transcriptUrls,
    audios,
    audioUrls
}) => {
    const [showDetails, setShowDetails] = useState(false);
    const [isTranscriptVisible, setIsTranscriptVisible] = useState(false);
    const [transcriptContent, setTranscriptContent] = useState("");
    const [updateCycle, setUpdateCycle] = useState(
        (transcript.metadata?.update_cycle ?? transcript.generation_interval) ||
            0
    ); // Editable updateCycle in seconds
    const config = transcript.metadata?.conversation_config || {};

    const toggleTranscriptVisibility = (transcriptId) => {
        if (!isTranscriptVisible && transcriptUrls[transcriptId]) {
            fetch(transcriptUrls[transcriptId], {
                headers: {
                    Authorization: `Bearer ${accessToken}`
                }
            })
                .then((response) => response.text())
                .then((text) => {
                    setTranscriptContent(text);
                    setIsTranscriptVisible(true);
                })
                .catch((error) =>
                    console.error("Error fetching transcript:", error)
                );
        } else {
            setIsTranscriptVisible(!isTranscriptVisible);
        }
    };

    const renderTranscript = (transcriptContent) => {
        const personRegex = /<([^>]+)>([^<]+)<\/\1>/g;
        const matches = [...transcriptContent.matchAll(personRegex)];

        return matches.map((match, index) =>
            React.createElement(
                "div",
                {
                    key: index,
                    className:
                        "flex items-start mb-2 p-2 border-b border-gray-300"
                },
                React.createElement(
                    "strong",
                    { className: "text-blue-600 w-24" },
                    match[1]
                ),
                React.createElement(
                    "span",
                    { className: "text-gray-700 flex-1" },
                    match[2].trim()
                )
            )
        );
    };

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

    const updateTranscript = async (newUpdateCycle) => {
        try {
            const response = await fetch(`/panel/transcript/${transcript.id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`
                },
                body: JSON.stringify({
                    ...transcript,
                    generation_interval: newUpdateCycle || null, // Set or remove the value
                    metadata: {
                        ...transcript.metadata,
                        update_cycle: newUpdateCycle || null
                    }
                })
            });

            if (!response.ok) {
                throw new Error("Failed to update transcript");
            }

            const updatedTranscript = await response.json();
            setUpdateCycle(updatedTranscript.metadata.update_cycle || 0);
        } catch (error) {
            console.error("Error updating transcript:", error);
        }
    };

    const formatUpdateCycle = (seconds) => {
        if (seconds === 0) return "Not set";
        const days = Math.floor(seconds / (24 * 3600));
        const hours = (seconds % (24 * 3600)) / 3600;
        return `${days}d ${hours}h`;
    };

    return React.createElement(
        "div",
        { className: "transcript-detail-display border p-3 mb-4 rounded" },
        React.createElement(
            "h5",
            { className: "font-bold mb-2" },
            transcript.title
        ),
        React.createElement(
            "p",
            { className: "mb-2 flex items-center" },
            React.createElement(
                "span",
                { className: "mr-2" },
                processStateIcon(transcript.process_state)
            ),
            React.createElement(
                "span",
                { className: "mr-2" },
                "📅" // UML symbol for Created At
            ),
            React.createElement(
                "span",
                { className: "mr-2" },
                new Date(transcript.created_at).toLocaleString()
            ),
            React.createElement(
                "span",
                { className: "mr-2" },
                "🕒" // UML symbol for Updated At
            ),
            React.createElement(
                "span",
                null,
                new Date(transcript.updated_at).toLocaleString()
            )
        ),
        transcript.process_fail_message &&
            React.createElement(
                "p",
                { className: "mb-2 text-red-500" },
                `Error: ${transcript.process_fail_message}`
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
                config.word_count &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Word Count: ${config.word_count}`
                    ),
                config.creativity &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Creativity: ${config.creativity}`
                    ),
                config.conversation_style &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Conversation Style: ${config.conversation_style.join(", ")}`
                    ),
                config.roles_person1 &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Role for Person 1: ${config.roles_person1}`
                    ),
                config.roles_person2 &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Role for Person 2: ${config.roles_person2}`
                    ),
                config.dialogue_structure &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Dialogue Structure: ${config.dialogue_structure.join(", ")}`
                    ),
                config.engagement_techniques &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Engagement Techniques: ${config.engagement_techniques.join(", ")}`
                    ),
                config.user_instructions &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `User Instructions: ${config.user_instructions}`
                    ),
                config.output_language &&
                    React.createElement(
                        "p",
                        { className: "mb-2" },
                        `Output Language: ${config.output_language}`
                    ),
                React.createElement(
                    "label",
                    { className: "font-semibold mb-1 block" },
                    "Update Cycle:"
                ),
                React.createElement(
                    "div",
                    { className: "mb-2 flex items-center space-x-2" },
                    React.createElement("input", {
                        type: "range",
                        min: 0,
                        max: 14 * 24 * 3600, // 2 weeks in seconds
                        step: 12 * 3600, // 12 hours in seconds
                        value: updateCycle,
                        onChange: (e) => setUpdateCycle(Number(e.target.value)),
                        className: "flex-grow"
                    }),
                    React.createElement(
                        "span",
                        { className: "ml-2" },
                        formatUpdateCycle(updateCycle)
                    ),
                    React.createElement(
                        "button",
                        {
                            onClick: () =>
                                updateTranscript(
                                    updateCycle === 0 ? null : updateCycle
                                ),
                            className:
                                "bg-blue-500 text-white py-1 px-3 rounded"
                        },
                        "Update"
                    ),
                    React.createElement(
                        "button",
                        {
                            onClick: () => updateTranscript(null),
                            className: "bg-red-500 text-white py-1 px-3 rounded"
                        },
                        "Remove"
                    )
                )
            ),
        React.createElement(
            "button",
            {
                onClick: () => toggleTranscriptVisibility(transcript.id),
                className:
                    "w-full py-2 mb-4 flex items-center justify-center bg-blue-500 text-white rounded"
            },
            React.createElement(
                "span",
                { className: "mr-2" },
                isTranscriptVisible ? "▼" : "▶"
            ),
            React.createElement(
                "span",
                null,
                isTranscriptVisible ? "Hide Transcript" : "View Transcript"
            )
        ),
        isTranscriptVisible &&
            React.createElement(
                "div",
                { className: "mt-4" },
                renderTranscript(transcriptContent)
            ),
        audios &&
            audios
                .filter((audio) => audio.transcript_id === transcript.id)
                .map((audio) =>
                    React.createElement(AudioDetailDisplay, {
                        key: audio.id,
                        audio,
                        audioUrl: audioUrls[audio.id]
                    })
                )
    );
};

export default TranscriptDetailDisplay;
