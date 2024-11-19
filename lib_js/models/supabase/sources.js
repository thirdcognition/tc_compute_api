import { SupabaseModel, Enum } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

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

export class SourceModel extends SupabaseModel {
    static TABLE_NAME = "source";

    constructor(args) {
        super();
        const {
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
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: true,
                dbColumn: "id"
            },
            type: {
                value: type,
                type: SourceType,
                required: false,
                dbColumn: "type"
            },
            disabled: {
                value: disabled,
                type: "boolean",
                required: false,
                dbColumn: "disabled"
            },
            disabledAt: {
                value: disabledAt,
                type: "date",
                required: false,
                dbColumn: "disabled_at"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            },
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: false,
                dbColumn: "organization_id"
            },
            currentVersionId: {
                value: currentVersionId,
                type: "uuid",
                required: false,
                dbColumn: "current_version_id"
            },
            updatedBy: {
                value: updatedBy,
                type: "uuid",
                required: false,
                dbColumn: "updated_by"
            }
        };
    }
}

export class SourceChunkModel extends SupabaseModel {
    static TABLE_NAME = "source_chunk";

    constructor(args) {
        super();
        const {
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
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: true,
                dbColumn: "id"
            },
            sourceId: {
                value: sourceId,
                type: "uuid",
                required: false,
                dbColumn: "source_id"
            },
            sourceVersionId: {
                value: sourceVersionId,
                type: "uuid",
                required: false,
                dbColumn: "source_version_id"
            },
            chunkNextId: {
                value: chunkNextId,
                type: "uuid",
                required: false,
                dbColumn: "chunk_next_id"
            },
            chunkPrevId: {
                value: chunkPrevId,
                type: "uuid",
                required: false,
                dbColumn: "chunk_prev_id"
            },
            data: {
                value: data,
                type: "json",
                required: false,
                dbColumn: "data"
            },
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: false,
                dbColumn: "organization_id"
            }
        };
    }
}

export class SourceRelationshipModel extends SupabaseModel {
    static TABLE_NAME = "source_relationship";

    constructor(args) {
        super();
        const {
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
        } = args;
        this.attributes = {
            sourceVersionId: {
                value: sourceVersionId,
                type: "uuid",
                required: true,
                dbColumn: "source_version_id"
            },
            relatedSourceVersionId: {
                value: relatedSourceVersionId,
                type: "uuid",
                required: true,
                dbColumn: "related_source_version_id"
            },
            relationshipType: {
                value: relationshipType,
                type: "string",
                required: false,
                dbColumn: "relationship_type"
            },
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
            },
            disabled: {
                value: disabled,
                type: "boolean",
                required: false,
                dbColumn: "disabled"
            },
            disabledAt: {
                value: disabledAt,
                type: "date",
                required: false,
                dbColumn: "disabled_at"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            },
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: false,
                dbColumn: "organization_id"
            }
        };
    }

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

export class SourceVersionModel extends SupabaseModel {
    static TABLE_NAME = "source_version";

    constructor(args) {
        super();
        const {
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
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: true,
                dbColumn: "id"
            },
            title: {
                value: title,
                type: "string",
                required: false,
                dbColumn: "title"
            },
            lang: {
                value: lang,
                type: "string",
                required: false,
                dbColumn: "lang"
            },
            contentHash: {
                value: contentHash,
                type: "string",
                required: false,
                dbColumn: "content_hash"
            },
            data: {
                value: data,
                type: "json",
                required: false,
                dbColumn: "data"
            },
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
            },
            disabled: {
                value: disabled,
                type: "boolean",
                required: false,
                dbColumn: "disabled"
            },
            disabledAt: {
                value: disabledAt,
                type: "date",
                required: false,
                dbColumn: "disabled_at"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            },
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: false,
                dbColumn: "organization_id"
            },
            versionOfId: {
                value: versionOfId,
                type: "uuid",
                required: false,
                dbColumn: "version_of_id"
            }
        };
    }
}
