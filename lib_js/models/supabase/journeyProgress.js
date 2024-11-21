import { SupabaseModel } from "./supabaseModel.js";

// Define JourneyProgressModel
export class JourneyProgressModel extends SupabaseModel {
    static TABLE_NAME = "journey_progress";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        journeyId: { type: "uuid", required: true, dbColumn: "journey_id" },
        journeyVersionId: {
            type: "uuid",
            required: true,
            dbColumn: "journey_version_id"
        },
        assignedAt: { type: "date", required: false, dbColumn: "assigned_at" },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        startedAt: { type: "date", required: false, dbColumn: "started_at" },
        completedAt: { type: "date", required: false, dbColumn: "completed_at" }
    };
}

// Define JourneyProgressLLMConversationMessagesModel
export class JourneyProgressLLMConversationMessagesModel extends SupabaseModel {
    static TABLE_NAME = "journey_progress_llm_conversation_messages";
    static TABLE_FIELDS = {
        journeyItemProgressId: {
            type: "uuid",
            required: true,
            dbColumn: "journey_item_progress_id"
        },
        messageId: { type: "uuid", required: true, dbColumn: "message_id" },
        conversationId: {
            type: "uuid",
            required: true,
            dbColumn: "conversation_id"
        },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };

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
                journeyItemProgressId: value.attributes.journeyItemProgressId,
                messageId: value.attributes.messageId
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                journeyItemProgressId: value.attributes.journeyItemProgressId,
                messageId: value.attributes.messageId
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                journeyItemProgressId: value.attributes.journeyItemProgressId,
                messageId: value.attributes.messageId
            };
        }
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

// Define JourneyProgressLLMConversationsModel
export class JourneyProgressLLMConversationsModel extends SupabaseModel {
    static TABLE_NAME = "journey_progress_llm_conversations";
    static TABLE_FIELDS = {
        progressId: { type: "uuid", required: true, dbColumn: "progress_id" },
        conversationId: {
            type: "uuid",
            required: true,
            dbColumn: "conversation_id"
        },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };

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
                progressId: value.attributes.progressId,
                conversationId: value.attributes.conversationId
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                progressId: value.attributes.progressId,
                conversationId: value.attributes.conversationId
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                progressId: value.attributes.progressId,
                conversationId: value.attributes.conversationId
            };
        }
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

// Define JourneyItemProgressModel
export class JourneyItemProgressModel extends SupabaseModel {
    static TABLE_NAME = "journey_item_progress";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        journeyProgressId: {
            type: "uuid",
            required: true,
            dbColumn: "journey_progress_id"
        },
        journeyItemId: {
            type: "uuid",
            required: true,
            dbColumn: "journey_item_id"
        },
        journeyItemVersionId: {
            type: "uuid",
            required: true,
            dbColumn: "journey_item_version_id"
        },
        data: { type: "json", required: false, dbColumn: "data" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        startedAt: { type: "date", required: false, dbColumn: "started_at" },
        completedAt: { type: "date", required: false, dbColumn: "completed_at" }
    };
}
