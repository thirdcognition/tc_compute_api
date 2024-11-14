import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export const SourceTypeEnum = Object.freeze({
    DOCUMENT: "document",
    WEBPAGE: "webpage",
    WEBSITE: "website",
    VIDEO: "video",
    AUDIO: "audio",
    IMAGE: "image",
    TOPIC: "topic",
    CONCEPT: "concept"
});

export class SourceModel extends SupabaseModel {
    static TABLE_NAME = "source";

    constructor({
        id,
        type = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId,
        currentVersionId = null,
        updatedBy = null
    }) {
        super();
        this.id = id || uuidv4();
        this.type = type;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.currentVersionId = currentVersionId;
        this.updatedBy = updatedBy;
    }
}

export class SourceChunkModel extends SupabaseModel {
    static TABLE_NAME = "source_chunk";

    constructor({
        id,
        sourceId = null,
        sourceVersionId = null,
        chunkNextId = null,
        chunkPrevId = null,
        data = null,
        metadata = null,
        createdAt = null,
        updatedAt = null,
        organizationId
    }) {
        super();
        this.id = id || uuidv4();
        this.sourceId = sourceId;
        this.sourceVersionId = sourceVersionId;
        this.chunkNextId = chunkNextId;
        this.chunkPrevId = chunkPrevId;
        this.data = data;
        this.metadata = metadata;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.organizationId = organizationId;
    }
}

export class SourceRelationshipModel extends SupabaseModel {
    static TABLE_NAME = "source_relationship";

    constructor({
        sourceVersionId,
        relatedSourceVersionId,
        relationshipType = null,
        metadata = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId
    }) {
        super();
        this.sourceVersionId = sourceVersionId;
        this.relatedSourceVersionId = relatedSourceVersionId;
        this.relationshipType = relationshipType;
        this.metadata = metadata;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
    }

    static async saveToSupabase(supabase, instance, onConflict = null) {
        return super.saveToSupabase(supabase, instance, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = null,
        idFieldName = "sourceVersionId"
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idFieldName
        );
    }

    static async fetchFromSupabase(
        supabase,
        value = null,
        idFieldName = "sourceVersionId"
    ) {
        return super.fetchFromSupabase(supabase, value, idFieldName);
    }

    static async existsInSupabase(
        supabase,
        value = null,
        idFieldName = "sourceVersionId"
    ) {
        return super.existsInSupabase(supabase, value, idFieldName);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idFieldName = "sourceVersionId"
    ) {
        return super.deleteFromSupabase(supabase, value, idFieldName);
    }
}

export class SourceVersionModel extends SupabaseModel {
    static TABLE_NAME = "source_version";

    constructor({
        id,
        title = null,
        lang = null,
        contentHash = null,
        data = null,
        metadata = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId,
        versionOfId = null
    }) {
        super();
        this.id = id || uuidv4();
        this.title = title;
        this.lang = lang;
        this.contentHash = contentHash;
        this.data = data;
        this.metadata = metadata;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.versionOfId = versionOfId;
    }
}
