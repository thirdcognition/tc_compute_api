import { SupabaseModel } from "./SupabaseModelInterface";

export enum SourceTypeEnum {
    DOCUMENT = "document",
    WEBPAGE = "webpage",
    WEBSITE = "website",
    VIDEO = "video",
    AUDIO = "audio",
    IMAGE = "image",
    TOPIC = "topic",
    CONCEPT = "concept",
    COLLECTION = "collection"
}

export interface SourceModel extends SupabaseModel<SourceModel> {
    id: string;
    originalSource?: string;
    resolvedSource?: string;
    type?: SourceTypeEnum;
    title?: string;
    lang?: string;
    contentHash?: string;
    data?: Record<string, unknown>;
    metadata?: Record<string, unknown>;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    updatedBy?: string;
}

export interface SourceChunkModel extends SupabaseModel<SourceChunkModel> {
    id: string;
    sourceId?: string;
    chunkNextId?: string;
    chunkPrevId?: string;
    data?: Record<string, unknown>;
    metadata?: Record<string, unknown>;
    isPublic?: boolean;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

export interface SourceRelationshipModel
    extends SupabaseModel<SourceRelationshipModel> {
    sourceId: string;
    relatedSourceId: string;
    relationshipType?: string;
    metadata?: Record<string, unknown>;
    isPublic?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}
