import {
    PanelDiscussionModel,
    PanelTranscriptModel,
    PanelAudioModel,
    PanelTranscriptSourceReferenceModel
} from "../models/supabase/panel.js";
import { SupabaseClient } from "@supabase/supabase-js";

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

/**
 * Function type definitions for panel.js
 */
export type GetPanelFunction = (
    supabase: SupabaseClient,
    panelId: string
) => Promise<PanelDiscussionModel>;

export type ListPanelsFunction = (
    supabase: SupabaseClient
) => Promise<PanelDiscussionModel[]>;

export type GetPanelDetailsFunction = (
    supabase: SupabaseClient,
    panelId: string
) => Promise<PanelDetails>;

export type GetPanelFilesFunction = (
    supabase: SupabaseClient,
    panelId: string
) => Promise<PanelFiles>;

export type GetPanelTranscriptFunction = (
    supabase: SupabaseClient,
    transcriptId: string
) => Promise<PanelTranscriptModel>;

export type ListPanelTranscriptsFunction = (
    supabase: SupabaseClient
) => Promise<PanelTranscriptModel[]>;

export type ListPanelTranscriptsByPanelIdFunction = (
    supabase: SupabaseClient,
    panelId: string
) => Promise<PanelTranscriptModel[]>;

export type GetPanelAudioFunction = (
    supabase: SupabaseClient,
    audioId: string
) => Promise<PanelAudioModel>;

export type ListPanelAudiosFunction = (
    supabase: SupabaseClient
) => Promise<PanelAudioModel[]>;

export type ListPanelAudiosByPanelIdFunction = (
    supabase: SupabaseClient,
    panelId: string
) => Promise<PanelAudioModel[]>;

export type GetPanelTranscriptSourcesFunction = (
    supabase: SupabaseClient,
    transcriptId: string
) => Promise<PanelTranscriptSourceReferenceModel[]>;
