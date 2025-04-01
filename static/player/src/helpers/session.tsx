import React, { createContext, useContext, ReactNode } from "react";
import { getCookie, setCookie } from "./auth.ts";
import { fetchData } from "./fetch.ts";

class Session {
    private accessToken: string;
    private navigate: ((path: string) => void) | null;
    private refreshCallback: (() => void) | null;

    constructor() {
        this.accessToken = getCookie("access_token") || "";
        this.navigate = null;
        this.refreshCallback = null;
    }

    setNavigate(navigate: (path: string) => void): void {
        this.navigate = navigate;
    }

    setRefreshCallback(callback: () => void): void {
        this.refreshCallback = callback;
    }

    setLanguage(language: string): void {
        localStorage.setItem("language", language);
    }

    getLanguage(): string {
        return localStorage.getItem("language") || "en";
    }

    setPanelId(panelId: string): void {
        localStorage.setItem("panelId", panelId);
    }

    getPanelId(): string | null {
        return localStorage.getItem("panelId");
    }

    async login(email: string, password: string): Promise<string> {
        const data = await fetchData(`/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json"
            },
            body: JSON.stringify({ email, password })
        });
        setCookie("access_token", data.access_token, 1);
        this.accessToken = data.access_token;
        return data.access_token;
    }

    logout(): void {
        setCookie("access_token", "", -1);
        this.accessToken = "";
    }

    getAccessToken(): string {
        return this.accessToken;
    }

    isAuthenticated(): boolean {
        return !!this.accessToken;
    }

    handleUnauthorized(): void {
        console.log("Handle unauthorized");
        this.logout();
        this.refreshApp();
    }

    refreshApp(): void {
        console.log("Refreshing app...");
        if (this.refreshCallback) {
            this.refreshCallback(); // Trigger the re-render
        }
    }
}

// Create the SessionContext with a default value of null
export const session = new Session();
const SessionContext = createContext<Session | null>(null);

// Custom hook to use the session
// export const useSession = (): Session => {
//     const session = useContext(SessionContext);
//     if (!session) {
//         throw new Error("SessionContext is not provided");
//     }
//     return session;
// };

// Define the type for the SessionProvider's props
interface SessionProviderProps {
    children: ReactNode;
}

export const SessionProvider: React.FC<SessionProviderProps> = ({
    children
}) => {
    return (
        <SessionContext.Provider value={session}>
            {children}
        </SessionContext.Provider>
    );
};
export default session;
