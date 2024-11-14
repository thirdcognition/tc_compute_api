import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export class LlmConversationModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation";

    constructor({
        id = null,
        startTime = null,
        endTime = null,
        title = null,
        tags = null,
        metadata = null,
        createdAt = null,
        ownerId = null,
        organizationId,
        state = null
    }) {
        super();
        this.id = id || uuidv4();
        this.startTime = startTime;
        this.endTime = endTime;
        this.title = title;
        this.tags = tags;
        this.metadata = metadata;
        this.createdAt = createdAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.state = state;
    }

    static validateMetadata(v) {
        if (typeof v === "string") {
            return JSON.parse(v);
        } else if (typeof v === "object") {
            return JSON.stringify(v);
        }
        return v;
    }
}

export class LlmConversationMessageModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation_message";

    constructor({
        id = null,
        type = null,
        conversationId,
        content = null,
        model = null,
        createdAt = null,
        ownerId = null,
        organizationId
    }) {
        super();
        this.id = id || uuidv4();
        this.type = type;
        this.conversationId = conversationId;
        this.content = content;
        this.model = model;
        this.createdAt = createdAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
    }
}

export class LlmConversationMessageHistoryModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation_message_history";

    constructor({
        organizationId,
        conversationId,
        sessionId = null,
        queryId = null,
        messageId,
        responseId = null,
        previousMessageId = null,
        nextMessageId = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        ownerId = null
    }) {
        super();
        this.organizationId = organizationId;
        this.conversationId = conversationId;
        this.sessionId = sessionId;
        this.queryId = queryId;
        this.messageId = messageId;
        this.responseId = responseId;
        this.previousMessageId = previousMessageId;
        this.nextMessageId = nextMessageId;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.ownerId = ownerId;
    }

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
        idFieldName = null
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idFieldName
        );
    }

    static async fetchFromSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = {
                conversationId: value.conversationId,
                messageId: value.messageId
            };
        }
        return super.fetchFromSupabase(supabase, value, idFieldName);
    }

    static async existsInSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = {
                conversationId: value.conversationId,
                messageId: value.messageId
            };
        }
        return super.existsInSupabase(supabase, value, idFieldName);
    }
}

export class LlmConversationThreadModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation_thread";

    constructor({
        conversationId,
        parentMessageId,
        createdAt = null,
        ownerId = null,
        organizationId
    }) {
        super();
        this.conversationId = conversationId;
        this.parentMessageId = parentMessageId;
        this.createdAt = createdAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
    }

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
        idFieldName = null
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idFieldName
        );
    }

    static async fetchFromSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = {
                conversationId: value.conversationId,
                parentMessageId: value.parentMessageId
            };
        }
        return super.fetchFromSupabase(supabase, value, idFieldName);
    }

    static async existsInSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = {
                conversationId: value.conversationId,
                parentMessageId: value.parentMessageId
            };
        }
        return super.existsInSupabase(supabase, value, idFieldName);
    }
}
