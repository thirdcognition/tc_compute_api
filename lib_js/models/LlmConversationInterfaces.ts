// models/LlmConversationInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import { LlmConversationData } from "./data/ConversationDataInterfaces";
import {
    LlmConversationMessageHistory,
    LlmConversationMessage
} from "./supabase/llmConversationInterfaces";

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
    ): Promise<LlmConversationMessageHistory[]>;
    getMessagesWithHistory(
        conversationId: string
    ): Promise<
        [
            LlmConversationMessage,
            LlmConversationMessage | null,
            LlmConversationMessage | null
        ][]
    >;

    listen(
        callback: (model: LlmConversation, ...args: unknown[]) => boolean | void
    ): this;
    notifyListeners(...args: unknown[]): void;
}
