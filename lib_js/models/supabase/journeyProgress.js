import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export class JourneyProgressModel extends SupabaseModel {
    static TABLE_NAME = "journey_progress";

    constructor({
        id = null,
        journeyId,
        journeyVersionId,
        assignedAt = null,
        metadata = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId,
        startedAt = null,
        completedAt = null
    }) {
        super();
        this.id = id || uuidv4();
        this.journeyId = journeyId;
        this.journeyVersionId = journeyVersionId;
        this.assignedAt = assignedAt;
        this.metadata = metadata;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.startedAt = startedAt;
        this.completedAt = completedAt;
    }
}

export class JourneyProgressLLMConversationMessagesModel extends SupabaseModel {
    static TABLE_NAME = "journey_progress_llm_conversation_messages";

    constructor({
        journeyItemProgressId,
        messageId,
        conversationId,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId
    }) {
        super();
        this.journeyItemProgressId = journeyItemProgressId;
        this.messageId = messageId;
        this.conversationId = conversationId;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
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
                journeyItemProgressId: value.journeyItemProgressId,
                messageId: value.messageId
            };
        }
        return super.fetchFromSupabase(supabase, value, idFieldName);
    }

    static async existsInSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = {
                journeyItemProgressId: value.journeyItemProgressId,
                messageId: value.messageId
            };
        }
        return super.existsInSupabase(supabase, value, idFieldName);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idFieldName = null
    ) {
        if (value instanceof this) {
            value = {
                journeyItemProgressId: value.journeyItemProgressId,
                messageId: value.messageId
            };
        }
        return super.deleteFromSupabase(supabase, value, idFieldName);
    }
}

export class JourneyProgressLLMConversationsModel extends SupabaseModel {
    static TABLE_NAME = "journey_progress_llm_conversations";

    constructor({
        progressId,
        conversationId,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId
    }) {
        super();
        this.progressId = progressId;
        this.conversationId = conversationId;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
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
        idFieldName = null
    ) {
        return super.upsertToSupabase(
            supabase,
            instance,
            onConflict,
            idFieldName
        );
    }

    static async fetchFromSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = {
                progressId: value.progressId,
                conversationId: value.conversationId
            };
        }
        return super.fetchFromSupabase(supabase, value, idFieldName);
    }

    static async existsInSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = {
                progressId: value.progressId,
                conversationId: value.conversationId
            };
        }
        return super.existsInSupabase(supabase, value, idFieldName);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idFieldName = null
    ) {
        if (value instanceof this) {
            value = {
                progressId: value.progressId,
                conversationId: value.conversationId
            };
        }
        return super.deleteFromSupabase(supabase, value, idFieldName);
    }
}

export class JourneyItemProgressModel extends SupabaseModel {
    static TABLE_NAME = "journey_item_progress";

    constructor({
        id = null,
        journeyProgressId,
        journeyItemId,
        journeyItemVersionId,
        data = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId,
        startedAt = null,
        completedAt = null
    }) {
        super();
        this.id = id || uuidv4();
        this.journeyProgressId = journeyProgressId;
        this.journeyItemId = journeyItemId;
        this.journeyItemVersionId = journeyItemVersionId;
        this.data = data;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.startedAt = startedAt;
        this.completedAt = completedAt;
    }
}
