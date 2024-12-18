import PanelDetailDisplay from "./PanelDetailDisplay.js";
import TranscriptDetailDisplay from "./TranscriptDetailDisplay.js";
const { Card } = ReactBootstrap;
const { Redirect, Link } = ReactRouterDOM; // Import Redirect

function PanelDetails({ panel, accessToken }) {
    const [details, setDetails] = React.useState({
        audioProcessState: "",
        audioFailMessage: "",
        transcriptProcessState: "",
        transcriptFailMessage: ""
    });
    const [transcripts, setTranscripts] = React.useState([]);
    const [audios, setAudios] = React.useState([]);
    const [transcriptUrls, setTranscriptUrls] = React.useState({});
    const [audioUrls, setAudioUrls] = React.useState({});
    const [redirectToEdit, setRedirectToEdit] = React.useState(false); // New state for redirection

    React.useEffect(() => {
        // Reset details, transcripts, and audios when panel changes
        setDetails({
            audioProcessState: "",
            audioFailMessage: "",
            transcriptProcessState: "",
            transcriptFailMessage: ""
        });
        setTranscripts([]);
        setAudios([]);
        setTranscriptUrls({});
        setAudioUrls({});

        fetch(`/public_panel/${panel.id}/files`, {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        })
            .then((response) => response.json())
            .then((data) => {
                const currentHost = window.location.host;
                const updatedTranscriptUrls = data.transcript_urls
                    ? Object.fromEntries(
                          Object.entries(data.transcript_urls).map(
                              ([id, url]) => [
                                  id,
                                  url.replace(
                                      "http://127.0.0.1",
                                      "http://" +
                                          currentHost.replace(":4000", "")
                                  )
                              ]
                          )
                      )
                    : {};
                const updatedAudioUrls = data.audio_urls
                    ? Object.fromEntries(
                          Object.entries(data.audio_urls).map(([id, url]) => [
                              id,
                              url.replace(
                                  "http://127.0.0.1",
                                  "http://" + currentHost.replace(":4000", "")
                              )
                          ])
                      )
                    : {};
                setTranscriptUrls(updatedTranscriptUrls);
                setAudioUrls(updatedAudioUrls);
            })
            .catch((error) =>
                console.error("Error fetching panel details:", error)
            );

        // Fetch audios
        fetch(
            `http://${window.location.hostname}:4000/public_panel/${panel.id}/audios`,
            {
                headers: {
                    Authorization: `Bearer ${accessToken}`
                }
            }
        )
            .then((response) => response.json())
            .then((data) => {
                setAudios(data);
                if (data.length === 0) {
                    setRedirectToEdit(true); // Set redirect if no audios
                } else {
                    const audio = data[0];
                    setDetails((prevDetails) => ({
                        ...prevDetails,
                        audioProcessState: audio.process_state || "",
                        audioFailMessage: audio.process_fail_message || ""
                    }));
                }
            })
            .catch((error) => console.error("Error fetching audios:", error));

        // Fetch transcripts
        fetch(
            `http://${window.location.hostname}:4000/public_panel/${panel.id}/transcripts`,
            {
                headers: {
                    Authorization: `Bearer ${accessToken}`
                }
            }
        )
            .then((response) => response.json())
            .then((data) => {
                setTranscripts(data);
                if (data.length === 0) {
                    setRedirectToEdit(true); // Set redirect if no transcripts
                } else {
                    const transcript = data[0];
                    setDetails((prevDetails) => ({
                        ...prevDetails,
                        transcriptProcessState: transcript.process_state || "",
                        transcriptFailMessage:
                            transcript.process_fail_message || ""
                    }));
                }
            })
            .catch((error) =>
                console.error("Error fetching transcripts:", error)
            );
    }, [panel, accessToken]);

    if (redirectToEdit) {
        return React.createElement(Redirect, { to: `/panel/${panel.id}/edit` });
    }

    return React.createElement(
        "div",
        { style: { maxHeight: "100vh", overflowY: "auto" } },
        React.createElement(
            "div",
            { className: "flex justify-between items-center" },
            React.createElement(
                Link,
                {
                    to: `/panel/${panel.id}/edit`,
                    className:
                        "btn btn-primary w-full py-2 mb-4 flex items-center"
                },
                "Edit Show"
            )
        ),
        React.createElement(
            Card,
            { className: "mb-3 shadow-lg" },
            React.createElement(
                Card.Body,
                null,
                React.createElement(PanelDetailDisplay, { panel }),
                transcripts.map((transcript) =>
                    React.createElement(
                        "div",
                        {
                            key: transcript.id,
                            className: "mb-4"
                        },
                        React.createElement(TranscriptDetailDisplay, {
                            transcript,
                            accessToken,
                            transcriptUrls,
                            audios,
                            audioUrls
                        })
                    )
                )
            )
        )
    );
}

export default PanelDetails;
