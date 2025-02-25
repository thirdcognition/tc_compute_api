import React, { useRef, useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Panel from "./components/Panel.tsx";
import {
    initializeAnalytics,
    Session,
    getUserId
} from "./helpers/analytics.ts";
import { SessionProvider, session } from "./helpers/session.tsx";

function App() {
    const userId = useRef(getUserId());
    const sessionRef = useRef<Session | null>(null);

    // Initialize session and analytics
    useEffect(() => {
        console.log("Initializing GA...");
        initializeAnalytics(sessionRef, userId);
    }, []);

    // "bg-gray-100 dark:bg-gray-800

    const defaultPanelId = session.getPanelId(); // Retrieve panelId from localStorage

    const [refreshKey, setRefreshKey] = useState(0);

    useEffect(() => {
        session.setRefreshCallback(() => setRefreshKey((prev) => prev + 1));
    }, []);

    return (
        <SessionProvider>
            <Router basename="/player">
                <div className="min-h-screen" key={refreshKey}>
                    <div className="min-h-screen flex flex-col items-center p-2 w-full">
                        <Routes>
                            <Route
                                path="/"
                                element={
                                    <Panel
                                        userId={userId}
                                        sessionRef={sessionRef}
                                        defaultPanelId={
                                            defaultPanelId ?? undefined
                                        }
                                    />
                                }
                            />
                            <Route
                                path="/panel/:panelId"
                                element={
                                    <Panel
                                        userId={userId}
                                        sessionRef={sessionRef}
                                    />
                                }
                            />
                        </Routes>
                    </div>
                </div>
            </Router>
        </SessionProvider>
    );
}

export default App;
