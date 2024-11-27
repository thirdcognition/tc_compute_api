import {
    LlmConversationModel,
    LlmConversationMessageModel,
    LlmConversationMessageHistoryModel,
    LlmConversationThreadModel
} from "../supabase/llmConversation.js";

export class LlmConversationData {
    constructor(
        user,
        conversations = null,
        messages = null,
        messageHistory = null,
        threads = null
    ) {
        this.listeners = [];
        this.boundNotifyListeners = (...args) => this.notifyListeners(...args);
        this.user = user;
        this.conversations = conversations;
        this.messages = messages;
        this.messageHistory = messageHistory;
        this.threads = threads;
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
    async saveAllToSupabase() {
        const supabase = this.user.supabase;
        const upsertTasks = [];

        if (this.conversations) {
            upsertTasks.push(
                this.conversations[0].upsertToSupabase(
                    supabase,
                    this.conversations
                )
            );
        }
        if (this.messages) {
            upsertTasks.push(
                this.messages[0].upsertToSupabase(supabase, this.messages)
            );
        }
        if (this.messageHistory) {
            upsertTasks.push(
                this.messageHistory[0].upsertToSupabase(
                    supabase,
                    this.messageHistory
                )
            );
        }
        if (this.threads) {
            upsertTasks.push(
                this.threads[0].upsertToSupabase(supabase, this.threads)
            );
        }

        await Promise.all(upsertTasks);
    }

    async fetchConversations(refresh = false) {
        if (!this.conversations || refresh) {
            this.conversations = (
                await LlmConversationModel.fetchExistingFromSupabase(
                    this.user.supabase,
                    {
                        owner_id: String(this.user.authId),
                        organization_id: String(this.user.activeOrganizationId)
                    }
                )
            ).listen(this.boundNotifyListeners);
            this.notifyListeners();
        }
    }

    async fetchMessages(refresh = false) {
        if (!this.messages || refresh) {
            this.messages = (
                await LlmConversationMessageModel.fetchExistingFromSupabase(
                    this.user.supabase,
                    {
                        owner_id: String(this.user.authId),
                        organization_id: String(this.user.activeOrganizationId)
                    }
                )
            ).listen(this.boundNotifyListeners);
            this.notifyListeners();
        }
    }

    async fetchMessageHistory(refresh = false) {
        if (!this.messageHistory || refresh) {
            this.messageHistory = (
                await LlmConversationMessageHistoryModel.fetchExistingFromSupabase(
                    this.user.supabase,
                    {
                        owner_id: String(this.user.authId),
                        organization_id: String(this.user.activeOrganizationId)
                    }
                )
            ).listen(this.boundNotifyListeners);
            this.notifyListeners();
        }
    }

    async fetchThreads(refresh = false) {
        if (!this.threads || refresh) {
            this.threads = (
                await LlmConversationThreadModel.fetchExistingFromSupabase(
                    this.user.supabase,
                    {
                        owner_id: String(this.user.authId),
                        organization_id: String(this.user.activeOrganizationId)
                    }
                )
            ).listen(this.boundNotifyListeners);
            this.notifyListeners();
        }
    }

    async newMessage(model, initialMessage = null, initialResponse = null) {
        const conversation = new LlmConversationModel({
            startTime: new Date().toISOString()
        });
        await conversation.create(this.user.supabase);

        if (initialMessage !== null) {
            const message = new LlmConversationMessageModel({
                content: initialMessage,
                model: model,
                type: "human",
                conversationId: conversation.id,
                ownerId: this.user.authId,
                organizationId: this.user.activeOrganizationId
            }).listen(this.boundNotifyListeners);
            await message.create(this.user.supabase);
        }

        if (initialResponse !== null) {
            const response = new LlmConversationMessageModel({
                content: initialResponse,
                model: model,
                type: "ai",
                conversationId: conversation.id,
                ownerId: this.user.authId,
                organizationId: this.user.activeOrganizationId
            }).listen(this.boundNotifyListeners);
            await response.create(this.user.supabase);
        }
        this.notifyListeners();
    }
}
