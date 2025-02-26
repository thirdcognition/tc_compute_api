import {
    PanelDiscussionModel,
    PanelTranscriptModel,
    PanelAudioModel
} from "../models/supabase/panel.js";

/**
 * Represents the detailed information about a panel, including its transcripts and audios.
 */
export interface PanelDetails {
    panel: PanelDiscussionModel;
    transcripts: PanelTranscriptModel[];
    audios: PanelAudioModel[];
}

/**
 * Represents the public URLs for transcripts and audios associated with a panel.
 */
export interface PanelFiles {
    transcriptUrls: Record<string, string>;
    audioUrls: Record<string, string>;
}
