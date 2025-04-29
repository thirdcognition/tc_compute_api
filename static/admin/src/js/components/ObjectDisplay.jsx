import React from "react";

/**
 * Recursively renders nested objects or arrays into an unordered list.
 * Handles basic data types (string, number, boolean).
 */
const ObjectDisplay = ({ data }) => {
    // console.log("display data", data);
    if (data === null || data === undefined) {
        return <span className="text-muted">N/A</span>;
    }

    if (typeof data !== "object" || Array.isArray(data)) {
        // Handle arrays or simple values directly
        if (Array.isArray(data)) {
            return data.length > 0 ? (
                data.join(", ")
            ) : (
                <span className="text-muted">empty</span>
            );
        }
        // Handle boolean explicitly
        if (typeof data === "boolean") {
            return data ? "Yes" : "No";
        }
        // Other primitives
        return String(data);
    }

    // Handle objects
    const entries = Object.entries(data);
    if (entries.length === 0) {
        return <span className="text-muted">empty object</span>;
    }

    return (
        <ul className="list-unstyled mb-0 ms-3">
            {" "}
            {/* Use list-unstyled and add margin */}
            {entries.map(([key, value]) => (
                <li key={key}>
                    <strong>{key}:</strong> {/* Recursively render the value */}
                    <ObjectDisplay data={value} />
                </li>
            ))}
        </ul>
    );
};

export default ObjectDisplay;
