import React from "react";
import SectionCard from "./SectionCard.jsx";
import { getWordCountDescription } from "../helpers/ui.js";

function TranscriptConfigDetails({ config, metadata }) {
    // Ensure config and metadata are objects to prevent errors
    const safeConfig = config || {};
    const safeMetadata = metadata || {};

    return (
        <>
            {safeConfig.word_count && (
                <SectionCard title="Length">
                    <p>
                        {getWordCountDescription(safeConfig.word_count, 4000)}
                    </p>
                </SectionCard>
            )}
            {safeConfig.conversation_style?.length > 0 && (
                <SectionCard title="Conversation Style">
                    <p>{safeConfig.conversation_style.join(", ")}</p>
                </SectionCard>
            )}
            {safeConfig.dialogue_structure?.length > 0 && (
                <SectionCard title="Dialogue Structure">
                    <p>{safeConfig.dialogue_structure.join(" → ")}</p>
                </SectionCard>
            )}
            {safeConfig.engagement_techniques?.length > 0 && (
                <SectionCard title="Engagement Techniques">
                    <p>{safeConfig.engagement_techniques.join(", ")}</p>
                </SectionCard>
            )}
            {safeConfig.user_instructions && (
                <SectionCard title="User Instructions">
                    <p>{safeConfig.user_instructions}</p>
                </SectionCard>
            )}
            {safeConfig.output_language && (
                <SectionCard title="Output Language">
                    <p>{safeConfig.output_language}</p>
                </SectionCard>
            )}
            <SectionCard title="Transcript Processing Options">
                <p>
                    <strong>Process every article separately:</strong>{" "}
                    {safeMetadata.longform ? "Yes" : "No"}
                </p>
                <p>
                    <strong>Use short intro/conclusion:</strong>{" "}
                    {safeConfig.short_intro_and_conclusion ? "Yes" : "No"}
                </p>
                <p>
                    <strong>Disable intro/conclusion:</strong>{" "}
                    {safeConfig.disable_intro_and_conclusion ? "Yes" : "No"}
                </p>
            </SectionCard>
        </>
    );
}

export default TranscriptConfigDetails;
