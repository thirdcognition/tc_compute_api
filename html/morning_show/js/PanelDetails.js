const { Card } = ReactBootstrap;

function PanelDetails({ panel, accessToken }) {
    const [details, setDetails] = React.useState({
        transcriptUrl: "",
        audioBlobUrl: "",
        audioProcessState: "",
        audioFailMessage: "",
        transcriptProcessState: "",
        transcriptFailMessage: ""
    });
    const [transcriptContent, setTranscriptContent] = React.useState("");
    const [isTranscriptVisible, setIsTranscriptVisible] = React.useState(false);

    React.useEffect(() => {
        // Reset details and transcript content when panel changes
        setDetails({
            transcriptUrl: "",
            audioBlobUrl: "",
            audioProcessState: "",
            audioFailMessage: "",
            transcriptProcessState: "",
            transcriptFailMessage: ""
        });
        setTranscriptContent("");
        setIsTranscriptVisible(false);

        fetch(`/public_panel/${panel.id}/files`, {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        })
            .then((response) => response.json())
            .then((data) => {
                setDetails((prevDetails) => ({
                    ...prevDetails,
                    transcriptUrl: data.transcript_url || "",
                    audioBlobUrl: data.audio_url || ""
                }));

                // Fetch the audio file with authorization
                if (data.audio_url) {
                    fetch(data.audio_url, {
                        headers: {
                            Authorization: `Bearer ${accessToken}`
                        }
                    })
                        .then((audioResponse) => audioResponse.blob())
                        .then((audioBlob) => {
                            const audioBlobUrl = URL.createObjectURL(audioBlob);
                            setDetails((prevDetails) => ({
                                ...prevDetails,
                                audioBlobUrl
                            }));
                        })
                        .catch((error) =>
                            console.error("Error fetching audio file:", error)
                        );
                }
            })
            .catch((error) =>
                console.error("Error fetching panel details:", error)
            );

        // Add process details from panel.audios and panel.transcripts
        if (panel.audios && panel.audios.length > 0) {
            const audio = panel.audios[0];
            setDetails((prevDetails) => ({
                ...prevDetails,
                audioProcessState: audio.process_state || "",
                audioFailMessage: audio.process_fail_message || ""
            }));
        }

        if (panel.transcripts && panel.transcripts.length > 0) {
            const transcript = panel.transcripts[0];
            setDetails((prevDetails) => ({
                ...prevDetails,
                transcriptProcessState: transcript.process_state || "",
                transcriptFailMessage: transcript.process_fail_message || ""
            }));
        }
    }, [panel, accessToken]);

    const renderStateIcon = (state) => {
        switch (state) {
            case "done":
                return React.createElement(
                    "svg",
                    {
                        width: 16,
                        height: 16,
                        fill: "green",
                        viewBox: "0 0 16 16"
                    },
                    React.createElement("path", {
                        d: "M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM6.5 11.5L3 8l1.5-1.5L6.5 9l5-5L13 5.5l-6.5 6z"
                    })
                );
            case "failed":
                return React.createElement(
                    "svg",
                    {
                        width: 16,
                        height: 16,
                        fill: "red",
                        viewBox: "0 0 16 16"
                    },
                    React.createElement("path", {
                        d: "M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.86 10.97L10.97 11.86 8 8.97l-2.97 2.89-1.89-1.89L6.03 8 3.14 5.03l1.89-1.89L8 6.03l2.97-2.89 1.89 1.89L9.97 8l2.89 2.97z"
                    })
                );
            case "processing":
                return React.createElement(
                    "svg",
                    {
                        width: 16,
                        height: 16,
                        fill: "blue",
                        viewBox: "0 0 16 16",
                        className: "spin"
                    },
                    React.createElement("path", {
                        d: "M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zm3.5 8a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0z"
                    })
                );
            default:
                return null;
        }
    };

    const toggleTranscriptVisibility = () => {
        if (!isTranscriptVisible && details.transcriptUrl) {
            fetch(details.transcriptUrl, {
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

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text).then(
            () => {
                console.log("Copying to clipboard was successful!");
            },
            (err) => {
                console.error("Could not copy text: ", err);
            }
        );
    };

    return React.createElement(
        "div",
        { style: { maxHeight: "100vh", overflowY: "auto" } },
        React.createElement(
            Card,
            { className: "mb-3 shadow-lg" },
            React.createElement(
                Card.Body,
                null,
                React.createElement(
                    Card.Title,
                    { className: "text-xl font-bold mb-4" },
                    panel.title
                ),
                React.createElement(
                    Card.Text,
                    {
                        className: "text-sm text-gray-600 mb-2",
                        onClick: () => copyToClipboard(panel.id),
                        style: { cursor: "pointer" }
                    },
                    React.createElement("strong", null, "ID: "),
                    panel.id
                ),
                details.audioBlobUrl &&
                    React.createElement(
                        "div",
                        {
                            className:
                                "flex items-center justify-between w-full mb-4"
                        },
                        React.createElement(
                            "strong",
                            { className: "text-sm font-medium" },
                            "Audio:"
                        ),
                        React.createElement("audio", {
                            controls: true,
                            src: details.audioBlobUrl,
                            className: "h-8"
                        }),
                        React.createElement(
                            "a",
                            {
                                href: details.audioBlobUrl,
                                download: `${panel.title || "audio"}.mp3`,
                                className: "ml-2"
                            },
                            React.createElement(
                                "svg",
                                {
                                    width: 16,
                                    height: 16,
                                    fill: "currentColor",
                                    viewBox: "0 0 16 16",
                                    className:
                                        "text-blue-500 hover:text-blue-700"
                                },
                                React.createElement("path", {
                                    d: "M.5 9.9V14a1 1 0 0 0 1 1h13a1 1 0 0 0 1-1V9.9a.5.5 0 0 0-1 0V14H1V9.9a.5.5 0 0 0-1 0z"
                                }),
                                React.createElement("path", {
                                    d: "M4.646 6.646a.5.5 0 0 1 .708 0L8 9.293l2.646-2.647a.5.5 0 0 1 .708.708l-3 3a.5.5 0 0 1-.708 0l-3-3a.5.5 0 0 1 0-.708z"
                                }),
                                React.createElement("path", {
                                    d: "M8 1a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 1z"
                                })
                            )
                        ),
                        React.createElement(
                            "div",
                            {
                                className:
                                    "flex items-center space-x-2 justify-end"
                            },
                            renderStateIcon(details.audioProcessState),
                            React.createElement(
                                "span",
                                {
                                    className:
                                        details.audioProcessState === "failed"
                                            ? "text-danger"
                                            : ""
                                },
                                details.audioProcessState
                            )
                        )
                    ),
                React.createElement(
                    "div",
                    {
                        className:
                            "flex items-center justify-between w-full mb-4"
                    },
                    React.createElement(
                        "strong",
                        { className: "text-sm font-medium" },
                        "Transcript:"
                    ),
                    React.createElement(
                        "button",
                        {
                            onClick: toggleTranscriptVisibility,
                            className: "text-blue-500 hover:underline"
                        },
                        isTranscriptVisible
                            ? "Hide Transcript"
                            : "View Transcript"
                    ),
                    React.createElement(
                        "div",
                        { className: "flex items-center space-x-2" },
                        renderStateIcon(details.transcriptProcessState),
                        React.createElement(
                            "span",
                            {
                                className:
                                    details.transcriptProcessState === "failed"
                                        ? "text-danger"
                                        : ""
                            },
                            details.transcriptProcessState
                        )
                    )
                ),
                isTranscriptVisible &&
                    React.createElement(
                        "div",
                        { className: "mt-4" },
                        renderTranscript(transcriptContent)
                    )
            )
        )
    );
}

export default PanelDetails;
