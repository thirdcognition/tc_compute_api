/// <reference types="react-scripts" />
import posthog from "posthog-js";

const POSTHOG_API_KEY = process.env.REACT_APP_POSTHOG_API_KEY || "";

posthog.init(POSTHOG_API_KEY, {
    api_host: "https://eu.i.posthog.com",
    person_profiles: "always" // Create profiles for anonymous users as well
});

const DEBUG_MODE = true; // process.env.REACT_APP_DEBUG_MODE === "true";

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

const updateHeartbeat = (session: Session): void => {
    session.lastHeartbeat = Date.now();
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
};

export const getUserId = () => {
    let userId = localStorage.getItem("userId");
    if (!userId) {
        userId = Math.random().toString(36).substring(2, 9);
        localStorage.setItem("userId", userId);
    }
    return userId;
};

export const trackEvent = (
    eventName: string,
    category: string,
    label: string | undefined,
    userId: React.RefObject<string>,
    sessionRef: React.RefObject<Session | null>,
    customData?: Record<string, unknown> // Add custom data parameter
) => {
    if (DEBUG_MODE) {
        console.group("PostHog Event Tracking");
        console.log("Event Name:", eventName);
        console.log("Category:", category);
        console.log("Label:", label);
        console.log("User ID:", userId.current);
        console.log("Session ID:", sessionRef.current?.id);
        if (customData) {
            console.log("Custom Data:", customData); // Log custom data
        }
        console.groupEnd();
    }

    posthog.capture(eventName, {
        category,
        label,
        user_id: userId.current,
        session_id: sessionRef.current?.id,
        timestamp: new Date().toISOString(),
        page_title: document.title,
        page_location: window.location.href,
        debug_mode: DEBUG_MODE,
        ...customData // Merge custom data
    });
};

export const initializeAnalytics = (
    sessionRef: React.RefObject<Session | null>,
    userId: React.RefObject<string>
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

    const existingSession = cleanupOldSessions();
    if (existingSession) {
        sessionRef.current = existingSession;
    } else {
        sessionRef.current = session;
    }

    posthog.identify(userId.current || "anonymous", {
        session_id: session.id
    });

    posthog.capture("$pageview", {
        page: window.location.pathname,
        title: document.title,
        location: window.location.href,
        ...(window.location.pathname.startsWith("/player/panel/") && {
            panelId: window.location.pathname.split("/player/panel/")[1]
        })
    });

    if (DEBUG_MODE) {
        console.log("PostHog Initialization:", {
            apiKey: POSTHOG_API_KEY,
            debug: DEBUG_MODE,
            sessionId: sessionId
        });
    }

    const heartbeatInterval = setInterval(() => {
        if (sessionRef.current) {
            updateHeartbeat(sessionRef.current);
        }
    }, HEARTBEAT_INTERVAL);

    const handleStorageChange = (e: StorageEvent) => {
        if (e.key === SESSION_KEY && e.newValue && sessionRef.current) {
            const newSession = JSON.parse(e.newValue) as Session;
            if (newSession.tabId !== sessionRef.current.tabId) {
                sessionRef.current = newSession;
            }
        }
    };

    window.addEventListener("storage", handleStorageChange);

    return () => {
        clearInterval(heartbeatInterval);
        window.removeEventListener("storage", handleStorageChange);
    };
};
