import React from "react";
import { Form, Card } from "react-bootstrap";

function ArticleReleasedWithinComponent({ value, onChange }) {
    const convertHoursToTimeFormat = (hours) => {
        const days = Math.floor(hours / 24);
        const remainingHours = hours % 24;
        const months = Math.floor(days / 30);
        const remainingDays = days % 30;
        let result = "";
        if (months > 0) result += `${months}m `;
        if (remainingDays > 0) result += `${remainingDays}d `;
        if (remainingHours > 0) result += `${remainingHours}h`;
        return result.trim();
    };

    const convertTimeFormatToHours = (timeFormat) => {
        if (typeof timeFormat !== "string") {
            if (timeFormat == null) return "";

            console.error(
                "Expected a string for timeFormat, but received:",
                timeFormat
            );
            return 0; // or handle the error as needed
        }
        const timeParts = timeFormat.split(" ");
        let totalHours = 0;
        timeParts.forEach((part) => {
            if (part.endsWith("m")) {
                totalHours += parseInt(part) * 30 * 24;
            } else if (part.endsWith("d")) {
                totalHours += parseInt(part) * 24;
            } else if (part.endsWith("h")) {
                totalHours += parseInt(part);
            }
        });
        return totalHours;
    };

    return (
        <Card className="mb-4 w-full">
            <Card.Header>Article has to be released within</Card.Header>
            <Card.Body>
                <div className="flex items-start w-full">
                    <Form.Control
                        type="range"
                        min="0"
                        max={24 * 7} // 2 months in hours
                        value={convertTimeFormatToHours(value) || "0"}
                        onChange={(e) =>
                            onChange(convertHoursToTimeFormat(e.target.value))
                        }
                        className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mr-4 flex-grow"
                    />
                    <span className="w-40 text-left">{value || "Not set"}</span>
                </div>
            </Card.Body>
        </Card>
    );
}

export default ArticleReleasedWithinComponent;
