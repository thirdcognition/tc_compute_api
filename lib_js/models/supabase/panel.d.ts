import { SupabaseClient } from "@supabase/supabase-js";
import {
    AudioMetadata,
    PanelMetadata,
    TranscriptMetadata
} from "../structures/panel";
import { SupabaseModel } from "./supabaseModel";

export enum ProcessStateEnum {
    NONE = "none",
    WAITING = "waiting",
    PROCESSING = "processing",
    FAILED = "failed",
    DONE = "done"
}

export declare class PanelAudioModel extends SupabaseModel<PanelAudioModel> {
    id?: string;
    panelId: string;
    transcriptId: string;
    title?: string;
    tags?: string[];
    file?: string;
    bucketId?: string;
    processState?: ProcessStateEnum;
    processStateMessage?: string;
    metadata?: AudioMetadata;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    lang?: string;

    getContentUrl(supabase: SupabaseClient): string;
}

export declare class PanelDiscussionModel extends SupabaseModel<PanelDiscussionModel> {
    id?: string;
    title?: string;
    tags?: string[];
    metadata?: PanelMetadata;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export declare class PanelTranscriptModel extends SupabaseModel<PanelTranscriptModel> {
    id?: string;
    panelId: string;
    title?: string;
    tags?: string[];
    file?: string;
    bucketId?: string;
    type?: string;
    transcript?: Record<string, unknown>;
    processState?: ProcessStateEnum;
    processStateMessage?: string;
    generationCronjob?: string;
    generationParent?: string;
    metadata?: TranscriptMetadata;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    lang?: string;

    getContentUrl(supabase: SupabaseClient): string;
    async fetchContent(supabase: SupabaseClient): string;
}

export declare class PanelTranscriptOrderModel extends SupabaseModel<PanelTranscriptOrderModel> {
    id?: string;
    panelId: string;
    transcriptId?: string;
    beforeId?: string;
    afterId?: string;
    data?: Record<string, unknown>;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export declare class PanelTranscriptSourceReferenceModel extends SupabaseModel<PanelTranscriptSourceReferenceModel> {
    id?: string;
    transcriptId: string;
    sourceId: string;
    type?: string;
    data?: Record<string, unknown>;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}
