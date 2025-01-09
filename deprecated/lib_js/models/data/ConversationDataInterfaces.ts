// models/data/ConversationDataInterfaces.ts

import { UserData } from "./UserDataInterfaces";
import {
    LlmConversation,
    LlmConversationMessage,
    LlmConversationMessageHistory,
    LlmConversationThread
} from "../supabase/llmConversationInterfaces";

export interface LlmConversationData {
    user: UserData;
    conversations: LlmConversation[] | null;
    messages: LlmConversationMessage[] | null;
    messageHistory: LlmConversationMessageHistory[] | null;
    threads: LlmConversationThread[] | null;

    // Methods
    saveAllToSupabase(): Promise<void>;
    fetchConversations(refresh?: boolean): Promise<void>;
    fetchMessages(refresh?: boolean): Promise<void>;
    fetchMessageHistory(refresh?: boolean): Promise<void>;
    fetchThreads(refresh?: boolean): Promise<void>;
    newMessage(
        model: string,
        initialMessage?: string | null,
        initialResponse?: string | null
    ): Promise<void>;

    // New methods
    listen(
        callback: (
            model: LlmConversationData,
            ...args: unknown[]
        ) => boolean | void
    ): this;
    notifyListeners(...args: unknown[]): void;
}
