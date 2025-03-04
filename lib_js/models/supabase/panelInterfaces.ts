import { SupabaseModel } from "./SupabaseModelInterface";

export interface PanelAudioModel extends SupabaseModel<PanelAudioModel> {
    id?: string;
    panelId: string;
    transcriptId: string;
    title?: string;
    tags?: string[];
    file?: string;
    bucketId?: string;
    processState?: "none" | "waiting" | "processing" | "failed" | "done"; // Updated to string literal type
    processStateMessage?: string;
    metadata?: object;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    lang?: string;
}

export interface PanelDiscussionModel
    extends SupabaseModel<PanelDiscussionModel> {
    id?: string;
    title?: string;
    tags?: string[];
    metadata?: object;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    lang?: string;
}

export interface PanelTranscriptModel
    extends SupabaseModel<PanelTranscriptModel> {
    id?: string;
    panelId: string;
    title?: string;
    tags?: string[];
    file?: string;
    bucketId?: string;
    type?: string;
    transcript?: object;
    processState?: string; // Enum: ProcessState
    processStateMessage?: string;
    generationCronjob?: string;
    generationParent?: string;
    metadata?: object;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface PanelTranscriptOrderModel
    extends SupabaseModel<PanelTranscriptOrderModel> {
    id?: string;
    panelId: string;
    transcriptId?: string;
    beforeId?: string;
    afterId?: string;
    data?: object;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface PanelTranscriptSourceReferenceModel
    extends SupabaseModel<PanelTranscriptSourceReferenceModel> {
    id?: string;
    transcriptId: string;
    sourceId: string;
    type?: string;
    data?: object;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}
