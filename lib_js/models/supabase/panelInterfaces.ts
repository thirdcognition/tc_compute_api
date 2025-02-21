import { SupabaseModel } from "./SupabaseModelInterface";

export interface PanelAudio extends SupabaseModel<PanelAudio> {
    id?: string;
    panelId: string;
    transcriptId: string;
    title?: string;
    tags?: string[];
    file?: string;
    bucketId?: string;
    processState?: string; // Enum: ProcessState
    processFailMessage?: string;
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

export interface PanelDiscussion extends SupabaseModel<PanelDiscussion> {
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

export interface PanelTranscript extends SupabaseModel<PanelTranscript> {
    id?: string;
    panelId: string;
    title?: string;
    tags?: string[];
    file?: string;
    bucketId?: string;
    type?: string;
    transcript?: object;
    processState?: string; // Enum: ProcessState
    processFailMessage?: string;
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

export interface PanelTranscriptOrder
    extends SupabaseModel<PanelTranscriptOrder> {
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

export interface PanelTranscriptSourceReference
    extends SupabaseModel<PanelTranscriptSourceReference> {
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
