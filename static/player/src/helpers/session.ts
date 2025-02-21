import { getCookie, setCookie } from "./auth.ts";
import { fetchData } from "./fetch.ts";

class Session {
    private accessToken: string;
    private navigate: ((path: string) => void) | null;

    constructor() {
        this.accessToken = getCookie("access_token") || "";
        this.navigate = null;
    }

    setNavigate(navigate: (path: string) => void): void {
        this.navigate = navigate;
    }

    setLanguage(language: string): void {
        localStorage.setItem("language", language);
    }

    getLanguage(): string {
        return localStorage.getItem("language") || "english";
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
        // if (this.navigate) {
        //     this.navigate("/login");
        // }
        this.logout();
        window.location.reload();
    }
}

export default new Session();
