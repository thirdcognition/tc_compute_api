import React, { useState, useEffect } from "react";
import { IoSendSharp } from "react-icons/io5";
import { FaChevronDown, FaChevronUp } from "react-icons/fa";
import { trackEvent, Session } from "../helpers/gaTracking.ts";

interface Comment {
    id: string;
    text: string;
    timestamp: number;
}

interface CommentsSectionProps {
    audioUrl: string;
    userId: React.RefObject<string>;
    sessionRef: React.RefObject<Session | null>;
}

const CommentsSection: React.FC<CommentsSectionProps> = ({
    userId,
    audioUrl,
    sessionRef
}) => {
    const [comments, setComments] = useState<Comment[]>([]);
    const [newComment, setNewComment] = useState("");
    const [showAllComments, setShowAllComments] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        const savedComments = localStorage.getItem(`comments_${audioUrl}`);
        if (savedComments) {
            setComments(JSON.parse(savedComments));
        } else {
            setComments([]);
        }
    }, [audioUrl]);

    const handleCommentSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (newComment.trim() && !isSubmitting) {
            setIsSubmitting(true);

            const comment: Comment = {
                id: Math.random().toString(36).substring(2, 9),
                text: newComment.trim(),
                timestamp: Date.now()
            };

            const updatedComments = [...comments, comment];
            setComments(updatedComments);
            localStorage.setItem(
                `comments_${audioUrl}`,
                JSON.stringify(updatedComments)
            );
            setNewComment("");
            setIsSubmitting(false);

            trackEvent(
                "comment_submit",
                "Engagement",
                `Comment: ${newComment.trim()}`,
                userId,
                sessionRef
            );
        }
    };
    const visibleComments = showAllComments ? comments : comments.slice(0, 3);
    const hasMoreComments = comments.length > 3;

    const formatTimestamp = (timestamp: number) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInSeconds = Math.floor(
            (now.getTime() - date.getTime()) / 1000
        );

        if (diffInSeconds < 60) return "just now";
        if (diffInSeconds < 3600)
            return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400)
            return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    };

    return (
        <div className="w-full max-w-2xl bg-gray-100 dark:bg-gray-800 rounded-lg shadow-xl p-6 overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-400">
                Feedback
            </h3>
            <small className="text-gray-800 dark:text-gray-400 mt-2 mb-4 block">
                Feedback is only visible for you.
            </small>

            {/* Comment Input */}
            <form onSubmit={handleCommentSubmit} className="mb-6">
                <div className="flex items-center space-x-2">
                    <input
                        type="text"
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        placeholder="Send feedback..."
                        className="flex-1 px-4 py-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-800 dark:text-gray-400 focus:outline-none focus:border-[#FD7E61] dark:focus:border-[#FD7E61]"
                        maxLength={500}
                    />
                    <button
                        type="submit"
                        disabled={!newComment.trim() || isSubmitting}
                        className="p-2 rounded-full transition-colors duration-200 disabled:text-gray-400 dark:disabled:text-gray-600 text-[#FD7E61] hover:text-[#E96A50] dark:hover:text-[#E96A50] disabled:hover:text-gray-400 dark:disabled:hover:text-gray-600"
                    >
                        <IoSendSharp className="w-5 h-5" />
                    </button>
                </div>
            </form>

            {/* Comments List */}
            <div className="space-y-4">
                {visibleComments.map((comment) => (
                    <div
                        key={comment.id}
                        className="bg-white dark:bg-gray-700 rounded-lg p-4 shadow-sm"
                    >
                        <p className="text-gray-800 dark:text-gray-400 mb-2">
                            {comment.text}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            {formatTimestamp(comment.timestamp)}
                        </p>
                    </div>
                ))}
            </div>

            {/* Show More/Less Button */}
            {hasMoreComments && (
                <button
                    onClick={() => setShowAllComments(!showAllComments)}
                    className="mt-4 flex items-center space-x-2 text-[#FD7E61] hover:text-[#E96A50] dark:text-[#FD7E61] dark:hover:text-[#E96A50] transition-colors duration-200"
                >
                    <span>{showAllComments ? "Show Less" : "Show More"}</span>
                    {showAllComments ? (
                        <FaChevronUp className="w-4 h-4" />
                    ) : (
                        <FaChevronDown className="w-4 h-4" />
                    )}
                </button>
            )}
        </div>
    );
};

export default CommentsSection;
