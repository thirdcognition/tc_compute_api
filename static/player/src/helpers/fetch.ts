import { urlFormatter, config } from "./url.ts";
import session from "./session.tsx";

interface FetchOptions extends RequestInit {
    headers?: HeadersInit;
}

const cache = {};

function memoize(fn: Function, ttl = 5000) {
    const promiseCache: { [key: string]: Promise<any> } = {};
    return async function (...args: any[]) {
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

export async function fetchData(
    endpoint: string,
    options: FetchOptions = {}
): Promise<any> {
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

const memoizedFetchData = memoize(fetchData);
const memoizedFetchDataLongCache = memoize(fetchData, 60000 * 15);

export function fetchDataWithMemoization(
    endpoint: string,
    options: FetchOptions = { method: "GET" },
    forceCache: boolean = false,
    shortCache: boolean = false
): Promise<any> {
    const fn = shortCache ? memoizedFetchData : memoizedFetchDataLongCache;
    if (
        options.method &&
        options.method.toUpperCase() !== "GET" &&
        !forceCache
    ) {
        return fetchData(endpoint, options);
    }
    return fn(endpoint, options);
}

export async function fetchPublicPanels(): Promise<any[]> {
    const panels = await fetchDataWithMemoization("/panel/discussions/");
    return Array.isArray(panels)
        ? panels.filter((panel) => panel.metadata && panel.metadata.display_tag)
        : [];
}

export async function fetchPanelFiles(panelId: string): Promise<{
    updatedTranscriptUrls: Record<string, string>;
    updatedAudioUrls: Record<string, string>;
}> {
    const data = await fetchDataWithMemoization(`/panel/${panelId}/files`);

    const updatedTranscriptUrls = urlFormatter(data.transcript_urls);
    const updatedAudioUrls = urlFormatter(data.audio_urls);
    return { updatedTranscriptUrls, updatedAudioUrls };
}

export async function fetchPanelAudios(panelId: string): Promise<any> {
    return fetchDataWithMemoization(`/panel/${panelId}/audios`);
}

export async function fetchPanelTranscripts(panelId: string): Promise<any> {
    return fetchDataWithMemoization(`/panel/${panelId}/transcripts`);
}

export async function fetchTranscriptContent(
    transcriptUrl: string
): Promise<string> {
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
    transcriptId: string,
    transcript: any,
    newCronjob: any
): Promise<any> {
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

    if (!response.ok) {
        throw new Error("Failed to update transcript");
    }

    return response.json();
}

export async function fetchPanelDetails(panelId: string): Promise<{
    discussionData: any;
    transcriptData: any;
    transcriptSources: any;
    audioData: any;
    filesData: {
        transcript_urls: Record<string, string>;
        audio_urls: Record<string, string>;
    };
}> {
    try {
        const panelDetails = await fetchDataWithMemoization(
            `/panel/${panelId}/details`,
            {},
            true
        );
        let language = session.getLanguage();
        let filteredTranscripts = panelDetails.transcripts.filter(
            (transcript: any) =>
                transcript.lang?.toLowerCase() === language?.toLowerCase()
        );
        if (filteredTranscripts.length == 0) {
            language = "english";
            filteredTranscripts = panelDetails.transcripts.filter(
                (transcript: any) =>
                    transcript.lang?.toLowerCase() === language?.toLowerCase()
            );
        }
        const filteredAudios = panelDetails.audios.filter(
            (audio: any) =>
                audio.lang?.toLowerCase() === language?.toLowerCase()
        );
        return {
            discussionData: panelDetails.panel,
            transcriptData: filteredTranscripts,
            transcriptSources: panelDetails.transcript_sources,
            audioData: filteredAudios,
            filesData: {
                transcript_urls: urlFormatter(panelDetails.transcript_urls),
                audio_urls: urlFormatter(panelDetails.audio_urls)
            }
        };
    } catch (error) {
        console.error("Error refreshing panel data:", error);
        throw error;
    }
}

export async function createPanel(data: any): Promise<string> {
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

export async function createTranscript(data: any): Promise<string> {
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

export async function createAudio(data: any): Promise<string> {
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
