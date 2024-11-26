import { SupabaseModel } from "./SupabaseModelInterface";

export interface ContextQuery extends SupabaseModel<ContextQuery> {
    id: string;
    params?: object;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface ContextQueryResponse
    extends SupabaseModel<ContextQueryResponse> {
    id: string;
    queryId?: string;
    responseData?: object;
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
    resultData?: object;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}
