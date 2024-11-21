import { SupabaseModel, Enum } from "./supabaseModel.js";

// Define SourceTypeEnum
class SourceTypeEnum extends Enum {
    constructor() {
        super();
        this.DOCUMENT = "document";
        this.WEBPAGE = "webpage";
        this.WEBSITE = "website";
        this.VIDEO = "video";
        this.AUDIO = "audio";
        this.IMAGE = "image";
        this.TOPIC = "topic";
        this.CONCEPT = "concept";
        Object.freeze(this);
    }
}

export const SourceType = new SourceTypeEnum();

// Define SourceModel
export class SourceModel extends SupabaseModel {
    static TABLE_NAME = "source";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: true, dbColumn: "id" },
        type: { type: SourceType, required: false, dbColumn: "type" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        currentVersionId: {
            type: "uuid",
            required: false,
            dbColumn: "current_version_id"
        },
        updatedBy: { type: "uuid", required: false, dbColumn: "updated_by" }
    };
}

// Define SourceChunkModel
export class SourceChunkModel extends SupabaseModel {
    static TABLE_NAME = "source_chunk";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: true, dbColumn: "id" },
        sourceId: { type: "uuid", required: false, dbColumn: "source_id" },
        sourceVersionId: {
            type: "uuid",
            required: false,
            dbColumn: "source_version_id"
        },
        chunkNextId: {
            type: "uuid",
            required: false,
            dbColumn: "chunk_next_id"
        },
        chunkPrevId: {
            type: "uuid",
            required: false,
            dbColumn: "chunk_prev_id"
        },
        data: { type: "json", required: false, dbColumn: "data" },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}

// Define SourceRelationshipModel
export class SourceRelationshipModel extends SupabaseModel {
    static TABLE_NAME = "source_relationship";
    static TABLE_FIELDS = {
        sourceVersionId: {
            type: "uuid",
            required: true,
            dbColumn: "source_version_id"
        },
        relatedSourceVersionId: {
            type: "uuid",
            required: true,
            dbColumn: "related_source_version_id"
        },
        relationshipType: {
            type: "string",
            required: false,
            dbColumn: "relationship_type"
        },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };

    static async saveToSupabase(supabase, instance, onConflict = null) {
        return super.saveToSupabase(supabase, instance, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = null,
        idColumn = "sourceVersionId"
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idColumn
        );
    }

    static async fetchFromSupabase(
        supabase,
        value = null,
        idColumn = "sourceVersionId"
    ) {
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(
        supabase,
        value = null,
        idColumn = "sourceVersionId"
    ) {
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idColumn = "sourceVersionId"
    ) {
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

// Define SourceVersionModel
export class SourceVersionModel extends SupabaseModel {
    static TABLE_NAME = "source_version";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: true, dbColumn: "id" },
        title: { type: "string", required: false, dbColumn: "title" },
        lang: { type: "string", required: false, dbColumn: "lang" },
        contentHash: {
            type: "string",
            required: false,
            dbColumn: "content_hash"
        },
        data: { type: "json", required: false, dbColumn: "data" },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        versionOfId: {
            type: "uuid",
            required: false,
            dbColumn: "version_of_id"
        }
    };
}
