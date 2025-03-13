import {
    PanelDiscussionModel,
    PanelTranscriptModel,
    PanelAudioModel,
    PanelTranscriptSourceReferenceModel
} from "../models/supabase/panel.js";

const PanelAPI = {
    async getPanel(supabase, panelId) {
        const panel = await PanelDiscussionModel.fetchFromSupabase(supabase, {
            id: panelId
        });
        if (!panel) {
            throw new Error("Panel not found");
        }
        return panel;
    },

    async listPanels(supabase) {
        return await PanelDiscussionModel.fetchExistingFromSupabase(supabase);
    },

    // async getPanelDetails(supabase, panelId) {
    //     const panel = await this.getPanel(supabase, panelId);
    //     const transcripts =
    //         await PanelTranscriptModel.fetchExistingFromSupabase(supabase, {
    //             panelId
    //         });
    //     const audios = await PanelAudioModel.fetchExistingFromSupabase(
    //         supabase,
    //         {
    //             panelId
    //         }
    //     );

    //     return {
    //         panel,
    //         transcripts,
    //         audios
    //     };
    // },

    // async getPanelFiles(supabase, panelId) {
    //     const transcripts =
    //         await PanelTranscriptModel.fetchExistingFromSupabase(supabase, {
    //             panelId
    //         });
    //     const audios = await PanelAudioModel.fetchExistingFromSupabase(
    //         supabase,
    //         {
    //             panelId
    //         }
    //     );

    //     const transcriptUrls = {};
    //     const audioUrls = {};

    //     for (const transcript of transcripts) {
    //         transcriptUrls[transcript.id] = supabase.storage
    //             .from(transcript.bucketId)
    //             .getPublicUrl(transcript.file).publicURL;
    //     }

    //     for (const audio of audios) {
    //         audioUrls[audio.id] = supabase.storage
    //             .from(audio.bucketId)
    //             .getPublicUrl(audio.file).publicURL;
    //     }

    //     return { transcriptUrls, audioUrls };
    // },

    async getPanelTranscript(supabase, transcriptId) {
        const transcript = await PanelTranscriptModel.fetchFromSupabase(
            supabase,
            {
                id: transcriptId
            }
        );
        if (!transcript) {
            throw new Error("Transcript not found");
        }
        return transcript;
    },

    // async listPanelTranscripts(supabase) {
    //     return await PanelTranscriptModel.fetchExistingFromSupabase(supabase);
    // },

    async listPanelTranscriptsByPanelId(supabase, panelId) {
        return await PanelTranscriptModel.fetchExistingFromSupabase(supabase, {
            panelId
        });
    },

    async getPanelAudio(supabase, audioId) {
        const audio = await PanelAudioModel.fetchFromSupabase(supabase, {
            id: audioId
        });
        if (!audio) {
            throw new Error("Audio not found");
        }
        return audio;
    },

    // async listPanelAudios(supabase) {
    //     return await PanelAudioModel.fetchExistingFromSupabase(supabase);
    // },

    // async listPanelAudiosByPanelId(supabase, panelId) {
    //     return await PanelAudioModel.fetchExistingFromSupabase(supabase, {
    //         panelId
    //     });
    // },

    async listPanelAudiosByTranscriptId(supabase, transcriptId) {
        return await PanelAudioModel.fetchExistingFromSupabase(supabase, {
            transcriptId
        });
    },

    async getPanelTranscriptSources(supabase, transcriptId) {
        return await PanelTranscriptSourceReferenceModel.fetchExistingFromSupabase(
            supabase,
            { transcriptId }
        );
    }
};

export default PanelAPI;
