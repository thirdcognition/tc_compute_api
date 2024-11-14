import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export class ContextQuery extends SupabaseModel {
    static TABLE_NAME = "context_query";

    constructor({
        id,
        params = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId
    }) {
        super();
        this.id = id || uuidv4();
        this.params = params;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
    }
}

export class ContextQueryResponse extends SupabaseModel {
    static TABLE_NAME = "context_query_response";

    constructor({
        id,
        queryId = null,
        responseData = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId
    }) {
        super();
        this.id = id || uuidv4();
        this.queryId = queryId;
        this.responseData = responseData;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
    }
}

export class ContextQueryResult extends SupabaseModel {
    static TABLE_NAME = "context_query_result";

    constructor({
        id,
        queryId = null,
        resultData = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId
    }) {
        super();
        this.id = id || uuidv4();
        this.queryId = queryId;
        this.resultData = resultData;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
    }

    static validateResultData(v) {
        if (typeof v === "string") {
            return JSON.parse(v);
        } else if (typeof v === "object") {
            return JSON.stringify(v);
        }
        return v;
    }
}
