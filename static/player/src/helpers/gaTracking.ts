import ReactGA from "react-ga4";

const DEBUG_MODE = true;
const GA_MEASUREMENT_ID = "G-5HQD9T8EHK";

// Session management
export const SESSION_KEY = "app_session";
export const HEARTBEAT_INTERVAL = 10000; // 10 seconds

export interface Session {
    id: string;
    startTime: number;
    lastHeartbeat: number;
    tabId: string;
}

const cleanupOldSessions = (): Session | null => {
    const currentTime = Date.now();
    const threshold = currentTime - HEARTBEAT_INTERVAL * 3;

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

// Heartbeat to maintain session
const updateHeartbeat = (session: Session): void => {
    session.lastHeartbeat = Date.now();
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
};

// Generate a unique user ID if it doesn't exist
export const getUserId = () => {
    let userId = localStorage.getItem("userId");
    if (!userId) {
        userId = Math.random().toString(36).substr(2, 9);
        localStorage.setItem("userId", userId);
    }
    return userId;
};

export const trackEvent = (
    eventName: string,
    category: string,
    label: string | undefined,
    userId: React.RefObject<string>,
    sessionRef: React.RefObject<Session | null>
) => {
    if (DEBUG_MODE) {
        console.group("GA4 Event Tracking");
        console.log("Event Name:", eventName);
        console.log("Category:", category);
        console.log("Label:", label);
        console.log("User ID:", userId.current);
        console.groupEnd();
    }

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

    if (!ReactGA.ga()) {
        console.error("GA4 not initialized properly");
        return;
    }
};

export const initializeAnalytics = (
    sessionRef: React.MutableRefObject<Session | null>,
    userId: React.MutableRefObject<string>
) => {
    const sessionId = Math.random().toString(36).substring(2);
    const timestamp = Date.now();
    const session: Session = {
        id: sessionId,
        startTime: timestamp,
        lastHeartbeat: timestamp,
        tabId: Math.random().toString(36).substring(2)
    };

    localStorage.setItem(SESSION_KEY, JSON.stringify(session));

    // Initialize GA if not already initialized
    if (!ReactGA.ga()) {
        ReactGA.initialize(GA_MEASUREMENT_ID, {
            gtagOptions: {
                debug_mode: DEBUG_MODE,
                send_page_view: true
            }
        });
    } else {
        console.log("GA already initialized");
        const existingSession = cleanupOldSessions();
        if (existingSession) {
            sessionRef.current = existingSession;
        } else {
            sessionRef.current = session;
        }
    }

    ReactGA.send({
        hitType: "pageview",
        page: window.location.pathname,
        title: document.title,
        location: window.location.href
    });

    if (DEBUG_MODE) {
        console.log("GA4 Initialization:", {
            measurementId: GA_MEASUREMENT_ID,
            debug: DEBUG_MODE,
            sessionId: sessionId
        });
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

    window.addEventListener("storage", handleStorageChange);

    // Cleanup
    return () => {
        clearInterval(heartbeatInterval);
        window.removeEventListener("storage", handleStorageChange);
    };
};

// Clean up old sessions
