import PanelDetailDisplay from "./PanelDetailDisplay.jsx";
import TranscriptDetailDisplay from "./TranscriptDetailDisplay.jsx";
import { fetchPanelTranscripts } from "./helpers/fetch.js";
import { showConfirmationDialog, handleDeleteItem } from "./helpers/panel.js";
import { Button, Card } from "react-bootstrap"; // Removed Accordion import
import { Navigate, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { FaClock, FaRegStar, FaSyncAlt } from "react-icons/fa"; // Removed FaTimes

// Import shared components
import DetailAccordion from "./components/DetailAccordion.jsx";
import RemoveButton from "./components/RemoveButton.jsx";

function PanelDetails({ panel }) {
    const [transcripts, setTranscripts] = useState([]);
    const [redirectToEdit, setRedirectToEdit] = useState(false);

    useEffect(() => {
        setTranscripts([]); // Clear previous transcripts

        fetchPanelTranscripts(panel.id)
            .then((data) => {
                if (data && data.length > 0) {
                    // Check if data is valid
                    const sortedData = data.sort(
                        (a, b) =>
                            new Date(b.created_at) - new Date(a.created_at)
                    );
                    setTranscripts(sortedData);
                } else {
                    setTranscripts([]); // Ensure transcripts is an array
                    setRedirectToEdit(true); // Redirect if no transcripts found
                }
            })
            .catch((error) => {
                console.error("Error fetching transcripts:", error);
                setTranscripts([]); // Ensure transcripts is an array on error
            });
    }, [panel.id]); // Depend only on panel.id

    const refreshTranscripts = () => {
        fetchPanelTranscripts(panel.id)
            .then((data) => {
                if (data && data.length > 0) {
                    const sortedData = data.sort(
                        (a, b) =>
                            new Date(b.created_at) - new Date(a.created_at)
                    );
                    setTranscripts(sortedData);
                } else {
                    setTranscripts([]);
                }
            })
            .catch((error) => {
                console.error("Error refreshing transcripts:", error);
                setTranscripts([]);
            });
    };

    // Renamed for clarity
    const handleDeleteTranscript = (transcriptId) => {
        handleDeleteItem(
            { type: "transcript", id: transcriptId },
            refreshTranscripts
        );
    };

    if (redirectToEdit) {
        return <Navigate to={`/panel/${panel.id}/edit`} />;
    }

    // --- Render Functions for DetailAccordion ---
    const renderTranscriptHeader = (transcript, index) => (
        <div className="d-flex justify-content-between align-items-center w-100">
            {/* Left side: Status Icons */}
            <div
                className="flex-shrink-0 me-3 d-flex flex-column align-items-center"
                style={{ width: "20px" }}
            >
                {transcript.transcript_parent_id && (
                    <FaSyncAlt
                        className="text-blue-500 mb-1"
                        title="Recurring Generation"
                        size="0.9em"
                    />
                )}
                {!transcript.transcript_parent_id &&
                    (transcript.generation_cronjob ? (
                        <FaClock
                            className="text-green-500 mb-1"
                            title="Scheduled Generation"
                            size="0.9em"
                        />
                    ) : (
                        <FaRegStar
                            className="text-gray-500 mb-1"
                            title="No Update Cycle"
                            size="0.9em"
                        />
                    ))}
            </div>

            {/* Middle: Title */}
            <div className="flex-grow-1 text-start mx-2">
                {`Transcript ${transcripts.length - index}`}:{" "}
                {transcript.title || `ID: ${transcript.id.substring(0, 6)}`}
            </div>

            {/* Right side: Remove Button */}
            <div className="flex-shrink-0 ms-2">
                <RemoveButton
                    onClick={(e) => {
                        e.stopPropagation(); // Prevent accordion toggle
                        showConfirmationDialog(
                            "Are you sure you want to delete this transcript? This action cannot be undone.",
                            () => handleDeleteTranscript(transcript.id)
                        );
                    }}
                    ariaLabel="Delete Transcript"
                    size="sm"
                />
            </div>
        </div>
    );

    const renderTranscriptBody = (transcript) => (
        <TranscriptDetailDisplay transcript={transcript} />
    );

    // --- Main Render ---
    return (
        // Removed max-h-screen overflow-y-auto, let parent handle scrolling if needed
        <div>
            <div className="d-flex justify-content-between gap-2 mb-4">
                <Button
                    variant="secondary"
                    href={`/player/panel/${panel.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-grow-1 py-2 d-flex align-items-center justify-content-center"
                >
                    View in Player
                </Button>
                <Button
                    as={Link} // Use Link component for internal navigation
                    to={`/panel/${panel.id}/edit`}
                    variant="primary"
                    className="flex-grow-1 py-2 d-flex align-items-center justify-content-center"
                >
                    Edit Show
                </Button>
            </div>
            <Card className="mb-3 shadow-lg">
                <Card.Body>
                    <PanelDetailDisplay panel={panel} />

                    <h4 className="mt-4 mb-3">Transcripts</h4>
                    {transcripts.length > 0 ? (
                        <DetailAccordion
                            items={transcripts}
                            itemKey="id"
                            renderHeader={renderTranscriptHeader}
                            renderBody={renderTranscriptBody}
                            defaultActiveKey={transcripts[0]?.id} // Open first transcript by ID
                        />
                    ) : (
                        <p className="text-muted">
                            No transcripts found for this panel.
                        </p>
                    )}
                </Card.Body>
            </Card>
        </div>
    );
}

export default PanelDetails;
