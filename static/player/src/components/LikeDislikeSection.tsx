import React, { useState, useEffect } from "react";
import {
    AiOutlineLike,
    AiOutlineDislike,
    AiFillLike,
    AiFillDislike
} from "react-icons/ai";
import { trackEvent, Session } from "../helpers/gaTracking.ts";

interface LikeDislikeSectionProps {
    audioSrc: string;
    userId: React.RefObject<string>;
    sessionRef: React.RefObject<Session | null>;
}

const LikeDislikeSection: React.FC<LikeDislikeSectionProps> = ({
    userId,
    audioSrc,
    sessionRef
}) => {
    const [likeCount, setLikeCount] = useState(0);
    const [dislikeCount, setDislikeCount] = useState(0);
    const [isLiked, setIsLiked] = useState(false);
    const [isDisliked, setIsDisliked] = useState(false);

    const loadVotes = () => {
        const totalLikes = parseInt(
            localStorage.getItem(`totalLikes_${audioSrc}`) || "0"
        );
        const totalDislikes = parseInt(
            localStorage.getItem(`totalDislikes_${audioSrc}`) || "0"
        );
        setLikeCount(totalLikes);
        setDislikeCount(totalDislikes);

        const userVote = localStorage.getItem(
            `vote_${userId.current}_${audioSrc}`
        );
        if (userVote === "like") {
            setIsLiked(true);
        } else if (userVote === "dislike") {
            setIsDisliked(true);
        }
    };

    useEffect(() => {
        setIsLiked(false);
        setIsDisliked(false);
        loadVotes();
    }, [audioSrc]);

    const handleLike = () => {
        const userVote = localStorage.getItem(`vote_${userId.current}`);

        if (isLiked) {
            setLikeCount((prev) => prev - 1);
            setIsLiked(false);
            localStorage.setItem(
                `totalLikes_${audioSrc}`,
                String(likeCount - 1)
            );
            localStorage.removeItem(`vote_${userId.current}_${audioSrc}`);
            trackEvent(
                "unlike",
                "Engagement",
                "Remove Like",
                userId,
                sessionRef
            );
        } else {
            if (isDisliked) {
                setDislikeCount((prev) => prev - 1);
                setIsDisliked(false);
                localStorage.setItem(
                    `totalDislikes_${audioSrc}`,
                    String(dislikeCount - 1)
                );
                trackEvent(
                    "remove_dislike",
                    "Engagement",
                    "Remove Dislike",
                    userId,
                    sessionRef
                );
            }
            setLikeCount((prev) => prev + 1);
            setIsLiked(true);
            localStorage.setItem(
                `totalLikes_${audioSrc}`,
                String(likeCount + 1)
            );
            localStorage.setItem(`vote_${userId.current}_${audioSrc}`, "like");
            trackEvent("like", "Engagement", "Add Like", userId, sessionRef);
        }
    };

    const handleDislike = () => {
        const userVote = localStorage.getItem(`vote_${userId.current}`);

        if (isDisliked) {
            setDislikeCount((prev) => prev - 1);
            setIsDisliked(false);
            localStorage.setItem(
                `totalDislikes_${audioSrc}`,
                String(dislikeCount - 1)
            );
            localStorage.removeItem(`vote_${userId.current}_${audioSrc}`);
            trackEvent(
                "undislike",
                "Engagement",
                "Remove Dislike",
                userId,
                sessionRef
            );
        } else {
            if (isLiked) {
                setLikeCount((prev) => prev - 1);
                setIsLiked(false);
                localStorage.setItem("totalLikes", String(likeCount - 1));
                trackEvent(
                    "remove_like",
                    "Engagement",
                    "Remove Like",
                    userId,
                    sessionRef
                );
            }
            setDislikeCount((prev) => prev + 1);
            setIsDisliked(true);
            localStorage.setItem(
                `totalDislikes_${audioSrc}`,
                String(dislikeCount + 1)
            );
            localStorage.setItem(
                `vote_${userId.current}_${audioSrc}`,
                "dislike"
            );
            trackEvent(
                "dislike",
                "Engagement",
                "Add Dislike",
                userId,
                sessionRef
            );
        }
    };

    return (
        <div className="border-t dark:border-gray-700 pt-4 mt-4">
            <div className="flex justify-center space-x-8">
                <button
                    onClick={handleLike}
                    className="flex items-center p-2 rounded-lg hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-200"
                >
                    {isLiked ? (
                        <AiFillLike className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    ) : (
                        <AiOutlineLike className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                    )}
                </button>
                <button
                    onClick={handleDislike}
                    className="flex items-center p-2 rounded-lg hover:bg-red-100 dark:hover:bg-gray-700 transition-colors duration-200"
                >
                    {isDisliked ? (
                        <AiFillDislike className="w-6 h-6 text-red-600 dark:text-red-400" />
                    ) : (
                        <AiOutlineDislike className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                    )}
                </button>
            </div>
        </div>
    );
};

export default LikeDislikeSection;
