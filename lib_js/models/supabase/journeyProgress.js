import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

// Define JourneyProgressModel
export class JourneyProgressModel extends SupabaseModel {
    static TABLE_NAME = "journey_progress";

    constructor(args) {
        super();
        const {
            id = null,
            journeyId,
            journeyVersionId,
            assignedAt = null,
            metadata = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId = null,
            startedAt = null,
            completedAt = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            journeyId: {
                value: journeyId,
                type: "uuid",
                required: true,
                dbColumn: "journey_id"
            },
            journeyVersionId: {
                value: journeyVersionId,
                type: "uuid",
                required: true,
                dbColumn: "journey_version_id"
            },
            assignedAt: {
                value: assignedAt,
                type: "date",
                required: false,
                dbColumn: "assigned_at"
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
            startedAt: {
                value: startedAt,
                type: "date",
                required: false,
                dbColumn: "started_at"
            },
            completedAt: {
                value: completedAt,
                type: "date",
                required: false,
                dbColumn: "completed_at"
            }
        };
    }
}

// Define JourneyProgressLLMConversationMessagesModel
export class JourneyProgressLLMConversationMessagesModel extends SupabaseModel {
    static TABLE_NAME = "journey_progress_llm_conversation_messages";

    constructor(args) {
        super();
        const {
            journeyItemProgressId,
            messageId,
            conversationId,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId = null
        } = args;
        this.attributes = {
            journeyItemProgressId: {
                value: journeyItemProgressId,
                type: "uuid",
                required: true,
                dbColumn: "journey_item_progress_id"
            },
            messageId: {
                value: messageId,
                type: "uuid",
                required: true,
                dbColumn: "message_id"
            },
            conversationId: {
                value: conversationId,
                type: "uuid",
                required: true,
                dbColumn: "conversation_id"
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

    static async saveToSupabase(
        supabase,
        instance,
        onConflict = ["journeyItemProgressId", "messageId"]
    ) {
        return super.saveToSupabase(supabase, instance, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["journeyItemProgressId", "messageId"],
        idColumn = null
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idColumn
        );
    }

    static async fetchFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                journeyItemProgressId:
                    value.attributes.journeyItemProgressId.value,
                messageId: value.attributes.messageId.value
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                journeyItemProgressId:
                    value.attributes.journeyItemProgressId.value,
                messageId: value.attributes.messageId.value
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                journeyItemProgressId:
                    value.attributes.journeyItemProgressId.value,
                messageId: value.attributes.messageId.value
            };
        }
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

// Define JourneyProgressLLMConversationsModel
export class JourneyProgressLLMConversationsModel extends SupabaseModel {
    static TABLE_NAME = "journey_progress_llm_conversations";

    constructor(args) {
        super();
        const {
            progressId,
            conversationId,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId = null
        } = args;
        this.attributes = {
            progressId: {
                value: progressId,
                type: "uuid",
                required: true,
                dbColumn: "progress_id"
            },
            conversationId: {
                value: conversationId,
                type: "uuid",
                required: true,
                dbColumn: "conversation_id"
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

    static async saveToSupabase(
        supabase,
        instance,
        onConflict = ["progressId", "conversationId"]
    ) {
        return super.saveToSupabase(supabase, instance, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instance,
        onConflict = ["progressId", "conversationId"],
        idColumn = null
    ) {
        return super.upsertToSupabase(supabase, instance, onConflict, idColumn);
    }

    static async fetchFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                progressId: value.attributes.progressId.value,
                conversationId: value.attributes.conversationId.value
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                progressId: value.attributes.progressId.value,
                conversationId: value.attributes.conversationId.value
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                progressId: value.attributes.progressId.value,
                conversationId: value.attributes.conversationId.value
            };
        }
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

// Define JourneyItemProgressModel
export class JourneyItemProgressModel extends SupabaseModel {
    static TABLE_NAME = "journey_item_progress";

    constructor(args) {
        super();
        const {
            id = null,
            journeyProgressId,
            journeyItemId,
            journeyItemVersionId,
            data = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId = null,
            startedAt = null,
            completedAt = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            journeyProgressId: {
                value: journeyProgressId,
                type: "uuid",
                required: true,
                dbColumn: "journey_progress_id"
            },
            journeyItemId: {
                value: journeyItemId,
                type: "uuid",
                required: true,
                dbColumn: "journey_item_id"
            },
            journeyItemVersionId: {
                value: journeyItemVersionId,
                type: "uuid",
                required: true,
                dbColumn: "journey_item_version_id"
            },
            data: {
                value: data,
                type: "json",
                required: false,
                dbColumn: "data"
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
            startedAt: {
                value: startedAt,
                type: "date",
                required: false,
                dbColumn: "started_at"
            },
            completedAt: {
                value: completedAt,
                type: "date",
                required: false,
                dbColumn: "completed_at"
            }
        };
    }
}
