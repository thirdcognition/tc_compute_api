import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export class ContextQuery extends SupabaseModel {
    static TABLE_NAME = "context_query";

    constructor(args) {
        super();
        const {
            id,
            params = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: true,
                dbColumn: "id"
            },
            params: {
                value: params,
                type: "json",
                required: false,
                dbColumn: "params"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            },
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            }
        };
    }
}

export class ContextQueryResponse extends SupabaseModel {
    static TABLE_NAME = "context_query_response";

    constructor(args) {
        super();
        const {
            id,
            queryId = null,
            responseData = null,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: true,
                dbColumn: "id"
            },
            queryId: {
                value: queryId,
                type: "uuid",
                required: false,
                dbColumn: "query_id"
            },
            responseData: {
                value: responseData,
                type: "json",
                required: false,
                dbColumn: "response_data"
            },
            disabled: {
                value: disabled,
                type: "boolean",
                required: false,
                dbColumn: "disabled"
            },
            disabledAt: {
                value: disabledAt,
                type: "date",
                required: false,
                dbColumn: "disabled_at"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            },
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            }
        };
    }
}

export class ContextQueryResult extends SupabaseModel {
    static TABLE_NAME = "context_query_result";

    constructor(args) {
        super();
        const {
            id,
            queryId = null,
            resultData = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: true,
                dbColumn: "id"
            },
            queryId: {
                value: queryId,
                type: "uuid",
                required: false,
                dbColumn: "query_id"
            },
            resultData: {
                value: resultData,
                type: "json",
                required: false,
                dbColumn: "result_data"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            },
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            }
        };
    }
}
