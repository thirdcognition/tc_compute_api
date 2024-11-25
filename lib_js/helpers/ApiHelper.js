import "server-only";
class ApiConfig {
    constructor(host, port, authToken, refreshToken) {
        this.host = host;
        this.port = port;
        this.authToken = authToken;
        this.refreshToken = refreshToken;
    }
}

async function fetchWithAuth(apiConfig, endpoint, method, body) {
    if (!(apiConfig instanceof ApiConfig)) {
        throw new Error("Invalid ApiConfig object.");
    }

    const { host, port, authToken, refreshToken } = apiConfig;

    if (!host || !port || !authToken) {
        throw new Error(
            "ApiConfig is not correctly set up. Host, port, and authToken are required."
        );
    }

    const url = `${host ? `http://${host}` : ""}${port ? `:${port}` : ""}${endpoint}`;
    const response = await fetch(url, {
        method: method,
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${authToken}`,
            "Refresh-Authorization": `Bearer ${refreshToken}`
        },
        body: JSON.stringify(body)
    });

    if (!response.ok) {
        throw new Error(`Failed to ${method} ${endpoint} ${response.error}`);
    }

    return await response.json();
}

export { ApiConfig, fetchWithAuth };
