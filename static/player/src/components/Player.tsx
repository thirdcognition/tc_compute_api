import React, { useState, useRef, useEffect } from "react";
import {
    BsFillPlayFill as PlayIcon,
    BsPauseFill as PauseIcon
} from "react-icons/bs";
import {
    FiRotateCcw as RewindIcon,
    FiRotateCw as ForwardIcon
} from "react-icons/fi";
import {
    TbVolumeOff as VolumeMuteIcon,
    TbVolume as VolumeUpIcon
} from "react-icons/tb";
import SpeedPopup from "./SpeedPopup.tsx";
import { trackEvent, Session } from "../helpers/analytics.ts";
import session from "../helpers/session.tsx";

interface PlayerProps {
    userId: React.RefObject<string>;
    sessionRef: React.RefObject<Session | null>;
    audioSrc: string;
    transcript: {
        panelId: string;
        panelDisplayTag: string | null;
        transcriptId: string;
        title: string;
        sources: any;
        languageOptions: Record<string, string> | null;
        metadata: {
            images: string[];
        };
    };
}

const Player: React.FC<PlayerProps> = ({
    userId,
    sessionRef,
    audioSrc,
    transcript
}) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const audioRef = useRef<HTMLAudioElement>(null);
    const [playbackSpeed, setPlaybackSpeed] = useState(1);
    const [showSpeedPopup, setShowSpeedPopup] = useState(false);
    const speedPopupRef = useRef<HTMLDivElement>(null);
    const [volume, setVolumeState] = useState(1); // Volume state (default: max volume)
    const [selectedLanguage, setSelectedLanguage] = useState(
        session.getLanguage()
    );

    const setVolume = (newVolume: number) => {
        setVolumeState(newVolume);
        if (audioRef.current) {
            if (/iP(hone|od|ad)/.test(navigator.userAgent)) {
                // iOS workaround: Use muted property
                audioRef.current.muted = newVolume === 0;
            } else {
                audioRef.current.volume = newVolume;
            }
        }
    };
    const [muted, setMuted] = useState(false); // Mute state

    useEffect(() => {
        if (audioRef.current) {
            audioRef.current.volume = muted ? 0 : volume;
        }
    }, [volume, muted]);

    useEffect(() => {
        if ("mediaSession" in navigator && audioRef.current) {
            const artwork = transcript.metadata.images[0]
                ? [
                      {
                          src: transcript.metadata.images[0],
                          sizes: "512x512",
                          type: "image/png"
                      }
                  ]
                : [
                      {
                          src: "/assets/icons/apple-touch-icon.png",
                          sizes: "512x512",
                          type: "image/png"
                      }
                  ];

            navigator.mediaSession.metadata = new MediaMetadata({
                title: transcript.title,
                artwork: artwork
            });

            navigator.mediaSession.setActionHandler("play", () => {
                audioRef.current?.play();
                setIsPlaying(true);
                trackEvent(
                    "player_play",
                    "Player",
                    "Media session play triggered",
                    userId,
                    sessionRef,
                    {
                        currentTime: audioRef.current?.currentTime || 0,
                        duration: audioRef.current?.duration || 0,
                        transctiptTitle: transcript?.title || "unknown",
                        transcriptId: transcript?.transcriptId || "unknown",
                        panelId: transcript.panelId || "unknown",
                        panelTag: transcript.panelDisplayTag || "unknown"
                    }
                );
            });

            navigator.mediaSession.setActionHandler("pause", () => {
                audioRef.current?.pause();
                setIsPlaying(false);
                trackEvent(
                    "player_pause",
                    "Player",
                    "Media session pause triggered",
                    userId,
                    sessionRef,
                    {
                        currentTime: audioRef.current?.currentTime || 0,
                        duration: audioRef.current?.duration || 0,
                        transctiptTitle: transcript?.title || "unknown",
                        transcriptId: transcript?.transcriptId || "unknown",
                        panelId: transcript.panelId || "unknown",
                        panelTag: transcript.panelDisplayTag || "unknown"
                    }
                );
            });

            navigator.mediaSession.setActionHandler("seekbackward", () => {
                skip(-10);
                trackEvent(
                    "player_seekbackward",
                    "Player",
                    "Media session seek backward triggered",
                    userId,
                    sessionRef,
                    {
                        currentTime: audioRef.current?.currentTime || 0,
                        duration: audioRef.current?.duration || 0,
                        transctiptTitle: transcript?.title || "unknown",
                        transcriptId: transcript?.transcriptId || "unknown",
                        panelId: transcript.panelId || "unknown",
                        panelTag: transcript.panelDisplayTag || "unknown",
                        seekOffset: -10
                    }
                );
            });

            navigator.mediaSession.setActionHandler("seekforward", () => {
                skip(10);
                trackEvent(
                    "player_seekforward",
                    "Player",
                    "Media session seek forward triggered",
                    userId,
                    sessionRef,
                    {
                        currentTime: audioRef.current?.currentTime || 0,
                        duration: audioRef.current?.duration || 0,
                        transctiptTitle: transcript?.title || "unknown",
                        transcriptId: transcript?.transcriptId || "unknown",
                        panelId: transcript.panelId || "unknown",
                        panelTag: transcript.panelDisplayTag || "unknown",
                        seekOffset: 10
                    }
                );
            });
        }
    }, [transcript, audioRef]);

    const togglePlay = () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
                trackEvent(
                    "player_pause",
                    "Player",
                    "Pause Audio",
                    userId,
                    sessionRef
                );
                setIsPlaying(false);
            } else {
                const playPromise = audioRef.current.play();
                if (playPromise !== undefined) {
                    playPromise
                        .then(() => {
                            setIsPlaying(true);
                            trackEvent(
                                "player_play",
                                "Player",
                                "Play Audio",
                                userId,
                                sessionRef,
                                {
                                    currentTime:
                                        audioRef.current?.currentTime || 0,
                                    duration: audioRef.current?.duration || 0,
                                    transctiptTitle:
                                        transcript?.title || "unknown",
                                    transcriptId:
                                        transcript?.transcriptId || "unknown",
                                    panelId: transcript.panelId || "unknown",
                                    panelTag:
                                        transcript.panelDisplayTag || "unknown"
                                }
                            );
                        })
                        .catch((error) => {
                            console.error("Error attempting to play:", error);
                            setIsPlaying(false);
                        });
                }
            }
        }
    };

    const skip = (seconds: number) => {
        if (audioRef.current) {
            audioRef.current.currentTime += seconds;
            trackEvent(
                "player_skip",
                "Player",
                `Skip ${seconds > 0 ? "Forward" : "Backward"}: ${Math.abs(seconds)}s`,
                userId,
                sessionRef,
                {
                    currentTime: audioRef.current?.currentTime || 0,
                    duration: audioRef.current?.duration || 0,
                    transctiptTitle: transcript?.title || "unknown",
                    transcriptId: transcript?.transcriptId || "unknown",
                    panelId: transcript.panelId || "unknown",
                    panelTag: transcript.panelDisplayTag || "unknown"
                }
            );
        }
    };

    const handleTimeUpdate = () => {
        if (audioRef.current) {
            setCurrentTime(audioRef.current.currentTime);
        }
    };

    const handleLoadedMetadata = () => {
        if (audioRef.current) {
            setDuration(audioRef.current.duration);
        }
    };

    const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const time = parseFloat(e.target.value);
        if (audioRef.current) {
            audioRef.current.currentTime = time;
            setCurrentTime(time);
        }
    };

    const handleSpeedChange = (newSpeed: number) => {
        setPlaybackSpeed(newSpeed);
        if (audioRef.current) {
            const wasPlaying = !audioRef.current.paused;
            audioRef.current.playbackRate = newSpeed;

            if (wasPlaying) {
                const playPromise = audioRef.current.play();
                if (playPromise !== undefined) {
                    playPromise.catch((error) => {
                        console.log("Playback error:", error);
                    });
                }
            }

            trackEvent(
                "player_speed_change",
                "Player",
                `Speed: ${newSpeed}x`,
                userId,
                sessionRef,
                {
                    currentTime: audioRef.current?.currentTime || 0,
                    duration: audioRef.current?.duration || 0,
                    transctiptTitle: transcript?.title || "unknown",
                    transcriptId: transcript?.transcriptId || "unknown",
                    panelId: transcript.panelId || "unknown",
                    panelTag: transcript.panelDisplayTag || "unknown"
                }
            );
        }
    };

    const formatTime = (time: number) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds.toString().padStart(2, "0")}`;
    };

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (
                speedPopupRef.current &&
                !speedPopupRef.current.contains(event.target as Node)
            ) {
                setShowSpeedPopup(false);
            }
        }

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    const handleLanguageChange = (
        event: React.ChangeEvent<HTMLSelectElement>
    ) => {
        const newLanguage = event.target.value;
        session.setLanguage(newLanguage);
        trackEvent(
            "player_language_switch",
            "Player",
            `Language changed to: ${newLanguage}`,
            userId,
            sessionRef,
            {
                currentTime: audioRef.current?.currentTime || 0,
                duration: audioRef.current?.duration || 0,
                transctiptTitle: transcript?.title || "unknown",
                transcriptId: transcript?.transcriptId || "unknown",
                panelId: transcript.panelId || "unknown",
                panelTag: transcript.panelDisplayTag || "unknown"
            }
        );
        setSelectedLanguage(newLanguage);
        session.refreshApp();
        // window.location.reload(); // Refresh the browser
    };

    const handleAudioEnded = () => {
        console.log("Playback completed!");
        trackEvent(
            "player_complete_audio",
            "Player",
            "Complete Audio playback",
            userId,
            sessionRef,
            {
                currentTime: audioRef.current?.currentTime || 0,
                duration: audioRef.current?.duration || 0,
                transctiptTitle: transcript?.title || "unknown",
                transcriptId: transcript?.transcriptId || "unknown",
                panelId: transcript.panelId || "unknown",
                panelTag: transcript.panelDisplayTag || "unknown"
            }
        );
    };

    return (
        <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-lg shadow-xl mb-4 overflow-hidden">
            <div
                className="relative w-full h-[680px] bg-top bg-cover bg-no-repeat"
                style={{
                    ...(transcript.metadata.images[0] && {
                        backgroundImage: `url(${transcript.metadata.images[0]})`
                    })
                }}
            >
                <div className="absolute bottom-0 w-full p-6 hero-image-gradient">
                    <p className="text-xs font-bold text-gray-800 dark:text-gray-300">
                        LATEST EPISODE:
                    </p>

                    <h2 className="text-2xl font-black text-gray-800 dark:text-gray-300 mb-10">
                        {transcript.title}
                    </h2>

                    <audio
                        ref={audioRef}
                        src={audioSrc}
                        onLoadedMetadata={handleLoadedMetadata}
                        onTimeUpdate={handleTimeUpdate}
                        onEnded={handleAudioEnded}
                    />

                    <div className="space-y-4">
                        {/* Row 2: Playback Speed - Volume Controls */}
                        <div className="flex justify-between items-center gap-3">
                            {transcript.languageOptions &&
                                Object.keys(transcript.languageOptions).length >
                                    1 && (
                                    <div className="relative flox-none pr-2">
                                        <select
                                            value={selectedLanguage}
                                            onChange={handleLanguageChange}
                                            className="px-3 py-1 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600
        text-gray-800 dark:text-gray-300 hover:border-gray-500 dark:hover:border-gray-500
        transition-colors duration-200 font-medium"
                                        >
                                            {Object.entries(
                                                transcript.languageOptions
                                            ).map(([code, name]) => (
                                                <option key={code} value={code}>
                                                    {name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                )}
                            <div className="relative flex-none">
                                <button
                                    onClick={() =>
                                        setShowSpeedPopup(!showSpeedPopup)
                                    }
                                    className="px-3 py-1 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600
                                    text-gray-800 dark:text-gray-300 hover:border-gray-500 dark:hover:border-gray-500
                                    transition-colors duration-200 font-medium"
                                >
                                    {playbackSpeed.toFixed(2)}x
                                </button>
                                {showSpeedPopup && (
                                    <SpeedPopup
                                        playbackSpeed={playbackSpeed}
                                        handleSpeedChange={handleSpeedChange}
                                    />
                                )}
                            </div>
                            <div className="flex flex-1 items-center space-x-4">
                                <button
                                    onClick={() => setMuted(!muted)}
                                    className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                                    title={muted ? "Unmute" : "Mute"}
                                >
                                    {muted ? (
                                        <VolumeMuteIcon className="w-5 h-5 text-red-500" />
                                    ) : (
                                        <VolumeUpIcon className="w-5 h-5 text-[#FD7E61]" />
                                    )}
                                </button>
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.01"
                                    value={muted ? 0 : volume}
                                    onChange={(e) =>
                                        setVolume(parseFloat(e.target.value))
                                    }
                                    disabled={muted}
                                    className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
                                />
                            </div>
                        </div>

                        {/* Row 3: Playback Track Slider */}
                        <div>
                            <input
                                type="range"
                                min="0"
                                max={duration}
                                value={currentTime}
                                onChange={handleSliderChange}
                                className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
                            />
                            <div className="flex justify-between text-sm text-gray-800 dark:text-gray-300">
                                <span>{formatTime(currentTime)}</span>
                                <span>{formatTime(duration)}</span>
                            </div>
                        </div>

                        {/* Row 4: Skip Backwards - Play Button - Skip Forwards */}
                        <div className="flex items-center justify-center space-x-6">
                            <button
                                onClick={() => skip(-15)}
                                className="p-3 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                            >
                                <RewindIcon className="w-6 h-6 text-[#FD7E61]" />
                            </button>

                            <button
                                onClick={togglePlay}
                                className="p-4 rounded-full  bg-[#FD7E61] hover:bg-[#E96A50] text-white"
                            >
                                {isPlaying ? (
                                    <PauseIcon className="w-8 h-8" />
                                ) : (
                                    <PlayIcon className="w-8 h-8" />
                                )}
                            </button>

                            <button
                                onClick={() => skip(15)}
                                className="p-3 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                            >
                                <ForwardIcon className="w-6 h-6 text-[#FD7E61]" />
                            </button>
                        </div>

                        {/* Row 1: Empty - Thumb Up - Thumb Down - Share */}

                        {/* <LikeDislikeSection
                            userId={userId}
                            sessionRef={sessionRef}
                            audioSrc={audioSrc}
                        /> */}
                    </div>
                </div>
            </div>
        </div>
    );
};

export { Player };
