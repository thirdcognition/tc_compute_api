import {
    PanelDiscussionModel,
    PanelTranscriptModel,
    PanelAudioModel,
    PanelTranscriptSourceReferenceModel
} from "../models/supabase/panel.js";

/**
 * Fetch a single panel by its ID.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @param {string} panelId - The ID of the panel to fetch.
 * @returns {Promise<PanelDiscussionModel>} - The fetched panel.
 */
export async function getPanel(supabase, panelId) {
    const panel = await PanelDiscussionModel.fetchFromSupabase(supabase, {
        id: panelId
    });
    if (!panel) {
        throw new Error("Panel not found");
    }
    return panel;
}

/**
 * Fetch all existing panels.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @returns {Promise<PanelDiscussionModel[]>} - The list of panels.
 */
export async function listPanels(supabase) {
    return await PanelDiscussionModel.fetchExistingFromSupabase(supabase);
}

/**
 * Fetch detailed information about a panel, including its transcripts and audios.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @param {string} panelId - The ID of the panel to fetch details for.
 * @returns {Promise<Object>} - The panel details including transcripts and audios.
 */
export async function getPanelDetails(supabase, panelId) {
    const panel = await getPanel(supabase, panelId);
    const transcripts = await PanelTranscriptModel.fetchExistingFromSupabase(
        supabase,
        { panelId }
    );
    const audios = await PanelAudioModel.fetchExistingFromSupabase(supabase, {
        panelId
    });

    return {
        panel,
        transcripts,
        audios
    };
}

/**
 * Fetch public URLs for all transcripts and audios associated with a panel.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @param {string} panelId - The ID of the panel to fetch files for.
 * @returns {Promise<Object>} - The public URLs for transcripts and audios.
 */
export async function getPanelFiles(supabase, panelId) {
    const transcripts = await PanelTranscriptModel.fetchExistingFromSupabase(
        supabase,
        { panelId }
    );
    const audios = await PanelAudioModel.fetchExistingFromSupabase(supabase, {
        panelId
    });

    const transcriptUrls = {};
    const audioUrls = {};

    for (const transcript of transcripts) {
        transcriptUrls[transcript.id] = supabase.storage
            .from(transcript.bucketId)
            .getPublicUrl(transcript.file).publicURL;
    }

    for (const audio of audios) {
        audioUrls[audio.id] = supabase.storage
            .from(audio.bucketId)
            .getPublicUrl(audio.file).publicURL;
    }

    return { transcriptUrls, audioUrls };
}

/**
 * Fetch a single transcript by its ID.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @param {string} transcriptId - The ID of the transcript to fetch.
 * @returns {Promise<PanelTranscriptModel>} - The fetched transcript.
 */
export async function getPanelTranscript(supabase, transcriptId) {
    const transcript = await PanelTranscriptModel.fetchFromSupabase(supabase, {
        id: transcriptId
    });
    if (!transcript) {
        throw new Error("Transcript not found");
    }
    return transcript;
}

/**
 * Fetch all transcripts.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @returns {Promise<PanelTranscriptModel[]>} - The list of transcripts.
 */
export async function listPanelTranscripts(supabase) {
    return await PanelTranscriptModel.fetchExistingFromSupabase(supabase);
}

/**
 * Fetch all transcripts associated with a specific panel ID.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @param {string} panelId - The ID of the panel.
 * @returns {Promise<PanelTranscriptModel[]>} - The list of transcripts for the panel.
 */
export async function listPanelTranscriptsByPanelId(supabase, panelId) {
    return await PanelTranscriptModel.fetchExistingFromSupabase(supabase, {
        panelId
    });
}

/**
 * Fetch a single audio by its ID.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @param {string} audioId - The ID of the audio to fetch.
 * @returns {Promise<PanelAudioModel>} - The fetched audio.
 */
export async function getPanelAudio(supabase, audioId) {
    const audio = await PanelAudioModel.fetchFromSupabase(supabase, {
        id: audioId
    });
    if (!audio) {
        throw new Error("Audio not found");
    }
    return audio;
}

/**
 * Fetch all audios.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @returns {Promise<PanelAudioModel[]>} - The list of audios.
 */
export async function listPanelAudios(supabase) {
    return await PanelAudioModel.fetchExistingFromSupabase(supabase);
}

/**
 * Fetch all audios associated with a specific panel ID.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @param {string} panelId - The ID of the panel.
 * @returns {Promise<PanelAudioModel[]>} - The list of audios for the panel.
 */
export async function listPanelAudiosByPanelId(supabase, panelId) {
    return await PanelAudioModel.fetchExistingFromSupabase(supabase, {
        panelId
    });
}

/**
 * Fetch all sources associated with a specific transcript ID.
 * @param {SupabaseClient} supabase - The Supabase client instance.
 * @param {string} transcriptId - The ID of the transcript.
 * @returns {Promise<PanelTranscriptSourceReferenceModel[]>} - The list of sources for the transcript.
 */
export async function getPanelTranscriptSources(supabase, transcriptId) {
    return await PanelTranscriptSourceReferenceModel.fetchExistingFromSupabase(
        supabase,
        { transcriptId }
    );
}
