import React from "react";
import { Form } from "react-bootstrap";

function ArticleCountComponent({ value, onChange }) {
    return (
        <div className="flex items-start mb-4 flex-col w-full">
            <label className="mb-1 self-start">Maximum news items</label>
            <div className="flex items-center w-full">
                <Form.Control
                    type="range"
                    min="1"
                    max="20"
                    value={value || "5"}
                    onChange={(e) => onChange(e.target.value)}
                    className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mr-4 flex-grow"
                />
                <span className="w-40 text-left">{value || 5}</span>
            </div>
        </div>
    );
}

export default ArticleCountComponent;
