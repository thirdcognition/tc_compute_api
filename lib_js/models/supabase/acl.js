import { SupabaseModel, Enum } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

class ACLEnum extends Enum {
    constructor() {
        super();
        this.PUBLIC = "public";
        this.GROUP = "group";
        this.PRIVATE = "private";
        Object.freeze(this);
    }
}

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

export class ACLGroupModel extends SupabaseModel {
    static TABLE_NAME = "acl_group";

    constructor(args) {
        super();
        const {
            id = null,
            name,
            description = null,
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
                required: false,
                dbColumn: "id"
            },
            name: {
                value: name,
                type: "string",
                required: true,
                dbColumn: "name"
            },
            description: {
                value: description,
                type: "string",
                required: false,
                dbColumn: "description"
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

export class ACLGroupItemsModel extends SupabaseModel {
    static TABLE_NAME = "acl_group_items";

    constructor(args) {
        super();
        const {
            aclGroupId,
            acl = ACL.PRIVATE,
            itemId,
            itemType,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId
        } = args;
        this.attributes = {
            aclGroupId: {
                value: aclGroupId,
                type: "uuid",
                required: true,
                dbColumn: "acl_group_id"
            },
            acl: { value: acl, type: ACL, required: false, dbColumn: "acl" },
            itemId: {
                value: itemId,
                type: "uuid",
                required: true,
                dbColumn: "item_id"
            },
            itemType: {
                value: itemType,
                type: "string",
                required: true,
                dbColumn: "item_type"
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

export class ACLGroupUsersModel extends SupabaseModel {
    static TABLE_NAME = "acl_group_users";

    constructor(args) {
        super();
        const {
            authId,
            userId,
            aclGroupId,
            acl = UserACL.RO,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            organizationId
        } = args;
        this.attributes = {
            authId: {
                value: authId,
                type: "uuid",
                required: true,
                dbColumn: "auth_id"
            },
            userId: {
                value: userId,
                type: "uuid",
                required: true,
                dbColumn: "user_id"
            },
            aclGroupId: {
                value: aclGroupId,
                type: "uuid",
                required: true,
                dbColumn: "acl_group_id"
            },
            acl: {
                value: acl,
                type: UserACL,
                required: false,
                dbColumn: "acl"
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
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            }
        };
    }

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

export class ACLGroupUsersWithItems {
    constructor(args) {
        const {
            organizationId,
            aclGroupId,
            itemId,
            itemType,
            itemAcl,
            itemCreatedAt = null,
            itemDisabled,
            itemDisabledAt = null,
            authId,
            userAcl,
            userId,
            userCreatedAt = null,
            userDisabled,
            userDisabledAt = null
        } = args;
        this.attributes = {
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            },
            aclGroupId: {
                value: aclGroupId,
                type: "uuid",
                required: true,
                dbColumn: "acl_group_id"
            },
            itemId: {
                value: itemId,
                type: "uuid",
                required: true,
                dbColumn: "item_id"
            },
            itemType: {
                value: itemType,
                type: "string",
                required: true,
                dbColumn: "item_type"
            },
            itemAcl: {
                value: itemAcl,
                type: ACL,
                required: true,
                dbColumn: "item_acl"
            },
            itemCreatedAt: {
                value: itemCreatedAt,
                type: "date",
                required: false,
                dbColumn: "item_created_at"
            },
            itemDisabled: {
                value: itemDisabled,
                type: "boolean",
                required: true,
                dbColumn: "item_disabled"
            },
            itemDisabledAt: {
                value: itemDisabledAt,
                type: "date",
                required: false,
                dbColumn: "item_disabled_at"
            },
            authId: {
                value: authId,
                type: "uuid",
                required: true,
                dbColumn: "auth_id"
            },
            userAcl: {
                value: userAcl,
                type: UserACL,
                required: true,
                dbColumn: "user_acl"
            },
            userId: {
                value: userId,
                type: "uuid",
                required: true,
                dbColumn: "user_id"
            },
            userCreatedAt: {
                value: userCreatedAt,
                type: "date",
                required: false,
                dbColumn: "user_created_at"
            },
            userDisabled: {
                value: userDisabled,
                type: "boolean",
                required: true,
                dbColumn: "user_disabled"
            },
            userDisabledAt: {
                value: userDisabledAt,
                type: "date",
                required: false,
                dbColumn: "user_disabled_at"
            }
        };
    }
}
