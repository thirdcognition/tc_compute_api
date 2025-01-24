// admin_js/helpers/session.js

import { getCookie, setCookie } from "./auth.js";
import { fetchData } from "./fetch.js";

class Session {
    constructor() {
        this.accessToken = getCookie("access_token") || "";
        this.navigate = null;
    }

    setNavigate(navigate) {
        this.navigate = navigate;
    }

    login(email, password) {
        return fetchData(`/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json"
            },
            body: JSON.stringify({ email, password })
        }).then((data) => {
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
        if (this.navigate) {
            this.navigate("/login");
        }
    }
}

const sessionInstance = new Session();
export default sessionInstance;
