import React, { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";
import { FaTrash, FaPlus } from "react-icons/fa";

function TranscriptSpeakerTurn({
    turnData, // Expects { _id, roleIndex, text, emote }
    index,
    isEditMode,
    personRoles, // Expects { "1": { name: "..." }, ... }
    onUpdate, // Expects (index, field: 'roleIndex' | 'text' | 'emote', value)
    onDelete,
    onAdd
}) {
    // State for editable fields
    const [roleIndex, setRoleIndex] = useState(turnData.roleIndex || ""); // Use roleIndex
    const [content, setContent] = useState(turnData.text || ""); // Internal state named content
    const [emote, setEmote] = useState(turnData.emote || "");

    // Update local state if turnData prop changes
    useEffect(() => {
        setRoleIndex(turnData.roleIndex || "");
        setContent(turnData.text || "");
        setEmote(turnData.emote || "");
    }, [turnData]);

    // Handles changes in any editable field
    const handleFieldChange = (field, value) => {
        let parentField = field; // Field name to notify parent with
        // Update local state
        if (field === "roleIndex") {
            setRoleIndex(value);
        } else if (field === "content") {
            setContent(value);
            parentField = "text"; // Notify parent about 'text' field change
        } else if (field === "emote") {
            setEmote(value);
        }
        // Notify parent component
        onUpdate(index, parentField, value);
    };

    // Derive speaker name for view mode using roleIndex
    const getSpeakerName = (idx) => {
        if (!idx) return "Unknown";
        return personRoles?.[idx]?.name || `Person ${idx}`; // Fallback to Person + index
    };

    if (!isEditMode) {
        // --- View Mode ---
        return (
            <div className="flex mb-2 border-b pb-2">
                <span className="font-semibold text-blue-600 mr-3 min-w-[80px] flex-shrink-0">
                    {getSpeakerName(turnData.roleIndex)}
                </span>
                <span className="flex-1">
                    {turnData.text} {/* Display original text prop */}
                    {turnData.emote && (
                        <div className="text-gray-400 ml-1">
                            - {turnData.emote}
                        </div>
                    )}
                </span>
            </div>
        );
    } else {
        // --- Edit Mode ---
        return (
            <div className="mb-3 p-3 border rounded bg-white shadow-sm relative">
                {/* Action Buttons */}
                <div className="absolute top-1 right-1 flex gap-1">
                    <Button
                        variant="outline-success"
                        size="sm"
                        onClick={() => onAdd(index)}
                        title="Add turn before this"
                        className="p-1 leading-none"
                    >
                        <FaPlus size="0.8em" />
                    </Button>
                    <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => onDelete(index)}
                        title="Delete this turn"
                        className="p-1 leading-none"
                    >
                        <FaTrash size="0.8em" />
                    </Button>
                </div>

                {/* Speaker Dropdown (using roleIndex) */}
                <Form.Group
                    controlId={`turn-${index}-roleIndex`}
                    className="mb-2"
                >
                    <Form.Label className="text-xs font-medium">
                        Speaker
                    </Form.Label>
                    <Form.Select
                        size="sm"
                        value={roleIndex} // Bind value to roleIndex state
                        onChange={(e) =>
                            handleFieldChange("roleIndex", e.target.value)
                        }
                        className="text-sm"
                    >
                        <option value="">Select Speaker</option>
                        {Object.entries(personRoles || {}).map(
                            ([key, roleDetails]) => (
                                <option
                                    key={key}
                                    value={key} // Value is the role index ("1", "2", etc.)
                                >
                                    {`Person ${key}: ${roleDetails.name || "Unnamed"}`}
                                </option>
                            )
                        )}
                    </Form.Select>
                </Form.Group>

                {/* Content (Textarea) */}
                <Form.Group
                    controlId={`turn-${index}-content`}
                    className="mb-2"
                >
                    <Form.Label className="text-xs font-medium">
                        Content
                    </Form.Label>
                    <Form.Control
                        as="textarea"
                        rows={3}
                        value={content} // Bind value to content state
                        onChange={(e) =>
                            handleFieldChange("content", e.target.value)
                        }
                        className="text-sm"
                    />
                </Form.Group>

                {/* Emote (Moved below Content) */}
                <Form.Group controlId={`turn-${index}-emote`}>
                    <Form.Label className="text-xs font-medium">
                        Emote (Optional)
                    </Form.Label>
                    <Form.Control
                        type="text"
                        size="sm"
                        value={emote}
                        onChange={(e) =>
                            handleFieldChange("emote", e.target.value)
                        }
                        placeholder="e.g., excited"
                        className="text-sm"
                    />
                </Form.Group>
            </div>
        );
    }
}

export default TranscriptSpeakerTurn;
