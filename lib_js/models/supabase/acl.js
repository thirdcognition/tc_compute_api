import { SupabaseModel, Enum } from "./supabaseModel.js";

// Define ACL Enum
class ACLEnum extends Enum {
    constructor() {
        super();
        this.PUBLIC = "public";
        this.GROUP = "group";
        this.PRIVATE = "private";
        Object.freeze(this);
    }
}

// Define UserACL Enum
class UserACLEnum extends Enum {
    constructor() {
        super();
        this.ADM = "adm";
        this.RW = "rw";
        this.RO = "ro";
        Object.freeze(this);
    }
}

export const ACL = new ACLEnum();
export const UserACL = new UserACLEnum();

// Define ACLGroupModel
export class ACLGroupModel extends SupabaseModel {
    static TABLE_NAME = "acl_group";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        name: { type: "string", required: true, dbColumn: "name" },
        description: {
            type: "string",
            required: false,
            dbColumn: "description"
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

// Define ACLGroupItemsModel
export class ACLGroupItemsModel extends SupabaseModel {
    static TABLE_NAME = "acl_group_items";
    static TABLE_FIELDS = {
        aclGroupId: { type: "uuid", required: true, dbColumn: "acl_group_id" },
        acl: { type: ACL, required: false, dbColumn: "acl" },
        itemId: { type: "uuid", required: true, dbColumn: "item_id" },
        itemType: { type: "string", required: true, dbColumn: "item_type" },
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

    static async saveToSupabase(
        supabase,
        instance,
        onConflict = ["itemId", "aclGroupId"]
    ) {
        return super.saveToSupabase(supabase, instance, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["itemId", "aclGroupId"],
        idColumn = "aclGroupId"
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idColumn
        );
    }

    static async fetchFromSupabase(
        supabase,
        value = null,
        idColumn = "aclGroupId"
    ) {
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(
        supabase,
        value = null,
        idColumn = "aclGroupId"
    ) {
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idColumn = "aclGroupId"
    ) {
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

// Define ACLGroupUsersModel
export class ACLGroupUsersModel extends SupabaseModel {
    static TABLE_NAME = "acl_group_users";
    static TABLE_FIELDS = {
        authId: { type: "uuid", required: true, dbColumn: "auth_id" },
        userId: { type: "uuid", required: true, dbColumn: "user_id" },
        aclGroupId: { type: "uuid", required: true, dbColumn: "acl_group_id" },
        acl: { type: UserACL, required: false, dbColumn: "acl" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };

    static async saveToSupabase(
        supabase,
        instance,
        onConflict = ["userId", "aclGroupId"]
    ) {
        return super.saveToSupabase(supabase, instance, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["userId", "aclGroupId"],
        idColumn = "aclGroupId"
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idColumn
        );
    }

    static async fetchFromSupabase(
        supabase,
        value = null,
        idColumn = "aclGroupId"
    ) {
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(
        supabase,
        value = null,
        idColumn = "aclGroupId"
    ) {
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idColumn = "aclGroupId"
    ) {
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

// Define ACLGroupUsersWithItems
export class ACLGroupUsersWithItems extends SupabaseModel {
    static TABLE_NAME = "acl_group_users_with_items";
    static TABLE_FIELDS = {
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        aclGroupId: { type: "uuid", required: true, dbColumn: "acl_group_id" },
        itemId: { type: "uuid", required: true, dbColumn: "item_id" },
        itemType: { type: "string", required: true, dbColumn: "item_type" },
        itemAcl: { type: ACL, required: true, dbColumn: "item_acl" },
        itemCreatedAt: {
            type: "date",
            required: false,
            dbColumn: "item_created_at"
        },
        itemDisabled: {
            type: "boolean",
            required: true,
            dbColumn: "item_disabled"
        },
        itemDisabledAt: {
            type: "date",
            required: false,
            dbColumn: "item_disabled_at"
        },
        authId: { type: "uuid", required: true, dbColumn: "auth_id" },
        userAcl: { type: UserACL, required: true, dbColumn: "user_acl" },
        userId: { type: "uuid", required: true, dbColumn: "user_id" },
        userCreatedAt: {
            type: "date",
            required: false,
            dbColumn: "user_created_at"
        },
        userDisabled: {
            type: "boolean",
            required: true,
            dbColumn: "user_disabled"
        },
        userDisabledAt: {
            type: "date",
            required: false,
            dbColumn: "user_disabled_at"
        }
    };
}
