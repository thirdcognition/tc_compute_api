import { SupabaseModel } from "./SupabaseModelInterface";

export interface JourneyProgress extends SupabaseModel<JourneyProgress> {
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

export interface JourneyProgressLLMConversationMessages
    extends SupabaseModel<JourneyProgressLLMConversationMessages> {
    journeyItemProgressId: string;
    messageId: string;
    conversationId: string;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface JourneyProgressLLMConversations
    extends SupabaseModel<JourneyProgressLLMConversations> {
    progressId: string;
    conversationId: string;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface JourneyItemProgress
    extends SupabaseModel<JourneyItemProgress> {
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
