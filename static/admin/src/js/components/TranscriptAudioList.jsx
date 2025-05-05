import React from "react";
import DetailAccordion from "./DetailAccordion.jsx";
import AudioDetailDisplay from "../AudioDetailDisplay.jsx"; // Adjust path as needed
import RemoveButton from "./RemoveButton.jsx";
import { showConfirmationDialog, handleDeleteItem } from "../helpers/panel.js"; // Import handleDeleteItem

// Accepts audios array, audioUrls map, and a callback for when an action completes
function TranscriptAudioList({ audios, audioUrls, onActionComplete }) {
    if (!audios || audios.length === 0) {
        return <p>No audio generated for this transcript yet.</p>;
    }

    // Internal handler for deletion confirmation
    const handleDelete = (audioId) => {
        showConfirmationDialog(
            "Are you sure you want to delete this audio? This action cannot be undone.",
            () => {
                // Call the imported handleDeleteItem helper, passing the parent's callback
                handleDeleteItem(
                    { type: "audio", id: audioId },
                    onActionComplete
                );
            }
        );
    };

    return (
        <DetailAccordion
            items={audios}
            itemKey="id"
            renderHeader={(audio) => audio.title || `Audio ${audio.id}`}
            renderBody={(audio) => {
                // Look up the URL from the passed map
                const audioUrl = audioUrls[audio.id];

                return (
                    <div className="relative">
                        <RemoveButton
                            onClick={() => handleDelete(audio.id)} // Use internal handler
                            className="absolute top-0 right-0 m-2"
                            ariaLabel="Delete Audio"
                            size="sm"
                        />
                        <AudioDetailDisplay
                            audio={audio}
                            audioUrl={audioUrl} // Pass looked-up URL
                        />
                    </div>
                );
            }}
            className="mt-0" // Remove default top margin if nested
        />
    );
}

export default TranscriptAudioList;
