import { SupabaseModel } from "./supabaseModel";

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

export declare class SourceModel extends SupabaseModel<SourceModel> {
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

export declare class SourceChunkModel extends SupabaseModel<SourceChunkModel> {
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

export declare class SourceRelationshipModel extends SupabaseModel<SourceRelationshipModel> {
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
