export interface JourneyProgress {
    id?: string;
    journeyId: string;
    journeyVersionId: string;
    assignedAt?: Date;
    metadata?: object;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    startedAt?: Date;
    completedAt?: Date;
}

export interface JourneyProgressLLMConversationMessages {
    journeyItemProgressId: string;
    messageId: string;
    conversationId: string;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface JourneyProgressLLMConversations {
    progressId: string;
    conversationId: string;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface JourneyItemProgress {
    id?: string;
    journeyProgressId: string;
    journeyItemId: string;
    journeyItemVersionId: string;
    data?: object;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    startedAt?: Date;
    completedAt?: Date;
}
