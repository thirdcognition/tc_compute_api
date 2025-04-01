import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchPanelDetails, fetchPanels } from "../helpers/fetch.ts";
import { urlFormatter } from "../helpers/url.ts";
import { FaImage } from "react-icons/fa";
import { Player } from "./Player.tsx";
import { Session, trackEvent } from "../helpers/analytics.ts";
import session from "../helpers/session.tsx";
// import { capitalizeFirstLetter } from "../helpers/lib.ts";
import { outputLanguageOptions } from "../helpers/options";
const Accordion: React.FC<{
    title: string;
    setOpen?: boolean; // Optional prop
    children: React.ReactNode;
    buttonClassName?: string; // Optional prop for button styling
}> = ({ title, setOpen = false, children, buttonClassName }) => {
    // Default to false
    const [isOpen, setIsOpen] = useState(setOpen);

    return (
        <div>
            <button
                className={`w-full text-left ${buttonClassName || "py-2 px-4 font-medium text-gray-800 dark:text-gray-400"}`}
                onClick={() => setIsOpen(!isOpen)}
            >
                {isOpen ? "▼" : "►"} {title}
            </button>
            {isOpen && <div className="px-4 py-2">{children}</div>}
        </div>
    );
};

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

    const [languageOptions, setLanguageOptions] = useState<Record<
        string,
        string
    > | null>(null);

    const navigate = useNavigate();

    // const { panelId } = useParams<{ panelId?: string }>();
    const [transcriptId, setTranscriptId] = useState<string | null>(null);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [audioOptions, setAudioOptions] = useState<
        {
            url: string;
            date: string;
            transcript_id: string;
            transcript: any;
            title: string;
            thumbnail?: string;
        }[]
    >([]);
    const [sourceData, setSourceData] = useState<
        Array<{
            id: string;
            data: Array<{
                url: string;
                title: string;
                publish_date: string;
                image: string;
            }>;
        }>
    >([]);
    const [panels, setPanels] = useState<any[]>([]); // State for public panels
    const [selectedPanel, setSelectedPanel] = useState<string | null>(null); // State for selected panel
    const [panelData, setPanelData] = useState<any>(null);

    useEffect(() => {
        async function fetchPanelData() {
            try {
                const fetchedPanels = await fetchPanels();
                setPanels(fetchedPanels);
            } catch (error) {
                console.error("Error fetching public panels:", error);
            }
        }
        fetchPanelData();
    }, []);

    useEffect(() => {
        if (!panelId && defaultPanelId) setPanelId(defaultPanelId);

        if (urlPanelId) setPanelId(urlPanelId);
    }, [urlPanelId, defaultPanelId]);

    async function configureTranscriptData() {
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

            // console.log(transcriptData, audioData, transcriptSources);

            setPanelData(discussionData);
            if (discussionData?.metadata?.languages) {
                const langs = { en: "English" };
                for (
                    let index = 0;
                    index < discussionData.metadata?.languages.length;
                    index++
                ) {
                    const element = discussionData.metadata?.languages[index];
                    langs[element] = outputLanguageOptions[element]; //capitalizeFirstLetter(element);
                }

                setLanguageOptions(langs);
            }

            setSourceData(
                Object.entries(transcriptSources || {}).map(
                    ([id, sources]: [string, any]) => {
                        const transcript = transcriptData.filter(
                            (t) => t.id === id
                        )[0];
                        return {
                            id,
                            data: sources.map((s, i) => ({
                                id: s?.id,
                                url: s?.data?.url || "",
                                title: s?.data?.title || "",
                                publish_date: s?.data?.publish_date || "",
                                image:
                                    s?.data?.image ||
                                    transcript?.metadta?.images[i] ||
                                    ""
                            }))
                        };
                    }
                ) as unknown as Array<{
                    id: string;
                    data: Array<{
                        url: string;
                        title: string;
                        publish_date: string;
                        image: string;
                    }>;
                }>
            );

            if (audioData && filesData && filesData.audio_urls) {
                const formattedAudioUrls = urlFormatter(filesData.audio_urls);
                const audioEntries = audioData
                    .map((audio) => {
                        const transcript = transcriptData.filter(
                            (t) => t.id === audio.transcript_id
                        )[0];
                        const sources =
                            transcriptSources[audio.transcript_id] || [];
                        const thumbnail =
                            (sources.length > 0
                                ? sources.filter((s) => !!s.image).data?.image
                                : null) ||
                            transcript?.metadata?.images?.at(0) ||
                            "null";
                        return {
                            transcript_id: audio.transcript_id,
                            transcript: transcript || null,
                            url: formattedAudioUrls[audio.id],
                            date: new Date(audio.created_at).toLocaleDateString(
                                undefined,
                                {
                                    year: "numeric",
                                    month: "long",
                                    day: "numeric",
                                    hour: "numeric",
                                    minute: "numeric"
                                }
                            ),
                            title: transcript?.title || "Untitled",
                            thumbnail,
                            created_at: new Date(audio.created_at).getTime()
                        };
                    })
                    .filter((i) => i.transcript !== null)
                    .sort((a, b) => b.created_at - a.created_at) // Sort by created_at descending
                    .slice(0, 5); // Limit to 5 most recent episodes

                // console.log(audioEntries);
                setAudioOptions(audioEntries);
                if (audioEntries.length > 0) {
                    setAudioUrl(audioEntries[0].url); // Default to the latest
                    setTranscriptId(audioEntries[0].transcript_id);
                } else {
                    setAudioUrl("none");
                }
            }
        } catch (error) {
            console.error("Error fetching panel data:", error);
        }
    }

    useEffect(() => {
        if (!panelId) {
            console.error("Panel ID is undefined.");
            return;
        }

        setSelectedPanel(panelId || null);

        configureTranscriptData();
    }, [panelId]);

    const getTranscript = () => {
        const currentAudio = audioOptions.find(
            (option) => option.url === audioUrl
        );
        const currentTranscript = currentAudio?.transcript;
        let currentSources;

        if (
            Array.isArray(currentTranscript?.metadata?.subjects) &&
            typeof currentTranscript.metadata.subjects[0] === "object"
        ) {
            currentSources = [
                {
                    data: currentTranscript.metadata?.subjects
                }
            ];
        } else {
            currentSources = sourceData.filter(
                (source) => source.id === transcriptId
            );
        }

        return {
            title: currentTranscript?.title || "Untitled",
            panelId: currentTranscript?.panel_id,
            panelDisplayTag: panelData?.metadata?.display_tag,
            transcriptId: currentTranscript?.id,
            sources: currentSources,
            languageOptions: languageOptions,
            metadata: {
                images:
                    (currentTranscript?.metadata?.images?.length || 0) > 0
                        ? currentTranscript?.metadata?.images || []
                        : currentSources
                              ?.at(0)
                              ?.data?.filter((i) => !!i.image)
                              ?.map((i) => i.image)
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
        session.setLanguage(newLanguage);
        trackEvent(
            "language_switch",
            "Panel",
            `Language changed to: ${newLanguage}`,
            userId,
            sessionRef,
            {
                language: newLanguage,
                panelId: selectedPanel
            }
        );
        setSelectedLanguage(newLanguage);
        session.refreshApp();
    };

    const handlePanelChange = (event: any) => {
        const selectedId = event.target.value;
        trackEvent(
            "show_switch",
            "Panel",
            `Show switched to: ${selectedId}`,
            userId,
            sessionRef,
            {
                panelId: selectedPanel,
                changePanel: selectedId
            }
        );
        setSelectedPanel(selectedId);
        session.setPanelId(selectedId); // Save the selected panel to localStorage
        navigate(`/panel/${selectedId}`);
    };

    const sourceItem = (option) => (
        <div
            key={option.url}
            className=" w-full flex items-start p-2 rounded-md cursor-pointer bg-white dark:bg-gray-900 mb-2"
        >
            {option.image ? (
                <img
                    src={option.image}
                    alt={option.title}
                    className="w-12 h-12 mr-4 rounded object-cover flex-none"
                />
            ) : (
                <div className="w-12 h-12 mr-4 rounded flex-none flex items-center justify-center bg-gray-200 dark:bg-gray-700">
                    <FaImage className="text-gray-500 dark:text-gray-400 w-6 h-6" />
                </div>
            )}

            <div className="flex-1 self-center overflow-hidden">
                <div className="flex flex-col">
                    {(Array.isArray(option.url)
                        ? option.url
                        : [option.url]
                    )?.filter((url) => !!url).length > 1 ? (
                        <Accordion
                            title={option.title}
                            buttonClassName="text-sm text-gray-800 dark:text-gray-400 mb-2"
                        >
                            {(Array.isArray(option.url)
                                ? option.url
                                : [option.url]
                            )
                                ?.filter((url) => !!url)
                                ?.map((url, index) => (
                                    <a
                                        key={index}
                                        href={url.trim()}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs block text-gray-500 hover:underline overflow-hidden text-ellipsis whitespace-nowrap"
                                    >
                                        {index + 1}: {url.trim()}
                                    </a>
                                ))}
                        </Accordion>
                    ) : (
                        <>
                            <span className="text-sm text-gray-800 dark:text-gray-400">
                                {option.title}
                            </span>
                            {option.url ? (
                                <a
                                    key={option.url}
                                    href={option.url.trim()}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs block text-gray-500 hover:underline overflow-hidden text-ellipsis whitespace-nowrap"
                                >
                                    1: {option.url.trim()}
                                </a>
                            ) : (
                                ""
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );

    const renderSources = (sources) => {
        console.log(sources);
        return (
            sources
                ?.at(0)
                ?.data?.filter((i) => !!i.title)
                ?.map((option) => {
                    if (option.references) {
                        return (
                            <Accordion
                                title={option.title}
                                buttonClassName="text-sm text-gray-800 dark:text-gray-400 mb-2 ml-4"
                            >
                                <span className="text-sm block text-gray-800 dark:text-gray-400 p-2 mb-4">
                                    {option.description}
                                </span>
                                {option.references.map(sourceItem)}
                            </Accordion>
                        );
                    } else {
                        return sourceItem(option);
                    }
                }) || <div>No sources found.</div>
        );
    };

    const renderEpisodes = (audioOptions) => {
        return audioOptions.map((option) => (
            <div
                key={option.url}
                className={`w-full flex items-start p-2 rounded-md cursor-pointer ${
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
                        sessionRef,
                        {
                            transctiptTitle: option.title || "unknown",
                            transcriptId: option.transcript_id || "unknown",
                            panelId: panelId || "unknown"
                        }
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
                <div className="flex-1 w-full overflow-hidden">
                    <span
                        className={`block text-sm font-medium overflow-hidden text-ellipsis whitespace-nowrap text-gray-800 dark:text-gray-400`}
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
        ));
    };

    const transcriptData = getTranscript();

    return (
        <div className="max-w-2xl w-full">
            <div className="flex flex-wrap gap-2 mb-4 justify-center">
                {panels.map((panel) => (
                    <button
                        key={panel.id}
                        onClick={() =>
                            handlePanelChange({ target: { value: panel.id } })
                        }
                        disabled={panelId === panel.id}
                        className={`px-4 py-2 rounded-full font-medium border transition-colors duration-200
                ${
                    panelId === panel.id
                        ? "bg-[#FD7E61] text-white border-[#FD7E61]"
                        : "bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-300 border-gray-300 dark:border-gray-600 "
                }
                `}
                    >
                        {panel.metadata.display_tag}
                    </button>
                ))}
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
                        transcript={transcriptData} // Pass transcript as a prop
                    />
                    {/* <CommentsSection
                        userId={userId}
                        sessionRef={sessionRef}
                        audioUrl={audioUrl}
                    /> */}
                    <div className="mt-4 bg-gray-100 dark:bg-gray-800 rounded-lg shadow-xl p-4">
                        {(
                            transcriptData?.sources
                                ?.at(0)
                                ?.data?.filter((i) => !!i.title) || []
                        ).length > 0 ? (
                            <Accordion title="Episode Subjects">
                                {renderSources(transcriptData.sources)}
                            </Accordion>
                        ) : (
                            ""
                        )}
                        <Accordion title="Other Episodes">
                            {renderEpisodes(audioOptions)}
                        </Accordion>
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
                            {languageOptions &&
                                Object.keys(languageOptions).length > 1 && (
                                    <>
                                        <p className="text-gray-600 dark:text-gray-400">
                                            No episodes available for the
                                            selected language.
                                        </p>
                                        <select
                                            value={selectedLanguage}
                                            onChange={handleLanguageChange}
                                            className="px-3 py-1 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600
                                    text-gray-800 dark:text-gray-300 hover:border-gray-500 dark:hover:border-gray-500
                                    transition-colors duration-200 font-medium"
                                        >
                                            {Object.entries(
                                                languageOptions
                                            ).map(([code, name]) => (
                                                <option key={code} value={code}>
                                                    {name}
                                                </option>
                                            ))}
                                        </select>
                                    </>
                                )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Panel;
