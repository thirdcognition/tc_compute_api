import React, { useRef, useEffect } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Panel from "./components/Panel.tsx";
import {
    initializeAnalytics,
    Session,
    getUserId
} from "./helpers/analytics.ts";
import session from "./helpers/session.ts";

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

    return (
        <Router basename="/player">
            <div className="min-h-screen">
                <div className="min-h-screen flex flex-col items-center p-2 w-full">
                    <Routes>
                        <Route
                            path="/"
                            element={
                                <Panel
                                    userId={userId}
                                    sessionRef={sessionRef}
                                    defaultPanelId={defaultPanelId ?? undefined}
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
    );
}

export default App;
