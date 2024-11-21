import { SupabaseModel } from "./supabaseModel.js";

// Define ContextQuery Model
export class ContextQuery extends SupabaseModel {
    static TABLE_NAME = "context_query";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: true, dbColumn: "id" },
        params: { type: "json", required: false, dbColumn: "params" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}

// Define ContextQueryResponse Model
export class ContextQueryResponse extends SupabaseModel {
    static TABLE_NAME = "context_query_response";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: true, dbColumn: "id" },
        queryId: { type: "uuid", required: false, dbColumn: "query_id" },
        responseData: {
            type: "json",
            required: false,
            dbColumn: "response_data"
        },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}

// Define ContextQueryResult Model
export class ContextQueryResult extends SupabaseModel {
    static TABLE_NAME = "context_query_result";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: true, dbColumn: "id" },
        queryId: { type: "uuid", required: false, dbColumn: "query_id" },
        resultData: { type: "json", required: false, dbColumn: "result_data" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}
