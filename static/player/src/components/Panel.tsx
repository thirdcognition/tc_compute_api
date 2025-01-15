import React, { useRef, useEffect, useState, ChangeEvent } from "react";
import { useParams } from "react-router-dom";
import { fetchPanelDetails } from "../helpers/fetch.ts";
import { urlFormatter } from "../helpers/url.ts";
import CommentsSection from "./CommentsSection.tsx";
import { Player } from "./Player.tsx";
import { Session } from "../helpers/gaTracking.ts";

interface PanelProps {
    userId: React.RefObject<string>;
    sessionRef: React.RefObject<Session | null>;
}

const Panel: React.FC<PanelProps> = ({ userId, sessionRef }) => {
    const { panelId } = useParams<{ panelId?: string }>();
    const [transcriptId, setTranscriptId] = useState<string | null>(null);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [audioOptions, setAudioOptions] = useState<
        { url: string; date: string; transcript_id: string }[]
    >([]);
    const [transcriptSources, setTranscriptSources] = useState([]);

    useEffect(() => {
        if (!panelId) {
            console.error("Panel ID is undefined.");
            return;
        }

        async function fetchData() {
            if (typeof panelId !== "string") {
                console.error("Panel ID is undefined.");
                return;
            }

            try {
                const {
                    discussionData,
                    transcriptData,
                    transcriptSources,
                    audioData,
                    filesData
                } = await fetchPanelDetails(panelId);
                setTranscriptSources(transcriptSources); // Set transcript sources
                if (audioData && filesData && filesData.audio_urls) {
                    const formattedAudioUrls = urlFormatter(
                        filesData.audio_urls
                    );
                    const audioEntries = audioData.map((audio) => ({
                        transcript_id: audio.transcript_id,
                        url: formattedAudioUrls[audio.id],
                        date: new Date(audio.created_at).toLocaleDateString()
                    }));
                    setAudioOptions(audioEntries);
                    if (audioEntries.length > 0) {
                        setAudioUrl(audioEntries[audioEntries.length - 1].url); // Default to the latest
                        setTranscriptId(
                            audioEntries[audioEntries.length - 1].transcript_id
                        );
                    }
                }
            } catch (error) {
                console.error("Error fetching panel data:", error);
            }
        }
        fetchData();
    }, [panelId]);

    return (
        <div>
            {audioUrl ? (
                <div className="w-full">
                    <Player
                        userId={userId}
                        sessionRef={sessionRef}
                        audioSrc={audioUrl}
                        audioDate={
                            audioOptions.find(
                                (option) => option.url === audioUrl
                            )?.date || ""
                        }
                        transcriptSources={
                            transcriptId && transcriptSources[transcriptId]
                        } // Pass sources as a prop
                    />
                    {/* <CommentsSection
                        userId={userId}
                        sessionRef={sessionRef}
                        audioUrl={audioUrl}
                    /> */}
                    <div className="mt-4 bg-blue-50 dark:bg-gray-800 rounded-lg shadow-xl p-4">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                            Episodes
                        </h3>
                        <div className="space-y-2">
                            {audioOptions
                                .slice()
                                .reverse()
                                .map((option) => (
                                    <div
                                        key={option.url}
                                        className={`p-2 rounded-md cursor-pointer ${
                                            audioUrl === option.url
                                                ? "bg-blue-100 dark:bg-gray-700"
                                                : "bg-white dark:bg-gray-800"
                                        }`}
                                        onClick={() => {
                                            setAudioUrl(option.url);
                                            setTranscriptId(
                                                option.transcript_id
                                            );
                                        }}
                                    >
                                        <span
                                            className={`text-sm font-medium text-center block ${
                                                audioUrl === option.url
                                                    ? "text-blue-600 dark:text-blue-400"
                                                    : "text-gray-700 dark:text-gray-300"
                                            }`}
                                        >
                                            {option.date}
                                        </span>
                                    </div>
                                ))}
                        </div>
                    </div>
                </div>
            ) : (
                <div className="w-full max-w-2xl bg-blue-50 dark:bg-gray-800 rounded-lg shadow-xl p-6 mb-4">
                    <p className="text-gray-600 dark:text-gray-400">
                        {audioUrl === null
                            ? "Loading audio..."
                            : "No audio file available."}
                    </p>
                </div>
            )}
        </div>
    );
};

export default Panel;
