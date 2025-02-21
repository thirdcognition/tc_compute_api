import React, { useRef, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchPanelDetails, fetchPublicPanels } from "../helpers/fetch.ts";
import { urlFormatter } from "../helpers/url.ts";
import CommentsSection from "./CommentsSection.tsx";
import { Player } from "./Player.tsx";
import { Session, trackEvent } from "../helpers/analytics.ts";
import session from "../helpers/session.ts";
import { LANGUAGE_MAP } from "../helpers/options.ts";

interface PanelProps {
    userId: React.RefObject<string>;
    sessionRef: React.RefObject<Session | null>;
    defaultPanelId?: string; // Optional prop for default panelId
}

const Panel: React.FC<PanelProps> = ({
    userId,
    sessionRef,
    defaultPanelId
}) => {
    const { panelId: urlPanelId } = useParams<{ panelId?: string }>();
    const [panelId, setPanelId] = useState<string | undefined>(
        urlPanelId || defaultPanelId
    );

    console.log(panelId, defaultPanelId);

    const navigate = useNavigate();

    // const { panelId } = useParams<{ panelId?: string }>();
    const [transcriptId, setTranscriptId] = useState<string | null>(null);
    const [transcript, setTranscript] = useState<any | null>(null);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [audioOptions, setAudioOptions] = useState<
        {
            url: string;
            date: string;
            transcript_id: string;
            title: string;
            thumbnail?: string;
        }[]
    >([]);
    const [transcriptSources, setTranscriptSources] = useState<
        Array<{
            id: string;
            data: {
                url: string;
                title: string;
                publish_date: string;
                image: string;
            };
        }>
    >([]);
    const [panels, setPanels] = useState<any[]>([]); // State for public panels
    const [selectedPanel, setSelectedPanel] = useState<string | null>(null); // State for selected panel

    useEffect(() => {
        async function fetchPanels() {
            try {
                const fetchedPanels = await fetchPublicPanels();
                setPanels(fetchedPanels);
            } catch (error) {
                console.error("Error fetching public panels:", error);
            }
        }
        fetchPanels();
    }, []);

    useEffect(() => {
        if (!panelId && defaultPanelId) setPanelId(defaultPanelId);

        if (urlPanelId) setPanelId(urlPanelId);
    }, [urlPanelId, defaultPanelId]);

    useEffect(() => {
        if (!panelId) {
            console.error("Panel ID is undefined.");
            return;
        }

        setSelectedPanel(panelId || null);

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

                console.log(transcriptData, audioData);

                setTranscriptSources(
                    Object.entries(transcriptSources || {}).map(
                        ([id, sources]: [string, any]) => ({
                            id,
                            data: {
                                url: sources[0]?.data?.url || "",
                                title: sources[0]?.data?.title || "Untitled",
                                publish_date:
                                    sources[0]?.data?.publish_date || "",
                                image: sources[0]?.data?.image || ""
                            }
                        })
                    ) as Array<{
                        id: string;
                        data: {
                            url: string;
                            title: string;
                            publish_date: string;
                            image: string;
                        };
                    }>
                );

                if (audioData && filesData && filesData.audio_urls) {
                    const formattedAudioUrls = urlFormatter(
                        filesData.audio_urls
                    );
                    const audioEntries = audioData
                        .map((audio) => {
                            const transcript = transcriptData.filter(
                                (t) => t.id === audio.transcript_id
                            )[0];
                            const sources =
                                transcriptSources[audio.transcript_id] || [];
                            const thumbnail =
                                sources.length > 0
                                    ? sources[0].data?.image
                                    : null;
                            return {
                                transcript_id: audio.transcript_id,
                                url: formattedAudioUrls[audio.id],
                                date: new Date(
                                    audio.created_at
                                ).toLocaleDateString(undefined, {
                                    year: "numeric",
                                    month: "long",
                                    day: "numeric",
                                    hour: "numeric",
                                    minute: "numeric"
                                }),
                                title: transcript?.title || "Untitled",
                                thumbnail,
                                created_at: new Date(audio.created_at).getTime()
                            };
                        })
                        .sort((a, b) => b.created_at - a.created_at) // Sort by created_at descending
                        .slice(0, 5); // Limit to 5 most recent episodes
                    setAudioOptions(audioEntries);
                    if (audioEntries.length > 0) {
                        setAudioUrl(audioEntries[0].url); // Default to the latest
                        setTranscriptId(audioEntries[0].transcript_id);

                        setTranscript(
                            transcriptData.find(
                                (transcript) =>
                                    transcript.id ===
                                    audioEntries[0].transcript_id
                            ) || null
                        );
                    } else {
                        setAudioUrl("none");
                    }
                }
            } catch (error) {
                console.error("Error fetching panel data:", error);
            }
        }
        fetchData();
    }, [panelId]);

    const getTranscript = () => {
        const currentAudio = audioOptions.find(
            (option) => option.url === audioUrl
        );
        const currentSource = transcriptSources.find(
            (source) => source.id === transcriptId
        );

        return {
            title: currentAudio?.title || "Untitled",
            metadata: {
                images: currentSource?.data.image
                    ? [currentSource.data.image]
                    : transcript?.metadata?.images || []
            }
        };
    };

    const [selectedLanguage, setSelectedLanguage] = useState(
        session.getLanguage()
    );

    const handleLanguageChange = (
        event: React.ChangeEvent<HTMLSelectElement>
    ) => {
        const newLanguage = event.target.value;
        setSelectedLanguage(newLanguage);
        session.setLanguage(newLanguage);
        trackEvent(
            "language_switch",
            "Panel",
            `Language changed to: ${newLanguage}`,
            userId,
            sessionRef
        );
        window.location.reload(); // Refresh the browser
    };

    const handlePanelChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedId = event.target.value;
        setSelectedPanel(selectedId);
        session.setPanelId(selectedId); // Save the selected panel to localStorage
        trackEvent(
            "show_switch",
            "Panel",
            `Show switched to: ${selectedId}`,
            userId,
            sessionRef
        );
        navigate(`/panel/${selectedId}`);
    };

    return (
        <div>
            <div className="mb-4 w-full">
                <select
                    value={panelId || undefined} // Use panelId directly
                    onChange={handlePanelChange}
                    className="px-3 py-1 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600
        text-gray-800 dark:text-gray-300 hover:border-gray-500 dark:hover:border-gray-500
        transition-colors duration-200 font-medium w-full text-center"
                >
                    <option value="" disabled>
                        Select a show
                    </option>
                    {panels.map((panel) => (
                        <option key={panel.id} value={panel.id}>
                            {panel.metadata.display_tag}
                        </option>
                    ))}
                </select>
            </div>
            {audioUrl && audioUrl != "none" ? (
                <div className="w-full">
                    {/* New container for the icon and text */}
                    {/* <div className="flex justify-center items-center space-x-4 mb-6 w-full">
                        <img
                            src="/assets/mail-header.svg" // Updated to use the URL path
                            alt="Mail Header Icon"
                            className="h-16 mr-2" // Adjust height dynamically based on text size
                            style={{ height: "54px" }} // 4x the height of 17px text
                        />
                        <span className="text-lg font-semibold text-gray-800 dark:text-gray-300">
                            {process.env.REACT_APP_PODCAST_NAME}
                        </span>
                    </div> */}

                    <Player
                        userId={userId}
                        sessionRef={sessionRef}
                        audioSrc={audioUrl}
                        transcript={getTranscript()} // Pass transcript as a prop
                    />
                    {/* <CommentsSection
                        userId={userId}
                        sessionRef={sessionRef}
                        audioUrl={audioUrl}
                    /> */}
                    <div className="mt-4 bg-gray-100 dark:bg-gray-800 rounded-lg shadow-xl p-4">
                        <h3 className="text-lg font-medium text-gray-800 dark:text-gray-400 mb-2">
                            Episodes
                        </h3>
                        <div className="space-y-2">
                            {audioOptions.map((option) => (
                                <div
                                    key={option.url}
                                    className={`flex items-start p-2 rounded-md cursor-pointer ${
                                        audioUrl === option.url
                                            ? "bg-gray-100 border-2 border-[#FD7E61] dark:bg-gray-700 dark:border-[#FD7E61]"
                                            : "bg-white dark:bg-gray-900"
                                    }`}
                                    onClick={() => {
                                        setAudioUrl(option.url);
                                        setTranscriptId(option.transcript_id);
                                        trackEvent(
                                            "episode_switch",
                                            "Panel",
                                            `Episode switched to: ${option.title}`,
                                            userId,
                                            sessionRef
                                        );
                                    }}
                                >
                                    {option.thumbnail && (
                                        <img
                                            src={option.thumbnail}
                                            alt={option.title}
                                            className="w-12 h-12 mr-4 rounded object-cover"
                                        />
                                    )}
                                    <div className="flex-1">
                                        <span
                                            className={`block text-sm font-medium text-gray-800 dark:text-gray-400`}
                                        >
                                            {option.title}
                                        </span>
                                        <span
                                            className={`block text-xs ${
                                                audioUrl === option.url
                                                    ? "text-[#FD7E61]"
                                                    : "text-gray-500 dark:text-gray-400"
                                            } text-right`}
                                        >
                                            {option.date}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            ) : (
                <div className="w-full max-w-2xl bg-gray-100 dark:bg-gray-800 rounded-lg shadow-xl p-6 mb-4">
                    {!panelId ? (
                        <p className="text-gray-600 dark:text-gray-400">
                            Please select your Show first...
                        </p>
                    ) : audioUrl === null ? (
                        <p className="text-gray-600 dark:text-gray-400">
                            Loading audio...
                        </p>
                    ) : (
                        <div className="flex flex-col relative gap-2">
                            <p className="text-gray-600 dark:text-gray-400">
                                No episodes available for the selected language.
                            </p>
                            <select
                                value={selectedLanguage}
                                onChange={handleLanguageChange}
                                className="px-3 py-1 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600
                                    text-gray-800 dark:text-gray-300 hover:border-gray-500 dark:hover:border-gray-500
                                    transition-colors duration-200 font-medium"
                            >
                                {Object.entries(LANGUAGE_MAP).map(
                                    ([code, name]) => (
                                        <option key={code} value={code}>
                                            {name}
                                        </option>
                                    )
                                )}
                            </select>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Panel;
