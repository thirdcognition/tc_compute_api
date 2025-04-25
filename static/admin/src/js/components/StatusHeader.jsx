import React from "react";
import { FaCalendarAlt, FaClock } from "react-icons/fa";
import { processStateIcon } from "../helpers/ui.js"; // Assuming helper is in this path

/**
 * Displays a standard header with process state icon and created/updated timestamps.
 */
const StatusHeader = ({ item }) => {
    if (!item) {
        return null; // Don't render if no item data
    }

    const { process_state, created_at, updated_at } = item;

    return (
        <div className="flex items-center mb-3 text-muted small">
            <span
                className="me-3"
                title={`Status: ${process_state || "unknown"}`}
            >
                {processStateIcon(process_state)}
            </span>
            {created_at && (
                <div class="flex-1 self-center">
                    <FaCalendarAlt className="me-1 inline-block" />
                    <span>
                        Created: {new Date(created_at).toLocaleString()}
                    </span>
                </div>
            )}
            {updated_at && (
                <div class="flex-1 self-center">
                    <FaClock className="me-1 inline-block" />
                    <span>
                        Updated: {new Date(updated_at).toLocaleString()}
                    </span>
                </div>
            )}
        </div>
    );
};

export default StatusHeader;
