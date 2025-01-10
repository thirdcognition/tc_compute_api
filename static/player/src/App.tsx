import React, { useState, useRef, useEffect } from 'react';
import { BsFillPlayFill, BsPauseFill, BsMoonFill, BsSunFill } from 'react-icons/bs';
import { BiSkipNext, BiSkipPrevious } from 'react-icons/bi';
import { FiRotateCcw, FiRotateCw } from 'react-icons/fi';
import { AiOutlineLike, AiOutlineDislike, AiFillLike, AiFillDislike } from 'react-icons/ai';
import { FaChevronDown, FaChevronUp } from 'react-icons/fa';
import { IoSendSharp } from 'react-icons/io5';
import { TbClearAll } from 'react-icons/tb';
import { HiMinus, HiPlus } from 'react-icons/hi';

// Configuration
const SHOW_CLEAR_BUTTON = true; // Set this to false to hide the clear button

// Generate a unique user ID if it doesn't exist
const getUserId = () => {
  let userId = localStorage.getItem('userId');
  if (!userId) {
    userId = Math.random().toString(36).substr(2, 9);
    localStorage.setItem('userId', userId);
  }
  return userId;
};

interface Comment {
  id: string;
  text: string;
  timestamp: number;
}

function App() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isDark, setIsDark] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [dislikeCount, setDislikeCount] = useState(0);
  const [isLiked, setIsLiked] = useState(false);
  const [isDisliked, setIsDisliked] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const userId = useRef(getUserId());
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [showAllComments, setShowAllComments] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [showSpeedPopup, setShowSpeedPopup] = useState(false);
  const speedPopupRef = useRef<HTMLDivElement>(null);

  // Load initial votes and comments from localStorage
  useEffect(() => {
    const loadVotes = () => {
      // Load total counts
      const totalLikes = parseInt(localStorage.getItem('totalLikes') || '0');
      const totalDislikes = parseInt(localStorage.getItem('totalDislikes') || '0');
      setLikeCount(totalLikes);
      setDislikeCount(totalDislikes);

      // Load user's vote
      const userVote = localStorage.getItem(`vote_${userId.current}`);
      if (userVote === 'like') {
        setIsLiked(true);
      } else if (userVote === 'dislike') {
        setIsDisliked(true);
      }
    };

    const loadComments = () => {
      const savedComments = localStorage.getItem('comments');
      if (savedComments) {
        setComments(JSON.parse(savedComments));
      }
    };

    loadVotes();
    loadComments();
  }, []);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const handleLike = () => {
    const userVote = localStorage.getItem(`vote_${userId.current}`);
    
    if (isLiked) {
      // Remove like
      setLikeCount(prev => prev - 1);
      setIsLiked(false);
      localStorage.setItem('totalLikes', String(likeCount - 1));
      localStorage.removeItem(`vote_${userId.current}`);
    } else {
      // Add like
      if (isDisliked) {
        // Remove previous dislike
        setDislikeCount(prev => prev - 1);
        setIsDisliked(false);
        localStorage.setItem('totalDislikes', String(dislikeCount - 1));
      }
      setLikeCount(prev => prev + 1);
      setIsLiked(true);
      localStorage.setItem('totalLikes', String(likeCount + 1));
      localStorage.setItem(`vote_${userId.current}`, 'like');
    }
  };

  const handleDislike = () => {
    const userVote = localStorage.getItem(`vote_${userId.current}`);
    
    if (isDisliked) {
      // Remove dislike
      setDislikeCount(prev => prev - 1);
      setIsDisliked(false);
      localStorage.setItem('totalDislikes', String(dislikeCount - 1));
      localStorage.removeItem(`vote_${userId.current}`);
    } else {
      // Add dislike
      if (isLiked) {
        // Remove previous like
        setLikeCount(prev => prev - 1);
        setIsLiked(false);
        localStorage.setItem('totalLikes', String(likeCount - 1));
      }
      setDislikeCount(prev => prev + 1);
      setIsDisliked(true);
      localStorage.setItem('totalDislikes', String(dislikeCount + 1));
      localStorage.setItem(`vote_${userId.current}`, 'dislike');
    }
  };

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const skip = (seconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime += seconds;
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

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleCommentSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newComment.trim() && !isSubmitting) {
      setIsSubmitting(true);
      
      const comment: Comment = {
        id: Math.random().toString(36).substr(2, 9),
        text: newComment.trim(),
        timestamp: Date.now(),
      };

      const updatedComments = [...comments, comment];
      setComments(updatedComments);
      localStorage.setItem('comments', JSON.stringify(updatedComments));
      setNewComment('');
      setIsSubmitting(false);
    }
  };

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  const visibleComments = showAllComments ? comments : comments.slice(0, 3);
  const hasMoreComments = comments.length > 3;

  const clearUserData = () => {
    // Clear all stored data
    localStorage.removeItem('totalLikes');
    localStorage.removeItem('totalDislikes');
    localStorage.removeItem(`vote_${userId.current}`);
    localStorage.removeItem('comments');
    
    // Reset state
    setLikeCount(0);
    setDislikeCount(0);
    setIsLiked(false);
    setIsDisliked(false);
    setComments([]);
  };

  // Close speed popup when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (speedPopupRef.current && !speedPopupRef.current.contains(event.target as Node)) {
        setShowSpeedPopup(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSpeedChange = (speed: number) => {
    const newSpeed = Math.max(0.75, Math.min(2, speed));
    if (audioRef.current) {
      audioRef.current.playbackRate = newSpeed;
      setPlaybackSpeed(newSpeed);
    }
  };

  const SpeedPopup = () => {
    const speeds = [0.75, 1.0, 1.25, 1.5, 2.0];
    
    return (
      <div 
        ref={speedPopupRef}
        className="absolute top-full left-0 mt-2 bg-white dark:bg-gray-800 rounded-lg shadow-xl p-4 w-64 z-50"
      >
        <div className="text-center mb-4">
          <span className="text-2xl font-semibold text-gray-800 dark:text-gray-200">
            {playbackSpeed}x
          </span>
        </div>
        
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => handleSpeedChange(playbackSpeed - 0.25)}
            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <HiMinus className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
          
          <input
            type="range"
            min="0.75"
            max="2"
            step="0.25"
            value={playbackSpeed}
            onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
            className="flex-1 mx-4 h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
          />
          
          <button
            onClick={() => handleSpeedChange(playbackSpeed + 0.25)}
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
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {speed === 1 ? 'Normal' : `${speed}x`}
            </button>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className={`min-h-screen ${isDark ? 'dark' : ''}`}>
      <div className="bg-white dark:bg-gray-900 min-h-screen flex flex-col items-center p-8">
        {/* Fixed height player container */}
        <div className="w-full max-w-2xl bg-blue-50 dark:bg-gray-800 rounded-lg shadow-xl p-6 mb-4">
          {/* Header with speed and controls */}
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
              {showSpeedPopup && <SpeedPopup />}
            </div>
            <div className="flex space-x-2">
              {SHOW_CLEAR_BUTTON && (
                <button
                  onClick={clearUserData}
                  className="p-2 rounded-full hover:bg-blue-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors duration-200"
                  title="Clear all interactions"
                >
                  <TbClearAll className="w-5 h-5" />
                </button>
              )}
              <button
                onClick={() => setIsDark(!isDark)}
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
            src="/Episode6.mp3"
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
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
            <div className="border-t dark:border-gray-700 pt-4 mt-4">
              <div className="flex justify-center space-x-8">
                <button
                  onClick={handleLike}
                  className="flex items-center space-x-2 p-2 rounded-lg hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-200"
                >
                  {isLiked ? (
                    <AiFillLike className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  ) : (
                    <AiOutlineLike className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                  )}
                  <span className="text-gray-600 dark:text-gray-400 font-medium">{likeCount}</span>
                </button>
                <button
                  onClick={handleDislike}
                  className="flex items-center space-x-2 p-2 rounded-lg hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-200"
                >
                  {isDisliked ? (
                    <AiFillDislike className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  ) : (
                    <AiOutlineDislike className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                  )}
                  <span className="text-gray-600 dark:text-gray-400 font-medium">{dislikeCount}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Scrollable Comments Section */}
        <div className="w-full max-w-2xl bg-blue-50 dark:bg-gray-800 rounded-lg shadow-xl p-6 overflow-y-auto">
          <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4">
            Comments ({comments.length})
          </h3>
          
          {/* Comment Input */}
          <form onSubmit={handleCommentSubmit} className="mb-6">
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                className="flex-1 px-4 py-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 focus:outline-none focus:border-blue-500 dark:focus:border-blue-400"
                maxLength={500}
              />
              <button
                type="submit"
                disabled={!newComment.trim() || isSubmitting}
                className="p-2 rounded-full transition-colors duration-200 disabled:text-gray-400 dark:disabled:text-gray-600 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 disabled:hover:text-gray-400 dark:disabled:hover:text-gray-600"
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
                <p className="text-gray-700 dark:text-gray-300 mb-2">{comment.text}</p>
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
              className="mt-4 flex items-center space-x-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors duration-200"
            >
              <span>{showAllComments ? 'Show Less' : 'Show More'}</span>
              {showAllComments ? (
                <FaChevronUp className="w-4 h-4" />
              ) : (
                <FaChevronDown className="w-4 h-4" />
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App; 