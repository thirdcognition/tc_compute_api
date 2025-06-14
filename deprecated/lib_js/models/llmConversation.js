import { LlmConversationData } from "./data/conversationData.js";
import {
    LlmConversationModel,
    LlmConversationMessageModel,
    LlmConversationMessageHistoryModel
} from "./supabase/llmConversation.js";

class LlmConversation {
    constructor(supabase, authId, organizationId) {
        this.listeners = [];
        this.boundNotifyListeners = (...args) => this.notifyListeners(...args);
        this.supabase = supabase;
        this.conversationData = new LlmConversationData(
            supabase,
            authId,
            organizationId
        ).listen(this.boundNotifyListeners);
    }
    listen(callback) {
        if (
            typeof callback === "function" &&
            this.listeners.indexOf(callback) === -1
        ) {
            this.listeners.push(callback);
        }
        return this;
    }

    notifyListeners(...args) {
        this.listeners = this.listeners.filter(
            (listener) => listener(this, ...args) !== false
        );
    }
    async newMessage(model, initialMessage = null, initialResponse = null) {
        const conversation = new LlmConversationModel({
            startTime: new Date().toISOString()
        }).listen(this.boundNotifyListeners);
        await conversation.create(this.supabase);

        if (initialMessage !== null) {
            const message = new LlmConversationMessageModel({
                content: initialMessage,
                model: model,
                type: "human",
                conversationId: conversation.id
            }).listen(this.boundNotifyListeners);
            await message.create(this.supabase);
        }

        if (initialResponse !== null) {
            const response = new LlmConversationMessageModel({
                content: initialResponse,
                model: model,
                type: "ai",
                conversationId: conversation.id
            }).listen(this.boundNotifyListeners);
            await response.create(this.supabase);
        }
    }

    async getConversationHistory(conversationId) {
        return await LlmConversationMessageHistoryModel.fetchExistingFromSupabase(
            this.supabase,
            { filter: { conversationId: conversationId.toString() } }
        );
    }

    async getMessagesWithHistory(conversationId) {
        const history = await this.getConversationHistory(conversationId);

        const messageMapping = {};
        history.forEach((historyItem) => {
            if (historyItem.messageId !== null) {
                messageMapping[historyItem.messageId] = {
                    previousMessageId: historyItem.previousMessageId,
                    nextMessageId: historyItem.nextMessageId,
                    query: historyItem.queryId,
                    response: historyItem.responseId
                };
            }
        });

        const messages =
            await LlmConversationMessageModel.fetchExistingFromSupabase(
                this.supabase,
                { filter: { conversationId: conversationId.toString() } }
            );

        const messagesWithHistory = [];
        messages.forEach((message) => {
            if (messageMapping[message.id]) {
                const previousMessageId =
                    messageMapping[message.id].previousMessageId;
                const nextMessageId = messageMapping[message.id].nextMessageId;

                const previousMessage =
                    messages.find((msg) => msg.id === previousMessageId) ||
                    null;
                const nextMessage =
                    messages.find((msg) => msg.id === nextMessageId) || null;

                messagesWithHistory.push([
                    message,
                    nextMessage,
                    previousMessage
                ]);
            }
        });

        return messagesWithHistory;
    }
}

export default LlmConversation;
