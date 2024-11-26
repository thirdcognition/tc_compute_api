// models/data/ConversationDataInterfaces.ts

import { UserData } from "./UserDataInterfaces";
import {
    LlmConversationModel,
    LlmConversationMessageModel,
    LlmConversationMessageHistoryModel,
    LlmConversationThreadModel
} from "../supabase/llmConversation";

export interface LlmConversationData {
    user: UserData;
    conversations: LlmConversationModel[] | null;
    messages: LlmConversationMessageModel[] | null;
    messageHistory: LlmConversationMessageHistoryModel[] | null;
    threads: LlmConversationThreadModel[] | null;

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
}
