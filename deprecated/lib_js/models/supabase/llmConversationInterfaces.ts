import { SupabaseModel } from "./SupabaseModelInterface";

export interface LlmConversation extends SupabaseModel<LlmConversation> {
    id?: string;
    startTime?: Date;
    endTime?: Date;
    title?: string;
    tags?: string[];
    metadata?: object;
    createdAt?: Date;
    ownerId?: string;
    organizationId?: string;
    state?: string;
}

export interface LlmConversationMessage
    extends SupabaseModel<LlmConversationMessage> {
    id?: string;
    type?: string;
    conversationId: string;
    content?: string;
    model?: string;
    createdAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface LlmConversationMessageHistory
    extends SupabaseModel<LlmConversationMessageHistory> {
    organizationId?: string;
    conversationId: string;
    sessionId?: string;
    queryId?: string;
    messageId: string;
    responseId?: string;
    previousMessageId?: string;
    nextMessageId?: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    ownerId?: string;
}

export interface LlmConversationThread
    extends SupabaseModel<LlmConversationThread> {
    conversationId: string;
    parentMessageId: string;
    createdAt?: Date;
    ownerId?: string;
    organizationId?: string;
}
