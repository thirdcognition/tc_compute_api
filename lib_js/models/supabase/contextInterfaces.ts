import { SupabaseModel } from "./SupabaseModelInterface";

export interface ContextQuery extends SupabaseModel<ContextQuery> {
    id: string;
    params?: Record<string, unknown>;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface ContextQueryResponse
    extends SupabaseModel<ContextQueryResponse> {
    id: string;
    queryId?: string;
    responseData?: Record<string, unknown>;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface ContextQueryResult extends SupabaseModel<ContextQueryResult> {
    id: string;
    queryId?: string;
    resultData?: Record<string, unknown>;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}
