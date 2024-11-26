// models/LlmConversationInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import { LlmConversationData } from "./data/ConversationDataInterfaces";

export interface LlmConversation {
    supabase: SupabaseClient;
    conversationData: LlmConversationData;
}
