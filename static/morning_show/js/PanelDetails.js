import PanelDetailDisplay from "./PanelDetailDisplay.js";
import TranscriptDetailDisplay from "./TranscriptDetailDisplay.js";
import { fetchPanelTranscripts } from "./helpers/fetch.js";
const { Card } = ReactBootstrap;
const { Redirect, Link } = ReactRouterDOM;

function PanelDetails({ panel }) {
    const [transcripts, setTranscripts] = React.useState([]);
    const [redirectToEdit, setRedirectToEdit] = React.useState(false);

    React.useEffect(() => {
        setTranscripts([]);

        fetchPanelTranscripts(panel.id)
            .then((data) => {
                setTranscripts(data);
                if (data.length === 0) {
                    setRedirectToEdit(true);
                }
            })
            .catch((error) =>
                console.error("Error fetching transcripts:", error)
            );
    }, [panel]);

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
                            transcript
                        })
                    )
                )
            )
        )
    );
}

export default PanelDetails;
