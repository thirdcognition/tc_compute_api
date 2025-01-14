import PanelDetailDisplay from "./PanelDetailDisplay.jsx";
import TranscriptDetailDisplay from "./TranscriptDetailDisplay.jsx";
import { fetchPanelTranscripts } from "./helpers/fetch.js";
import { Card } from "react-bootstrap";
import { Navigate, Link } from "react-router-dom";
import { useState, useEffect } from "react";

function PanelDetails({ panel }) {
    const [transcripts, setTranscripts] = useState([]);
    const [redirectToEdit, setRedirectToEdit] = useState(false);

    useEffect(() => {
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
        return <Navigate to={`/panel/${panel.id}/edit`} />;
    }

    return (
        <div className="max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center">
                <Link
                    to={`/panel/${panel.id}/edit`}
                    className="btn btn-primary w-full py-2 mb-4 flex items-center"
                >
                    Edit Show
                </Link>
            </div>
            <Card className="mb-3 shadow-lg">
                <Card.Body>
                    <PanelDetailDisplay panel={panel} />
                    {transcripts.map((transcript) => (
                        <div key={transcript.id} className="mb-4">
                            <TranscriptDetailDisplay transcript={transcript} />
                        </div>
                    ))}
                </Card.Body>
            </Card>
        </div>
    );
}

export default PanelDetails;
