import { SupabaseModel } from "./supabaseModel.js";

// Define LlmConversationModel
export class LlmConversationModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        startTime: { type: "date", required: false, dbColumn: "start_time" },
        endTime: { type: "date", required: false, dbColumn: "end_time" },
        title: { type: "string", required: false, dbColumn: "title" },
        tags: { type: "array", required: false, dbColumn: "tags" },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        state: { type: "string", required: false, dbColumn: "state" }
    };
}

// Define LlmConversationMessageModel
export class LlmConversationMessageModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation_message";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        type: { type: "string", required: false, dbColumn: "type" },
        conversationId: {
            type: "uuid",
            required: true,
            dbColumn: "conversation_id"
        },
        content: { type: "string", required: false, dbColumn: "content" },
        model: { type: "string", required: false, dbColumn: "model" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}

// Define LlmConversationMessageHistoryModel
export class LlmConversationMessageHistoryModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation_message_history";
    static TABLE_FIELDS = {
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        conversationId: {
            type: "uuid",
            required: true,
            dbColumn: "conversation_id"
        },
        sessionId: { type: "uuid", required: false, dbColumn: "session_id" },
        queryId: { type: "uuid", required: false, dbColumn: "query_id" },
        messageId: { type: "uuid", required: true, dbColumn: "message_id" },
        responseId: { type: "uuid", required: false, dbColumn: "response_id" },
        previousMessageId: {
            type: "uuid",
            required: false,
            dbColumn: "previous_message_id"
        },
        nextMessageId: {
            type: "uuid",
            required: false,
            dbColumn: "next_message_id"
        },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" }
    };

    static async saveToSupabase(
        supabase,
        value,
        onConflict = ["conversationId", "messageId"]
    ) {
        return super.saveToSupabase(supabase, value, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["conversationId", "messageId"],
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
                conversationId: value.attributes.conversationId,
                messageId: value.attributes.messageId
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                conversationId: value.attributes.conversationId,
                messageId: value.attributes.messageId
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }
}

// Define LlmConversationThreadModel
export class LlmConversationThreadModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation_thread";
    static TABLE_FIELDS = {
        conversationId: {
            type: "uuid",
            required: true,
            dbColumn: "conversation_id"
        },
        parentMessageId: {
            type: "uuid",
            required: true,
            dbColumn: "parent_message_id"
        },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };

    static async saveToSupabase(
        supabase,
        value,
        onConflict = ["conversationId", "parentMessageId"]
    ) {
        return super.saveToSupabase(supabase, value, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["conversationId", "parentMessageId"],
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
                conversationId: value.attributes.conversationId,
                parentMessageId: value.attributes.parentMessageId
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                conversationId: value.attributes.conversationId,
                parentMessageId: value.attributes.parentMessageId
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }
}
