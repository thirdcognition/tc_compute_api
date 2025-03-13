import {
    PanelDiscussionModel,
    PanelTranscriptModel,
    PanelAudioModel,
    PanelTranscriptSourceReferenceModel
} from "../models/supabase/panel";
import { SupabaseClient } from "@supabase/supabase-js";

/**
 * Represents the detailed information about a panel, including its transcripts and audios.
 */
export declare class PanelDetails {
    panel: PanelDiscussionModel;
    transcripts: PanelTranscriptModel[];
    audios: PanelAudioModel[];
}

/**
 * Represents the public URLs for transcripts and audios associated with a panel.
 */
export declare class PanelFiles {
    transcriptUrls: Record<string, string>;
    audioUrls: Record<string, string>;
}

/**
 * Interface for the PanelAPI object.
 */
declare const PanelAPI: {
    getPanel(
        supabase: SupabaseClient,
        panelId: string
    ): Promise<PanelDiscussionModel>;

    listPanels(supabase: SupabaseClient): Promise<PanelDiscussionModel[]>;

    // getPanelDetails(
    //     supabase: SupabaseClient,
    //     panelId: string
    // ): Promise<PanelDetails>;

    // getPanelFiles(
    //     supabase: SupabaseClient,
    //     panelId: string
    // ): Promise<PanelFiles>;

    getPanelTranscript(
        supabase: SupabaseClient,
        transcriptId: string
    ): Promise<PanelTranscriptModel>;

    // listPanelTranscripts(
    //     supabase: SupabaseClient
    // ): Promise<PanelTranscriptModel[]>;

    listPanelTranscriptsByPanelId(
        supabase: SupabaseClient,
        panelId: string
    ): Promise<PanelTranscriptModel[]>;

    getPanelAudio(
        supabase: SupabaseClient,
        audioId: string
    ): Promise<PanelAudioModel>;

    // listPanelAudios(supabase: SupabaseClient): Promise<PanelAudioModel[]>;

    // listPanelAudiosByPanelId(
    //     supabase: SupabaseClient,
    //     panelId: string
    // ): Promise<PanelAudioModel[]>;

    listPanelAudiosByTranscriptId(
        supabase: SupabaseClient,
        transcriptId: string
    ): Promise<PanelAudioModel[]>;

    getPanelTranscriptSources(
        supabase: SupabaseClient,
        transcriptId: string
    ): Promise<PanelTranscriptSourceReferenceModel[]>;
};

export default PanelAPI;
