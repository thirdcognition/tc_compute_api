// morning_show_js/helpers/session.js

import { getCookie, setCookie } from "./auth.js";

class Session {
    constructor() {
        this.accessToken = getCookie("access_token") || "";
        this.history = null;
    }

    setHistory(history) {
        this.history = history;
    }

    login(email, password) {
        return fetch(`${window.location.origin}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json"
            },
            body: JSON.stringify({ email, password })
        })
            .then((response) => response.json())
            .then((data) => {
                setCookie("access_token", data.access_token, 1);
                this.accessToken = data.access_token;
                return data.access_token;
            });
    }

    logout() {
        setCookie("access_token", "", -1);
        this.accessToken = "";
    }

    getAccessToken() {
        return this.accessToken;
    }

    isAuthenticated() {
        return !!this.accessToken;
    }

    handleUnauthorized() {
        if (this.history) {
            this.history.push("/login");
        }
    }
}

export default new Session();
