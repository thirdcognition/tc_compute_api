import { urlFormatter, config } from "./url.js";
import session from "./session.js";

const cache = {};

function memoize(fn, ttl = 5000) {
    const promiseCache = {};
    return async function (...args) {
        const key = JSON.stringify(args);
        if (cache.hasOwnProperty(key)) {
            const { result, expiry } = cache[key];
            if (Date.now() < expiry) {
                return result;
            }
            delete cache[key];
        }
        if (promiseCache.hasOwnProperty(key)) {
            return promiseCache[key];
        }
        const expiry = Date.now() + ttl;
        const promise = fn(...args);
        promiseCache[key] = promise;
        const result = await promise;
        delete promiseCache[key];
        cache[key] = { result, expiry };
        return result;
    };
}

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

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
}

const memoizedFetchData = memoize(fetchData);

export function fetchDataWithMemoization(endpoint, options = {}) {
    if (options.method && options.method.toUpperCase() !== "GET") {
        return fetchData(endpoint, options);
    }
    return memoizedFetchData(endpoint, options);
}

export async function fetchPanels() {
    const panels = await fetchDataWithMemoization("/panel/discussions/");
    return Array.isArray(panels) ? panels : [];
}

export async function fetchPanelFiles(panelId) {
    const data = await fetchDataWithMemoization(`/panel/${panelId}/files`);

    const updatedTranscriptUrls = urlFormatter(data.transcript_urls);
    const updatedAudioUrls = urlFormatter(data.audio_urls);
    return { updatedTranscriptUrls, updatedAudioUrls };
}

export async function fetchPanelAudios(panelId) {
    return fetchDataWithMemoization(`/panel/${panelId}/audios`);
}

export async function fetchPanelTranscripts(panelId) {
    return fetchDataWithMemoization(`/panel/${panelId}/transcripts`);
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

export async function updateTranscript(transcriptId, transcript, newCronjob) {
    const response = await fetchData(`/panel/transcript/${transcriptId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.getAccessToken()}`
        },
        body: JSON.stringify({
            ...transcript,
            generation_cronjob: newCronjob || null,
            metadata: {
                ...transcript.metadata,
                cronjob: newCronjob || null
            }
        })
    });

    if (response) {
        return { success: true, response: response };
    }
    throw new Error("Failed to update transcript");
}

export async function fetchPanelDetails(panelId) {
    try {
        const panelDetails = await fetchDataWithMemoization(
            `/panel/${panelId}/details`
        );
        return {
            discussionData: panelDetails.panel,
            transcriptData: panelDetails.transcripts,
            transcriptSources: panelDetails.transcript_sources,
            audioData: panelDetails.audios,
            filesData: {
                transcript_urls: urlFormatter(panelDetails.transcript_urls),
                audio_urls: urlFormatter(panelDetails.audio_urls)
            }
        };

        // const [discussionData, transcriptData, audioData, filesData] =
        //     await Promise.all([
        //         fetchData(`/panel/${panelId}`),
        //         fetchData(`/panel/${panelId}/transcripts`),
        //         fetchData(`/panel/${panelId}/audios`),
        //         fetchData(`/panel/${panelId}/files`)
        //     ]);

        // return { discussionData, transcriptData, audioData, filesData };
    } catch (error) {
        console.error("Error refreshing panel data:", error);
        throw error;
    }
}

export async function updateTranscriptFile(transcriptId, content) {
    try {
        const response = await fetchData(
            `/panel/transcript/${transcriptId}/update_file`,
            {
                method: "PUT",
                headers: {
                    // Explicitly define all required headers
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${session.getAccessToken()}` // Get token directly
                },
                body: JSON.stringify({ content: content })
            }
        );

        // Assuming the API returns the updated transcript object on success
        if (response && response.id === transcriptId) {
            console.log("Transcript file updated successfully:", response);
            return { success: true, transcript: response };
        } else {
            // Handle cases where the response might not be as expected
            // even if the fetch itself didn't throw an error (e.g., status 200 but unexpected body)
            console.error(
                "Failed to update transcript file: Unexpected response format",
                response
            );
            return {
                success: false,
                error: "Unexpected response format after update."
            };
        }
    } catch (error) {
        // fetchData already handles basic HTTP errors and unauthorized access
        console.error("Error updating transcript file:", error);
        // Re-throw or return a specific error structure
        return { success: false, error: error.message || "Unknown error" };
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

export async function updatePanel(panelId, data) {
    try {
        const response = await fetchData(`/panel/${panelId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${session.getAccessToken()}`
            },
            body: JSON.stringify(data)
        });

        if (response) {
            return { success: true, response: response };
        } else {
            console.error("Failed to update panel:", response);
            return { success: false };
        }
    } catch (error) {
        console.error("Error updating panel:", error);
        return { success: false };
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

export async function deletePanel(panelId) {
    try {
        await fetchData(`/panel/${panelId}`, {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${session.getAccessToken()}`
            }
        });
    } catch (error) {
        console.error("Error deleting panel:", error);
        throw error;
    }
}

export async function deleteTranscript(transcriptId) {
    try {
        await fetchData(`/panel/transcript/${transcriptId}`, {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${session.getAccessToken()}`
            }
        });
    } catch (error) {
        console.error("Error deleting transcript:", error);
        throw error;
    }
}

export async function deleteAudio(audioId) {
    try {
        await fetchData(`/panel/audio/${audioId}`, {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${session.getAccessToken()}`
            }
        });
    } catch (error) {
        console.error("Error deleting audio.", error);
        throw error;
    }
}

export async function fetchNewsLinks(configs) {
    try {
        const response = await fetchData("/panel/news_links", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${session.getAccessToken()}`
            },
            body: JSON.stringify(configs)
        });
        return response.news_links;
    } catch (error) {
        console.error("Error fetching news links:", error);
        throw error;
    }
}
