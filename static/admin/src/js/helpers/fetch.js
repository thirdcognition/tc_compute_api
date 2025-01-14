import { urlFormatter, config } from "./url.js";
import session from "./session.js";

export async function fetchData(endpoint, options = {}) {
    const { protocol, hostname, port } = config;
    const response = await fetch(
        `${protocol}//${hostname}${port ? `:${port}` : ""}${endpoint}`,
        {
            method: "GET",
            headers: {
                Accept: "application/json",
                Authorization: `Bearer ${session.getAccessToken()}`
            },
            ...options
        }
    );

    if (response.status === 401 || response.status === 403) {
        session.handleUnauthorized();
        throw new Error("Unauthorized access - redirecting to login.");
    }

    return response.json();
}

export async function fetchPublicPanels() {
    const panels = await fetchData("/panel/discussions/");
    return Array.isArray(panels) ? panels : [];
}

export async function fetchPanelFiles(panelId) {
    const data = await fetchData(`/panel/${panelId}/files`);

    const updatedTranscriptUrls = urlFormatter(data.transcript_urls);
    const updatedAudioUrls = urlFormatter(data.audio_urls);
    return { updatedTranscriptUrls, updatedAudioUrls };
}

export async function fetchPanelAudios(panelId) {
    return fetchData(`/panel/${panelId}/audios`);
}

export async function fetchPanelTranscripts(panelId) {
    return fetchData(`/panel/${panelId}/transcripts`);
}

export async function fetchTranscriptContent(transcriptUrl) {
    const response = await fetch(transcriptUrl, {
        headers: {
            Authorization: `Bearer ${session.getAccessToken()}`
        }
    });

    if (!response.ok) {
        throw new Error("Error fetching transcript");
    }

    return response.text();
}

export async function updateTranscript(
    transcriptId,
    transcript,
    newUpdateCycle
) {
    const response = await fetchData(`/panel/transcript/${transcriptId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.getAccessToken()}`
        },
        body: JSON.stringify({
            ...transcript,
            generation_interval: newUpdateCycle || null,
            metadata: {
                ...transcript.metadata,
                update_cycle: newUpdateCycle || null
            }
        })
    });

    if (!response.ok) {
        throw new Error("Failed to update transcript");
    }

    return response.json();
}

export async function refreshPanelData(panelId) {
    try {
        const [discussionData, transcriptData, audioData, filesData] =
            await Promise.all([
                fetchData(`/panel/${panelId}`),
                fetchData(`/panel/${panelId}/transcripts`),
                fetchData(`/panel/${panelId}/audios`),
                fetchData(`/panel/${panelId}/files`)
            ]);

        return { discussionData, transcriptData, audioData, filesData };
    } catch (error) {
        console.error("Error refreshing panel data:", error);
        throw error;
    }
}

export async function createPanel(data) {
    try {
        const result = await fetchData(`/panel/discussion`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${session.getAccessToken()}`
            },
            body: JSON.stringify(data)
        });
        return result.panel_id;
    } catch (error) {
        console.error("Error creating panel:", error);
        throw error;
    }
}

export async function createTranscript(data) {
    try {
        const result = await fetchData(`/panel/transcript`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${session.getAccessToken()}`
            },
            body: JSON.stringify(data)
        });
        return result.task_id;
    } catch (error) {
        console.error("Error creating transcript:", error);
        throw error;
    }
}

export async function createAudio(data) {
    try {
        const result = await fetchData(`/panel/audio`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${session.getAccessToken()}`
            },
            body: JSON.stringify(data)
        });
        return result.task_id;
    } catch (error) {
        console.error("Error creating audio.", error);
        throw error;
    }
}
