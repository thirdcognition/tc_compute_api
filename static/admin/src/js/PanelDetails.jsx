import PanelDetailDisplay from "./PanelDetailDisplay.jsx";
import TranscriptDetailDisplay from "./TranscriptDetailDisplay.jsx";
import { fetchPanelTranscripts } from "./helpers/fetch.js";
import { showConfirmationDialog, handleDeleteItem } from "./helpers/panel.js";
import { Card } from "react-bootstrap";
import { Navigate, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { FaTrash } from "react-icons/fa";

function PanelDetails({ panel }) {
    const [transcripts, setTranscripts] = useState([]);
    const [redirectToEdit, setRedirectToEdit] = useState(false);

    useEffect(() => {
        setTranscripts([]);

        fetchPanelTranscripts(panel.id)
            .then((data) => {
                const sortedData = data.sort(
                    (a, b) => new Date(b.created_at) - new Date(a.created_at)
                );
                setTranscripts(sortedData);
                if (data.length === 0) {
                    setRedirectToEdit(true);
                }
            })
            .catch((error) =>
                console.error("Error fetching transcripts:", error)
            );
    }, [panel]);

    const refreshTranscripts = () => {
        fetchPanelTranscripts(panel.id)
            .then((data) => {
                const sortedData = data.sort(
                    (a, b) => new Date(b.created_at) - new Date(a.created_at)
                );
                setTranscripts(sortedData);
            })
            .catch((error) =>
                console.error("Error refreshing transcripts:", error)
            );
    };

    const handleDelete = (deleteTarget) => {
        handleDeleteItem(deleteTarget, refreshTranscripts);
    };

    if (redirectToEdit) {
        return <Navigate to={`/panel/${panel.id}/edit`} />;
    }

    return (
        <div className="max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center text-center">
                <a
                    href={`/player/panel/${panel.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary w-full py-2 mb-4 flex items-center justify-center mr-2"
                >
                    View in Player
                </a>
                <Link
                    to={`/panel/${panel.id}/edit`}
                    className="btn btn-primary w-full py-2 mb-4 flex items-center justify-center"
                >
                    Edit Show
                </Link>
            </div>
            <Card className="mb-3 shadow-lg">
                <Card.Body>
                    <PanelDetailDisplay panel={panel} />
                    {transcripts.map((transcript) => (
                        <div key={transcript.id} className="mb-4 relative">
                            <button
                                onClick={() =>
                                    showConfirmationDialog(
                                        "Are you sure you want to delete this transcript? This action cannot be undone.",
                                        () =>
                                            handleDelete({
                                                type: "transcript",
                                                id: transcript.id
                                            })
                                    )
                                }
                                className="absolute top-0 right-0 p-2 text-red-500 hover:text-red-700"
                                aria-label="Delete Transcript"
                            >
                                <FaTrash />
                            </button>
                            <TranscriptDetailDisplay transcript={transcript} />
                        </div>
                    ))}
                </Card.Body>
            </Card>
        </div>
    );
}

export default PanelDetails;
