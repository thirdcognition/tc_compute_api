// models/LlmConversationInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import { LlmConversationData } from "./data/ConversationDataInterfaces";
import {
    LlmConversationMessageHistoryModel,
    LlmConversationMessageModel
} from "./supabase/llmConversation";

export interface LlmConversation {
    supabase: SupabaseClient;
    conversationData: LlmConversationData;

    // Methods
    newMessage(
        model: string,
        initialMessage?: string | null,
        initialResponse?: string | null
    ): Promise<void>;
    getConversationHistory(
        conversationId: string
    ): Promise<LlmConversationMessageHistoryModel[]>;
    getMessagesWithHistory(
        conversationId: string
    ): Promise<
        [
            LlmConversationMessageModel,
            LlmConversationMessageModel | null,
            LlmConversationMessageModel | null
        ][]
    >;

    listen(
        callback: (model: LlmConversation, ...args: unknown[]) => boolean | void
    ): this;
    notifyListeners(...args: unknown[]): void;
}
