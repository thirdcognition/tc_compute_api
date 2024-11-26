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
}
