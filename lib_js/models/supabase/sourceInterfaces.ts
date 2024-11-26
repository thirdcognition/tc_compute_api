import { SupabaseModel } from "./SupabaseModelInterface";

export interface Source extends SupabaseModel<Source> {
    id: string;
    type?: string; // Assuming SourceType is a string enum
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    currentVersionId?: string;
    updatedBy?: string;
}

export interface SourceChunk extends SupabaseModel<SourceChunk> {
    id: string;
    sourceId?: string;
    sourceVersionId?: string;
    chunkNextId?: string;
    chunkPrevId?: string;
    data?: object;
    metadata?: object;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

export interface SourceRelationship extends SupabaseModel<SourceRelationship> {
    sourceVersionId: string;
    relatedSourceVersionId: string;
    relationshipType?: string;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface SourceVersion extends SupabaseModel<SourceVersion> {
    id: string;
    title?: string;
    lang?: string;
    contentHash?: string;
    data?: object;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    versionOfId?: string;
}
