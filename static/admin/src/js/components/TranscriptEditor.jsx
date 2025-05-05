import React, { useState, useEffect, useMemo, useRef } from "react"; // Added useRef
import { Button, Dropdown, Spinner, Alert } from "react-bootstrap";
import { FaPlus, FaDownload, FaUpload, FaCheckCircle } from "react-icons/fa"; // Added icons
import TranscriptSpeakerTurn from "./TranscriptSpeakerTurn.jsx";
import {
    fetchTranscriptContent,
    updateTranscriptFile
} from "../helpers/fetch.js";

function TranscriptEditor({ transcript, transcriptUrls, onSaveSuccess }) {
    // --- Derived Data ---
    const transcriptId = transcript.id;
    const metadata = transcript.metadata || {};
    const personRoles = metadata.conversation_config?.person_roles || {};
    const transcriptHistory = metadata.transcript_history || [];
    const currentFileUrl = useMemo(
        () => transcriptUrls?.[transcriptId] || transcript.file || "",
        [transcriptUrls, transcriptId, transcript.file]
    );

    // --- State ---
    const [isEditMode, setIsEditMode] = useState(false);
    const [turns, setTurns] = useState([]); // Holds { _id, roleIndex, text, emote }
    const [isModified, setIsModified] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [selectedVersionUrl, setSelectedVersionUrl] =
        useState(currentFileUrl);
    const [rawContent, setRawContent] = useState("");
    const [isLoadingVersion, setIsLoadingVersion] = useState(true);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null); // Ref for hidden file input
    const [isSettingAsCurrent, setIsSettingAsCurrent] = useState(false); // State for Set as Current action

    // --- Parsing/Reconstruction Helpers ---
    const parseTranscriptContent = (content) => {
        if (!content) return [];
        // Basic check for XML structure - might need more robust parsing if format varies significantly
        const isXml = content.trim().startsWith("<");
        const segmentRegex = isXml
            ? /<person(\d+)(?:[^>]*emote="([^"]*)")?[^>]*>([^<]+)<\/person\1>/gi // Existing regex for XML-like structure
            : /^\[(\d+)(?::([^\]]+))?\]\s*(.*)$/gm; // Simple regex for potential plain text [speaker]: text

        const matches = [...content.matchAll(segmentRegex)];

        if (isXml) {
            return matches.map((match, index) => ({
                _id: `turn_${selectedVersionUrl}_${index}_${Date.now()}`,
                roleIndex: match[1] || "",
                emote: match[2] || "",
                text: match[3]?.trim() || ""
            }));
        } else {
            // Handle plain text format if needed, or return empty/error
            // This is a placeholder - adjust if plain text parsing is required
            console.warn(
                "Parsing non-XML content, format might not be fully supported."
            );
            return matches.map((match, index) => ({
                _id: `turn_${selectedVersionUrl}_${index}_${Date.now()}`,
                roleIndex: match[1] || "1", // Default speaker if not found
                emote: match[2] || "", // Emote might not exist in plain text
                text: match[3]?.trim() || ""
            }));
        }
    };

    const reconstructTranscriptContent = (currentTurns) => {
        return currentTurns
            .map(
                (turn) =>
                    `<person${turn.roleIndex}${turn.emote ? ` emote="${turn.emote}"` : ""}>${turn.text}</person${turn.roleIndex}>`
            )
            .join("\n");
    };

    // --- Fetching Logic ---
    const fetchContentForUrl = async (url) => {
        if (!url) {
            setRawContent("");
            setTurns([]);
            setIsLoadingVersion(false);
            setError("No transcript file URL found for this version.");
            return;
        }
        setIsLoadingVersion(true);
        setRawContent("");
        setTurns([]);
        setError(null);
        try {
            const text = await fetchTranscriptContent(url);
            setRawContent(text);
        } catch (fetchError) {
            console.error("Error fetching transcript content:", fetchError);
            setError(`Error loading transcript: ${fetchError.message}`);
            setRawContent("");
            setTurns([]);
        } finally {
            setSelectedVersionUrl((prevSelectedUrl) => {
                if (prevSelectedUrl === url) {
                    setIsLoadingVersion(false);
                }
                return prevSelectedUrl;
            });
        }
    };

    // --- Effects ---
    // Initialize or update selected URL when the main transcript URL changes
    useEffect(() => {
        if (currentFileUrl && currentFileUrl !== selectedVersionUrl) {
            setSelectedVersionUrl(currentFileUrl);
            // Fetching is handled by the next effect reacting to selectedVersionUrl change
        } else if (!currentFileUrl) {
            setIsLoadingVersion(false);
            setError("Transcript file URL not available.");
            setRawContent("");
            setTurns([]);
        }
    }, [currentFileUrl]);

    // Fetch content whenever selectedVersionUrl changes
    useEffect(() => {
        if (selectedVersionUrl) {
            fetchContentForUrl(selectedVersionUrl);
        } else {
            setIsLoadingVersion(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedVersionUrl]); // Only trigger fetch when the selected URL changes

    // Parse content whenever rawContent changes and there's no error
    useEffect(() => {
        if (rawContent && !error) {
            setTurns(parseTranscriptContent(rawContent));
        } else {
            setTurns([]); // Clear turns if no raw content or error
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [rawContent, error]); // Parse when raw content updates

    // --- Handlers ---
    const handleToggleEdit = () => {
        setError(null);
        const turningOff = isEditMode;
        setIsEditMode(!turningOff);
        if (turningOff) {
            setIsModified(false);
            // Re-fetch the content for the currently selected version to discard changes
            if (selectedVersionUrl) {
                fetchContentForUrl(selectedVersionUrl);
            } else {
                // If selectedVersionUrl is somehow empty (e.g., after upload cancel?), reset
                setRawContent("");
                setTurns([]);
            }
        } else {
            setIsModified(false); // Reset modified on entering edit mode
        }
    };

    const handleTurnUpdate = (index, field, value) => {
        setTurns((currentTurns) =>
            currentTurns.map((turn, i) =>
                i === index ? { ...turn, [field]: value } : turn
            )
        );
        setIsModified(true);
        setError(null);
    };

    const handleAddTurn = (index) => {
        const firstRoleKey = Object.keys(personRoles)[0] || "1";
        const newTurn = {
            _id: `turn_${Date.now()}_new_${Math.random()}`,
            roleIndex: firstRoleKey,
            text: "",
            emote: ""
        };
        setTurns((currentTurns) => [
            ...currentTurns.slice(0, index),
            newTurn,
            ...currentTurns.slice(index)
        ]);
        setIsModified(true);
        setError(null);
    };

    const handleDeleteTurn = (index) => {
        setTurns((currentTurns) => currentTurns.filter((_, i) => i !== index));
        setIsModified(true);
        setError(null);
    };

    const handleSaveChanges = async () => {
        setIsSaving(true);
        setError(null);
        const reconstructedContent = reconstructTranscriptContent(turns);
        try {
            const result = await updateTranscriptFile(
                transcriptId,
                reconstructedContent
            );
            if (result.success) {
                setIsModified(false);
                setIsEditMode(false);
                alert("Transcript saved successfully!");
                if (onSaveSuccess) {
                    onSaveSuccess(); // Notify parent to refresh
                }
            } else {
                console.error("Save failed:", result.error);
                setError(`Failed to save transcript: ${result.error}`);
            }
        } catch (saveError) {
            console.error("Error saving transcript:", saveError);
            setError(`An error occurred while saving: ${saveError.message}`);
        } finally {
            setIsSaving(false);
        }
    };

    const handleVersionSelect = (url) => {
        if (isEditMode && isModified) {
            if (
                !window.confirm(
                    "You have unsaved changes. Are you sure you want to switch versions and discard changes?"
                )
            ) {
                return;
            }
            setIsEditMode(false);
            setIsModified(false);
        }
        if (url !== selectedVersionUrl) {
            setSelectedVersionUrl(url); // This will trigger useEffect to fetch
        }
    };

    const handleSetAsCurrent = async () => {
        if (!selectedVersionUrl || selectedVersionUrl === currentFileUrl)
            return; // Should not happen if button is disabled correctly

        if (
            !window.confirm(
                `Are you sure you want to set the content of "${getFilename(selectedVersionUrl)}" as the new current version? This will save the currently displayed content.`
            )
        ) {
            return;
        }

        setIsSettingAsCurrent(true);
        setError(null);
        // Use the content currently loaded in the editor (from the selected version)
        const contentToUpload = reconstructTranscriptContent(turns);

        try {
            // Re-use the same update function, backend handles the logic
            const result = await updateTranscriptFile(
                transcriptId,
                contentToUpload
            );
            if (result.success) {
                setIsModified(false); // Reset modification state
                setIsEditMode(false); // Exit edit mode
                alert("Version set as current successfully!");
                if (onSaveSuccess) {
                    onSaveSuccess(); // Notify parent to refresh data
                }
                // The parent refresh should update currentFileUrl, which will update selectedVersionUrl via useEffect
            } else {
                console.error("Set as current failed:", result.error);
                setError(`Failed to set version as current: ${result.error}`);
            }
        } catch (saveError) {
            console.error("Error setting version as current:", saveError);
            setError(
                `An error occurred while setting version as current: ${saveError.message}`
            );
        } finally {
            setIsSettingAsCurrent(false);
        }
    };

    const handleDownload = () => {
        const content = reconstructTranscriptContent(turns);
        // Use selectedFilename if available, otherwise derive from URL, default to 'current'
        const baseFilename = getFilename(selectedVersionUrl) || "current";
        // Ensure it ends with .xml
        const filenameWithoutExt = baseFilename.replace(/\.[^/.]+$/, "");
        const filename = `transcript_${transcriptId}_${filenameWithoutExt}.xml`;

        const blob = new Blob([content], {
            type: "application/xml;charset=utf-8"
        }); // Changed type to xml
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    const handleUploadClick = () => {
        fileInputRef.current?.click(); // Trigger click on hidden input
    };

    const handleFileSelect = (event) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const text = e.target?.result;
            if (typeof text === "string") {
                setRawContent(text); // This triggers parsing useEffect
                setIsEditMode(true);
                setIsModified(true);
                setError(null);
                // Clear selected URL as it's now custom content from upload
                setSelectedVersionUrl("");
                alert(
                    "File content loaded into editor. Make any further changes and click 'Save Modifications'."
                );
            } else {
                setError("Failed to read file content.");
            }
        };
        reader.onerror = () => {
            setError("Error reading file.");
        };
        reader.readAsText(file);

        // Reset file input value so the same file can be uploaded again if needed
        event.target.value = null;
    };

    // --- Rendering ---
    const getFilename = (url) => {
        if (!url || typeof url !== "string") return "N/A";
        try {
            // Try parsing as URL first
            const urlObject = new URL(url);
            return urlObject.pathname.substring(
                urlObject.pathname.lastIndexOf("/") + 1
            );
        } catch (e) {
            // If it's not a full URL (e.g., just a path), get the last part
            const lastSlash = url.lastIndexOf("/");
            return lastSlash >= 0 ? url.substring(lastSlash + 1) : url;
        }
    };

    // Corrected URL construction and labeling for historical versions
    const versionsList = useMemo(() => {
        if (!currentFileUrl && transcriptHistory.length === 0) return [];

        // Determine the directory from the current URL if possible
        let directoryUrl = "";
        if (currentFileUrl) {
            const lastSlashIndex = currentFileUrl.lastIndexOf("/");
            if (lastSlashIndex !== -1) {
                directoryUrl = currentFileUrl.substring(0, lastSlashIndex + 1);
            }
        } else if (transcriptHistory.length > 0) {
            // If no current URL, try to infer directory from the first history item
            const firstHistoryPath = transcriptHistory[0];
            const lastSlashIndex = firstHistoryPath.lastIndexOf("/");
            if (lastSlashIndex !== -1) {
                directoryUrl = firstHistoryPath.substring(
                    0,
                    lastSlashIndex + 1
                );
            }
        }

        const validHistory = transcriptHistory.filter(
            (item) => typeof item === "string" && item.length > 0
        );

        // Use a Map to handle potential duplicates and easily identify the latest
        const versionMap = new Map();

        // Add historical versions
        validHistory.forEach((historyPath) => {
            const historyFilename = getFilename(historyPath); // Use getFilename for consistency
            // Construct full URL only if directory is known
            const fullHistoricalUrl = directoryUrl
                ? `${directoryUrl}${historyFilename}`
                : historyPath;
            // Use the path itself as the key if URL construction fails
            versionMap.set(fullHistoricalUrl, {
                url: fullHistoricalUrl,
                label: `History: ${historyFilename}` // Simple history label
            });
        });

        // Add/update the current version entry
        if (currentFileUrl) {
            versionMap.set(currentFileUrl, {
                url: currentFileUrl,
                label: `Latest: ${getFilename(currentFileUrl)}`
            });
        }

        // Convert map values back to an array
        const uniqueVersions = Array.from(versionMap.values());

        // Sort: Put "Latest" first, then sort others by filename (descending version number if possible)
        uniqueVersions.sort((a, b) => {
            if (a.label.startsWith("Latest")) return -1;
            if (b.label.startsWith("Latest")) return 1;

            // Attempt to extract version numbers for sorting (e.g., from transcript_vN.xml)
            const matchA = a.label.match(/_v(\d+)\.xml$/);
            const matchB = b.label.match(/_v(\d+)\.xml$/);
            const versionA = matchA ? parseInt(matchA[1], 10) : NaN;
            const versionB = matchB ? parseInt(matchB[1], 10) : NaN;

            if (!isNaN(versionA) && !isNaN(versionB)) {
                return versionB - versionA; // Sort descending by version number
            }

            // Fallback: alphabetical sort on label if version numbers aren't present/parseable
            return a.label.localeCompare(b.label);
        });

        return uniqueVersions;
    }, [transcriptHistory, currentFileUrl]);

    const selectedFilename = getFilename(selectedVersionUrl);
    const isSelectedLatest = selectedVersionUrl === currentFileUrl;

    const wordCount = useMemo(() => {
        if (isLoadingVersion || error || !turns) return 0;
        const contentToCount = reconstructTranscriptContent(turns);
        // More robust word count - handles multiple spaces, newlines etc.
        return contentToCount
            .replace(/<[^>]+>/g, " ") // Replace tags with space
            .replace(/[^\w\s]|_/g, "") // Remove punctuation
            .trim()
            .split(/\s+/)
            .filter(Boolean).length;
    }, [isLoadingVersion, error, turns]); // Removed reconstructTranscriptContent dependency as it's stable

    return (
        <div>
            {/* Controls: Version Dropdown, Edit Toggle, Save Button */}
            <div className="mb-3 flex flex-wrap justify-between items-center gap-2">
                {/* Version Dropdown Area */}
                {versionsList.length > 0 && ( // Show dropdown only if there are versions
                    <div
                        className={`flex items-center ${isEditMode && isModified ? "opacity-50 pointer-events-none" : ""}`}
                        title={
                            isEditMode && isModified
                                ? "Save or cancel edits to change version"
                                : ""
                        }
                    >
                        <span className="mr-2 text-sm font-medium">
                            Version:
                        </span>
                        <Dropdown onSelect={handleVersionSelect}>
                            <Dropdown.Toggle
                                variant="outline-secondary"
                                size="sm"
                                id="dropdown-transcript-version"
                                disabled={isEditMode && isModified} // Disable dropdown itself when modified
                                className="max-w-[300px] text-truncate" // Prevent long filenames breaking layout
                            >
                                {selectedFilename !== "N/A"
                                    ? selectedFilename
                                    : "Select Version"}
                                {isSelectedLatest && " (Latest)"}
                                {isEditMode && isModified && " (modified)"}
                            </Dropdown.Toggle>
                            <Dropdown.Menu className="max-h-[200px] overflow-y-auto">
                                {versionsList.map((version) => (
                                    <Dropdown.Item
                                        key={version.url}
                                        eventKey={version.url}
                                        active={
                                            selectedVersionUrl === version.url
                                        }
                                        title={version.label} // Show full label on hover
                                    >
                                        {version.label}
                                    </Dropdown.Item>
                                ))}
                            </Dropdown.Menu>
                        </Dropdown>
                        {/* "Set as Current" Button */}
                        {selectedVersionUrl &&
                            !isSelectedLatest &&
                            !isEditMode && (
                                <Button
                                    variant="outline-primary"
                                    size="sm"
                                    onClick={handleSetAsCurrent}
                                    disabled={
                                        isLoadingVersion ||
                                        isSaving ||
                                        isSettingAsCurrent
                                    }
                                    title={`Set the content of ${selectedFilename} as the new current version`}
                                    className="ml-2 flex items-center gap-1"
                                >
                                    {isSettingAsCurrent ? (
                                        <>
                                            <Spinner
                                                animation="border"
                                                size="sm"
                                                className="mr-1"
                                            />
                                            Setting...
                                        </>
                                    ) : (
                                        <>
                                            <FaCheckCircle size="0.9em" /> Set
                                            as Current
                                        </>
                                    )}
                                </Button>
                            )}
                    </div>
                )}
                {/* Spacer or Word Count */}
                <div className="flex-grow text-center text-sm text-gray-500 px-2">
                    {wordCount > 0 && `Word Count: ${wordCount}`}
                </div>

                {/* Action Buttons Area */}
                <div className="flex items-center gap-2">
                    {/* Hidden File Input */}
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileSelect}
                        accept=".xml,text/xml,.txt,text/plain" // Accept XML and TXT
                        style={{ display: "none" }}
                    />
                    {/* Download Button */}
                    <Button
                        variant="outline-info"
                        size="sm"
                        onClick={handleDownload}
                        disabled={
                            isLoadingVersion ||
                            !!error ||
                            turns.length === 0 ||
                            isSettingAsCurrent
                        }
                        title={
                            turns.length === 0
                                ? "Cannot download empty transcript"
                                : "Download current transcript content as XML"
                        }
                        className="flex items-center gap-1"
                    >
                        <FaDownload size="0.9em" /> Download XML
                    </Button>
                    {/* Upload Button */}
                    <Button
                        variant="outline-success"
                        size="sm"
                        onClick={handleUploadClick}
                        disabled={
                            isLoadingVersion || isSaving || isSettingAsCurrent
                        }
                        title="Upload a .xml or .txt transcript file to edit"
                        className="flex items-center gap-1"
                    >
                        <FaUpload size="0.9em" /> Upload & Edit
                    </Button>
                    {/* Edit/Cancel Button */}
                    <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={handleToggleEdit}
                        disabled={
                            isLoadingVersion ||
                            isSaving ||
                            !!error ||
                            isSettingAsCurrent
                        }
                        title={
                            error
                                ? "Cannot edit while content failed to load"
                                : isSettingAsCurrent
                                  ? "Cannot edit while setting version"
                                  : ""
                        }
                    >
                        {isEditMode ? "Cancel Edit" : "Edit Transcript"}
                    </Button>
                    {/* Save Modifications Button */}
                    {isEditMode && isModified && (
                        <Button
                            variant="primary"
                            size="sm"
                            onClick={handleSaveChanges}
                            disabled={
                                isSaving ||
                                isLoadingVersion ||
                                isSettingAsCurrent
                            }
                        >
                            {isSaving ? (
                                <>
                                    <Spinner
                                        as="span"
                                        animation="border"
                                        size="sm"
                                        role="status"
                                        aria-hidden="true"
                                        className="mr-1"
                                    />
                                    Saving...
                                </>
                            ) : (
                                "Save Modifications"
                            )}
                        </Button>
                    )}
                </div>
            </div>

            {/* Error Display */}
            {error && <Alert variant="danger">{error}</Alert>}

            {/* Transcript Content Area */}
            <div className="transcript-content-area border p-3 bg-gray-100 rounded min-h-[200px] max-h-[60vh] overflow-y-auto">
                {isLoadingVersion ? (
                    <div className="text-center p-5">
                        <Spinner animation="border" role="status">
                            <span className="sr-only">Loading...</span>
                        </Spinner>
                    </div>
                ) : error ? (
                    <p className="text-center p-5 text-red-500">
                        Could not load transcript content. Check file format or
                        network.
                    </p>
                ) : turns.length > 0 ? (
                    // Always render turns using TranscriptSpeakerTurn, passing isEditMode
                    <div>
                        {turns.map((turn, index) => (
                            <TranscriptSpeakerTurn
                                key={turn._id} // Use stable unique ID from parsing
                                turnData={turn}
                                index={index}
                                isEditMode={isEditMode} // Pass edit mode status down
                                personRoles={personRoles}
                                onUpdate={handleTurnUpdate}
                                onDelete={handleDeleteTurn}
                                onAdd={handleAddTurn}
                            />
                        ))}
                        {/* Add Turn button only in edit mode */}
                        {isEditMode && (
                            <Button
                                variant="outline-success"
                                size="sm"
                                onClick={() => handleAddTurn(turns.length)}
                                className="mt-2 flex items-center gap-1"
                            >
                                <FaPlus size="0.8em" /> Add Turn at End
                            </Button>
                        )}
                    </div>
                ) : (
                    // No turns parsed and not loading/error
                    <p className="text-center p-5 text-gray-500">
                        Transcript is empty or could not be parsed. Try
                        uploading a valid XML or TXT file.
                    </p>
                )}
            </div>
        </div>
    );
}

export default TranscriptEditor;
