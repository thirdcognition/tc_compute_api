import { SupabaseModel } from "./SupabaseModelInterface";

export interface Source extends SupabaseModel<Source> {
    id: string;
    originalSource?: string;
    resolvedSource?: string;
    type?: string; // Assuming SourceType is a string enum
    title?: string;
    lang?: string;
    contentHash?: string;
    data?: object;
    metadata?: object;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    updatedBy?: string;
}

export interface SourceChunk extends SupabaseModel<SourceChunk> {
    id: string;
    sourceId?: string;
    chunkNextId?: string;
    chunkPrevId?: string;
    data?: object;
    metadata?: object;
    isPublic?: boolean;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

export interface SourceRelationship extends SupabaseModel<SourceRelationship> {
    sourceId: string;
    relatedSourceId: string;
    relationshipType?: string;
    metadata?: object;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}
