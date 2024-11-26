export interface LlmConversation {
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

export interface LlmConversationMessage {
    id?: string;
    type?: string;
    conversationId: string;
    content?: string;
    model?: string;
    createdAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface LlmConversationMessageHistory {
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

export interface LlmConversationThread {
    conversationId: string;
    parentMessageId: string;
    createdAt?: Date;
    ownerId?: string;
    organizationId?: string;
}
