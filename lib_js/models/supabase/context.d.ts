import { SupabaseModel } from "./supabaseModel";

export declare class ContextQuery extends SupabaseModel<ContextQuery> {
    id: string;
    params?: Record<string, unknown>;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export declare class ContextQueryResponse extends SupabaseModel<ContextQueryResponse> {
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

export declare class ContextQueryResult extends SupabaseModel<ContextQueryResult> {
    id: string;
    queryId?: string;
    resultData?: Record<string, unknown>;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}
