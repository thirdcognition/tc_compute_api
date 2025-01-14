import React, { useState, useRef, useEffect } from "react";
import {
    BsFillPlayFill,
    BsPauseFill,
    BsMoonFill,
    BsSunFill
} from "react-icons/bs";
import { FiRotateCcw, FiRotateCw } from "react-icons/fi";
import { TbClearAll } from "react-icons/tb";
import SpeedPopup from "./SpeedPopup.tsx";
import LikeDislikeSection from "./LikeDislikeSection.tsx";
import { trackEvent, Session } from "../helpers/gaTracking.ts";

interface PlayerProps {
    userId: React.RefObject<string>;
    sessionRef: React.RefObject<Session | null>;
    audioSrc: string;
    audioDate: string; // New prop for audio date
}

const Player: React.FC<PlayerProps> = ({
    userId,
    sessionRef,
    audioSrc,
    audioDate
}) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [isDark, setIsDark] = useState(false);
    const audioRef = useRef<HTMLAudioElement>(null);
    const [playbackSpeed, setPlaybackSpeed] = useState(1);
    const [showSpeedPopup, setShowSpeedPopup] = useState(false);
    const speedPopupRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (isDark) {
            document.documentElement.classList.add("dark");
        } else {
            document.documentElement.classList.remove("dark");
        }
    }, [isDark]);

    const togglePlay = () => {
        if (audioRef.current) {
            if (isPlaying) {
                audioRef.current.pause();
                trackEvent(
                    "pause",
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
                                "play",
                                "Player",
                                "Play Audio",
                                userId,
                                sessionRef
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
                "skip",
                "Player",
                `Skip ${seconds > 0 ? "Forward" : "Backward"}: ${Math.abs(seconds)}s`,
                userId,
                sessionRef
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

    const clearUserData = () => {
        localStorage.removeItem(`totalLikes_${audioSrc}`);
        localStorage.removeItem(`totalDislikes_${audioSrc}`);
        localStorage.removeItem(`vote_${userId.current}_${audioSrc}`);
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
                "speed_change",
                "Player",
                `Speed: ${newSpeed}x`,
                userId,
                sessionRef
            );
        }
    };

    const toggleTheme = () => {
        const newTheme = !isDark;
        setIsDark(newTheme);
        trackEvent(
            "theme_toggle",
            "UI",
            `Theme: ${newTheme ? "Dark" : "Light"}`,
            userId,
            sessionRef
        );
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

    return (
        <div className="w-full max-w-2xl bg-blue-50 dark:bg-gray-800 rounded-lg shadow-xl p-6 mb-4">
            {/* Episode title */}
            <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4 text-center">
                Episode: {audioDate}
            </h2>
            <div className="flex justify-between mb-4">
                <div className="relative">
                    <button
                        onClick={() => setShowSpeedPopup(!showSpeedPopup)}
                        className="px-3 py-1 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600
                      text-gray-700 dark:text-gray-300 hover:border-blue-500 dark:hover:border-blue-400
                      transition-colors duration-200 font-medium"
                    >
                        {playbackSpeed}x
                    </button>
                    {showSpeedPopup && (
                        <SpeedPopup
                            playbackSpeed={playbackSpeed}
                            handleSpeedChange={handleSpeedChange}
                        />
                    )}
                </div>
                <div className="flex space-x-2">
                    <button
                        onClick={clearUserData}
                        className="p-2 rounded-full hover:bg-blue-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors duration-200"
                        title="Clear all interactions"
                    >
                        <TbClearAll className="w-5 h-5" />
                    </button>
                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-full hover:bg-blue-100 dark:hover:bg-gray-700"
                    >
                        {isDark ? (
                            <BsSunFill className="w-5 h-5 text-yellow-400" />
                        ) : (
                            <BsMoonFill className="w-5 h-5 text-gray-600" />
                        )}
                    </button>
                </div>
            </div>

            <audio
                ref={audioRef}
                src={audioSrc}
                onLoadedMetadata={handleLoadedMetadata}
                onTimeUpdate={handleTimeUpdate}
            />

            {/* Player Controls */}
            <div className="space-y-4">
                <div className="flex items-center justify-center space-x-6">
                    <button
                        onClick={() => skip(-15)}
                        className="p-3 rounded-full hover:bg-blue-100 dark:hover:bg-gray-700"
                    >
                        <FiRotateCcw className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </button>

                    <button
                        onClick={togglePlay}
                        className="p-4 rounded-full bg-blue-600 hover:bg-blue-700 text-white"
                    >
                        {isPlaying ? (
                            <BsPauseFill className="w-8 h-8" />
                        ) : (
                            <BsFillPlayFill className="w-8 h-8" />
                        )}
                    </button>

                    <button
                        onClick={() => skip(15)}
                        className="p-3 rounded-full hover:bg-blue-100 dark:hover:bg-gray-700"
                    >
                        <FiRotateCw className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </button>
                </div>

                <div className="space-y-2">
                    <input
                        type="range"
                        min="0"
                        max={duration}
                        value={currentTime}
                        onChange={handleSliderChange}
                        className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                    />
                    <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                        <span>{formatTime(currentTime)}</span>
                        <span>{formatTime(duration)}</span>
                    </div>
                </div>

                {/* Like/Dislike Section */}
                <LikeDislikeSection
                    userId={userId}
                    sessionRef={sessionRef}
                    audioSrc={audioSrc}
                />
            </div>
        </div>
    );
};

export { Player };
