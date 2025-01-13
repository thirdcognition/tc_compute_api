import React, { useState, useRef, useEffect } from 'react';
import ReactGA from 'react-ga4';
import { BsFillPlayFill, BsPauseFill, BsMoonFill, BsSunFill } from 'react-icons/bs';
import { BiSkipNext, BiSkipPrevious } from 'react-icons/bi';
import { FiRotateCcw, FiRotateCw } from 'react-icons/fi';
import { AiOutlineLike, AiOutlineDislike, AiFillLike, AiFillDislike } from 'react-icons/ai';
import { FaChevronDown, FaChevronUp } from 'react-icons/fa';
import { IoSendSharp } from 'react-icons/io5';
import { TbClearAll } from 'react-icons/tb';
import { HiMinus, HiPlus } from 'react-icons/hi';

// Configuration
const SHOW_CLEAR_BUTTON = false; // Set this to false to hide the clear button
const GA_MEASUREMENT_ID = 'G-5HQD9T8EHK';

// Declare gtag type
declare global {
  interface Window {
    gtag: (...args: any[]) => void;
  }
}

// set the debug mode to true or false
const DEBUG_MODE = true;

// Enable GA4 debug mode in development
if (process.env.NODE_ENV === 'development' && DEBUG_MODE) {
  window.localStorage.setItem('debug', 'ga:*');
  // Enable GA4 debug view
  if (window.gtag) {
    window.gtag('config', GA_MEASUREMENT_ID, {
      debug_mode: DEBUG_MODE
    });
  }
}

// Session management
const SESSION_KEY = 'app_session';
const HEARTBEAT_INTERVAL = 10000; // 10 seconds

interface Session {
  id: string;
  startTime: number;
  lastHeartbeat: number;
  tabId: string;
}

// Generate a unique user ID if it doesn't exist
const getUserId = () => {
  let userId = localStorage.getItem('userId');
  if (!userId) {
    userId = Math.random().toString(36).substr(2, 9);
    localStorage.setItem('userId', userId);
  }
  return userId;
};

// Custom analytics initialization
const initializeAnalytics = (): Session => {
  const sessionId = Math.random().toString(36).substring(2);
  const timestamp = Date.now();
  const session: Session = {
    id: sessionId,
    startTime: timestamp,
    lastHeartbeat: timestamp,
    tabId: Math.random().toString(36).substring(2)
  };
  
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  
  // Updated GA4 initialization with debug options
  ReactGA.initialize(GA_MEASUREMENT_ID, {
    gtagOptions: {
      debug_mode: DEBUG_MODE,
      send_page_view: true
    }
  });

  // Send initial pageview with more details
  ReactGA.send({
    hitType: "pageview",
    page: window.location.pathname,
    title: document.title,
    location: window.location.href
  });

  // Log initialization in debug mode
  if (DEBUG_MODE) {
    console.log('GA4 Initialization:', {
      measurementId: GA_MEASUREMENT_ID,
      debug: DEBUG_MODE,
      sessionId: sessionId,
      userId: getUserId()
    });
  }
  
  return session;
};

// Heartbeat to maintain session
const updateHeartbeat = (session: Session): void => {
  session.lastHeartbeat = Date.now();
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
};

// Clean up old sessions
const cleanupOldSessions = (): Session | null => {
  const currentTime = Date.now();
  const threshold = currentTime - (HEARTBEAT_INTERVAL * 3);
  
  try {
    const sessionData = localStorage.getItem(SESSION_KEY);
    if (!sessionData) return null;
    
    const session = JSON.parse(sessionData) as Session;
    if (session.lastHeartbeat < threshold) {
      localStorage.removeItem(SESSION_KEY);
      return null;
    }
    return session;
  } catch {
    return null;
  }
};

interface Comment {
  id: string;
  text: string;
  timestamp: number;
}

const DebugGA = () => {
  useEffect(() => {
    console.group('GA4 Debug Information');
    console.log('GA Measurement ID:', GA_MEASUREMENT_ID);
    console.log('GA Initialized:', !!ReactGA.ga());
    console.log('Debug Mode:', DEBUG_MODE);
    console.log('Current Page:', window.location.pathname);
    console.groupEnd();
  }, []);

  return null;
};

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
  const sessionRef = useRef<Session | null>(null);

  // Initialize session and analytics
  useEffect(() => {
    // Add these console logs
    console.log('Initializing GA...');
    console.log('GA Measurement ID:', GA_MEASUREMENT_ID);
    
    if (!ReactGA.ga()) {
      sessionRef.current = initializeAnalytics();
      // Add this check
      console.log('GA Initialized:', !!ReactGA.ga());
    } else {
      console.log('GA already initialized');
      const existingSession = cleanupOldSessions();
      if (existingSession) {
        sessionRef.current = existingSession;
      } else {
        sessionRef.current = initializeAnalytics();
      }
    }

    // Set up heartbeat
    const heartbeatInterval = setInterval(() => {
      if (sessionRef.current) {
        updateHeartbeat(sessionRef.current);
      }
    }, HEARTBEAT_INTERVAL);

    // Set up storage event listener to handle multiple tabs
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === SESSION_KEY && e.newValue && sessionRef.current) {
        const newSession = JSON.parse(e.newValue) as Session;
        if (newSession.tabId !== sessionRef.current.tabId) {
          // Another tab is active, update our session if needed
          sessionRef.current = newSession;
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Cleanup
    return () => {
      clearInterval(heartbeatInterval);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

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

  // Track user interactions with GA4
  const trackEvent = (eventName: string, category: string, label?: string) => {
    if (DEBUG_MODE) {
      console.group('GA4 Event Tracking');
      console.log('Event Name:', eventName);
      console.log('Category:', category);
      console.log('Label:', label);
      console.log('User ID:', userId.current);
      console.groupEnd();
    }

    // Enhanced event tracking with more parameters
    ReactGA.event(eventName, {
      event_category: category,
      event_label: label,
      user_id: userId.current,
      session_id: sessionRef.current?.id,
      timestamp: new Date().toISOString(),
      page_title: document.title,
      page_location: window.location.href,
      debug_mode: DEBUG_MODE
    });

    // Verify GA object exists and log any issues
    if (!ReactGA.ga()) {
      console.error('GA4 not initialized properly');
      return;
    }
  };

  const handleLike = () => {
    const userVote = localStorage.getItem(`vote_${userId.current}`);
    
    if (isLiked) {
      // Remove like
      setLikeCount(prev => prev - 1);
      setIsLiked(false);
      localStorage.setItem('totalLikes', String(likeCount - 1));
      localStorage.removeItem(`vote_${userId.current}`);
      trackEvent('unlike', 'Engagement', 'Remove Like');
    } else {
      // Add like
      if (isDisliked) {
        // Remove previous dislike
        setDislikeCount(prev => prev - 1);
        setIsDisliked(false);
        localStorage.setItem('totalDislikes', String(dislikeCount - 1));
        trackEvent('remove_dislike', 'Engagement', 'Remove Dislike');
      }
      setLikeCount(prev => prev + 1);
      setIsLiked(true);
      localStorage.setItem('totalLikes', String(likeCount + 1));
      localStorage.setItem(`vote_${userId.current}`, 'like');
      trackEvent('like', 'Engagement', 'Add Like');
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
      trackEvent('undislike', 'Engagement', 'Remove Dislike');
    } else {
      // Add dislike
      if (isLiked) {
        // Remove previous like
        setLikeCount(prev => prev - 1);
        setIsLiked(false);
        localStorage.setItem('totalLikes', String(likeCount - 1));
        trackEvent('remove_like', 'Engagement', 'Remove Like');
      }
      setDislikeCount(prev => prev + 1);
      setIsDisliked(true);
      localStorage.setItem('totalDislikes', String(dislikeCount + 1));
      localStorage.setItem(`vote_${userId.current}`, 'dislike');
      trackEvent('dislike', 'Engagement', 'Add Dislike');
    }
  };

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        trackEvent('pause', 'Player', 'Pause Audio');
        setIsPlaying(false);
      } else {
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              setIsPlaying(true);
              trackEvent('play', 'Player', 'Play Audio');
            })
            .catch(error => {
              // Handle any play() errors here
              console.error('Error attempting to play:', error);
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
        'skip', 
        'Player', 
        `Skip ${seconds > 0 ? 'Forward' : 'Backward'}: ${Math.abs(seconds)}s`
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

      trackEvent('comment_submit', 'Engagement', `Comment Length: ${newComment.trim().length}`);
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

  const handleSpeedChange = (newSpeed: number) => {
    setPlaybackSpeed(newSpeed);
    if (audioRef.current) {
      const wasPlaying = !audioRef.current.paused;
      const currentTime = audioRef.current.currentTime;
      audioRef.current.playbackRate = newSpeed;
      
      // If audio was playing, ensure it continues playing after speed change
      if (wasPlaying) {
        const playPromise = audioRef.current.play();
        if (playPromise !== undefined) {
          playPromise.catch((error) => {
            console.log("Playback error:", error);
          });
        }
      }

      trackEvent('speed_change', 'Player', `Speed: ${newSpeed}x`);
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

  // Add new tracking for audio progress
  useEffect(() => {
    let progressInterval: NodeJS.Timeout;
    
    if (isPlaying) {
      progressInterval = setInterval(() => {
        if (audioRef.current) {
          const progress = (audioRef.current.currentTime / audioRef.current.duration) * 100;
          trackEvent('progress', 'Player', `Progress: ${Math.floor(progress)}%`);
        }
      }, 10000); // Track progress every 10 seconds
    }

    return () => clearInterval(progressInterval);
  }, [isPlaying]);

  // Add tracking for time spent
  useEffect(() => {
    let timeSpentInterval: NodeJS.Timeout;
    
    if (isPlaying) {
      const startTime = Date.now();
      timeSpentInterval = setInterval(() => {
        const timeSpent = Math.floor((Date.now() - startTime) / 1000);
        trackEvent('time_spent', 'Player', `Time Spent: ${timeSpent}s`);
      }, 60000); // Track time spent every minute
    }

    return () => clearInterval(timeSpentInterval);
  }, [isPlaying]);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    trackEvent(
      'theme_toggle', 
      'UI', 
      `Theme: ${newTheme ? 'Dark' : 'Light'}`
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
            src="https://cehncdkfuslzatlfawma.supabase.co/storage/v1/object/public/public_panels/panel_4bdb5eba-20bd-4eab-9f89-519126c7de3e_6cce40af-a079-49af-9dad-cc8741d88485_64614690-5116-4c18-9138-2492dff137ef_audio.mp3"
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