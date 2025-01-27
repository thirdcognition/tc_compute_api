import React, { useRef } from "react";
import { HiMinus, HiPlus } from "react-icons/hi";

interface SpeedPopupProps {
    playbackSpeed: number;
    handleSpeedChange: (newSpeed: number) => void;
}

const SpeedPopup: React.FC<SpeedPopupProps> = ({
    playbackSpeed,
    handleSpeedChange
}) => {
    const speedPopupRef = useRef<HTMLDivElement>(null);
    const speeds = [0.75, 1.0, 1.25, 1.5, 2.0];

    return (
        <div
            ref={speedPopupRef}
            className="absolute top-full left-0 mt-2 bg-white dark:bg-gray-800 rounded-lg shadow-xl p-4 w-64 z-50"
        >
            <div className="text-center mb-4">
                <span className="text-2xl font-semibold text-gray-800 dark:text-gray-200">
                    {playbackSpeed.toFixed(2)}x
                </span>
            </div>

            <div className="flex items-center justify-between mb-4">
                <button
                    onClick={() => handleSpeedChange(playbackSpeed - 0.1)}
                    className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                    <HiMinus className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>

                <input
                    type="range"
                    min="0.75"
                    max="2"
                    step="0.1"
                    value={playbackSpeed}
                    onChange={(e) =>
                        handleSpeedChange(parseFloat(e.target.value))
                    }
                    className="flex-1 mx-4 h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                />

                <button
                    onClick={() => handleSpeedChange(playbackSpeed + 0.1)}
                    className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                    <HiPlus className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>
            </div>

            <div className="flex flex-wrap gap-2 justify-center">
                {speeds.map((speed) => (
                    <button
                        key={speed}
                        onClick={() => handleSpeedChange(speed)}
                        className={`px-3 py-1 rounded-full text-sm transition-colors duration-200 ${
                            playbackSpeed === speed
                                ? "bg-blue-600 text-white"
                                : "bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600"
                        }`}
                    >
                        {speed === 1 ? "Normal" : `${speed}x`}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default SpeedPopup;
