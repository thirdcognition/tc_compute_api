import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

// Define LlmConversationModel
export class LlmConversationModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation";

    constructor(args) {
        super();
        const {
            id = null,
            startTime = null,
            endTime = null,
            title = null,
            tags = null,
            metadata = null,
            createdAt = null,
            ownerId = null,
            organizationId = null,
            state = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            startTime: {
                value: startTime,
                type: "date",
                required: false,
                dbColumn: "start_time"
            },
            endTime: {
                value: endTime,
                type: "date",
                required: false,
                dbColumn: "end_time"
            },
            title: {
                value: title,
                type: "string",
                required: false,
                dbColumn: "title"
            },
            tags: {
                value: tags,
                type: "array",
                required: false,
                dbColumn: "tags"
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
            state: {
                value: state,
                type: "string",
                required: false,
                dbColumn: "state"
            }
        };
    }
}

// Define LlmConversationMessageModel
export class LlmConversationMessageModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation_message";

    constructor(args) {
        super();
        const {
            id = null,
            type = null,
            conversationId,
            content = null,
            model = null,
            createdAt = null,
            ownerId = null,
            organizationId = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            type: {
                value: type,
                type: "string",
                required: false,
                dbColumn: "type"
            },
            conversationId: {
                value: conversationId,
                type: "uuid",
                required: true,
                dbColumn: "conversation_id"
            },
            content: {
                value: content,
                type: "string",
                required: false,
                dbColumn: "content"
            },
            model: {
                value: model,
                type: "string",
                required: false,
                dbColumn: "model"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
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
}

// Define LlmConversationMessageHistoryModel
export class LlmConversationMessageHistoryModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation_message_history";

    constructor(args) {
        super();
        const {
            organizationId = null,
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
        } = args;
        this.attributes = {
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: false,
                dbColumn: "organization_id"
            },
            conversationId: {
                value: conversationId,
                type: "uuid",
                required: true,
                dbColumn: "conversation_id"
            },
            sessionId: {
                value: sessionId,
                type: "uuid",
                required: false,
                dbColumn: "session_id"
            },
            queryId: {
                value: queryId,
                type: "uuid",
                required: false,
                dbColumn: "query_id"
            },
            messageId: {
                value: messageId,
                type: "uuid",
                required: true,
                dbColumn: "message_id"
            },
            responseId: {
                value: responseId,
                type: "uuid",
                required: false,
                dbColumn: "response_id"
            },
            previousMessageId: {
                value: previousMessageId,
                type: "uuid",
                required: false,
                dbColumn: "previous_message_id"
            },
            nextMessageId: {
                value: nextMessageId,
                type: "uuid",
                required: false,
                dbColumn: "next_message_id"
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
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            }
        };
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
                conversationId: value.attributes.conversationId.value,
                messageId: value.attributes.messageId.value
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                conversationId: value.attributes.conversationId.value,
                messageId: value.attributes.messageId.value
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }
}

// Define LlmConversationThreadModel
export class LlmConversationThreadModel extends SupabaseModel {
    static TABLE_NAME = "llm_conversation_thread";

    constructor(args) {
        super();
        const {
            conversationId,
            parentMessageId,
            createdAt = null,
            ownerId = null,
            organizationId = null
        } = args;
        this.attributes = {
            conversationId: {
                value: conversationId,
                type: "uuid",
                required: true,
                dbColumn: "conversation_id"
            },
            parentMessageId: {
                value: parentMessageId,
                type: "uuid",
                required: true,
                dbColumn: "parent_message_id"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
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
                conversationId: value.attributes.conversationId.value,
                parentMessageId: value.attributes.parentMessageId.value
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                conversationId: value.attributes.conversationId.value,
                parentMessageId: value.attributes.parentMessageId.value
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }
}
