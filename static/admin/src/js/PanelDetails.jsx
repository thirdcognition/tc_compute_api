import PanelDetailDisplay from "./PanelDetailDisplay.jsx";
import TranscriptDetailDisplay from "./TranscriptDetailDisplay.jsx";
import { fetchPanelTranscripts } from "./helpers/fetch.js";
import { showConfirmationDialog, handleDeleteItem } from "./helpers/panel.js";
import { Accordion, Button, Card } from "react-bootstrap";
import { Navigate, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import { FaTimes, FaClock, FaRegStar, FaSyncAlt } from "react-icons/fa";
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

    console.log(transcripts);

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
                    <Accordion defaultActiveKey="0">
                        {transcripts.map((transcript, index) => (
                            <Accordion.Item
                                eventKey={index.toString()}
                                key={transcript.id}
                            >
                                <Accordion.Header>
                                    <div class="flex justify-between items-center w-full pr-4">
                                        <div className="flex-none flex flex-col items-center gap-2">
                                            {transcript.transcript_parent_id && (
                                                <FaSyncAlt
                                                    className="inline-block mr-2 text-blue-500"
                                                    title="Recurring Generation"
                                                />
                                            )}
                                            {!transcript.transcript_parent_id &&
                                                (transcript.generation_cronjob ? (
                                                    <FaClock
                                                        className="inline-block mr-2 text-green-500"
                                                        title="Scheduled Generation"
                                                    />
                                                ) : (
                                                    <FaRegStar
                                                        className="inline-block mr-2 text-gray-500"
                                                        title="No Update Cycle"
                                                    />
                                                ))}
                                        </div>
                                        <div class="flex-1">
                                            {`Transcript ${transcripts.length - index}`}
                                            : {transcript.title}
                                        </div>
                                        <Button
                                            className="flex-none"
                                            variant="danger"
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
                                            aria-label="Delete Transcript"
                                        >
                                            <FaTimes className="inline-block" />
                                        </Button>
                                    </div>
                                </Accordion.Header>
                                <Accordion.Body>
                                    <TranscriptDetailDisplay
                                        transcript={transcript}
                                    />
                                </Accordion.Body>
                            </Accordion.Item>
                        ))}
                    </Accordion>
                </Card.Body>
            </Card>
        </div>
    );
}

export default PanelDetails;
