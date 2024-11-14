import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export const ACL = Object.freeze({
    PUBLIC: "public",
    GROUP: "group",
    PRIVATE: "private"
});

export const UserACL = Object.freeze({
    ADM: "adm",
    RW: "rw",
    RO: "ro"
});

export class ACLGroupModel extends SupabaseModel {
    static TABLE_NAME = "acl_group";

    constructor({
        id = null,
        name,
        description = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null,
        organizationId
    }) {
        super();
        this.id = id || uuidv4();
        this.name = name;
        this.description = description;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
    }
}

export class ACLGroupItemsModel extends SupabaseModel {
    static TABLE_NAME = "acl_group_items";

    constructor({
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
    }) {
        super();
        this.aclGroupId = aclGroupId;
        this.acl = acl;
        this.itemId = itemId;
        this.itemType = itemType;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
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
        idFieldName = "aclGroupId"
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idFieldName
        );
    }

    static async fetchFromSupabase(
        supabase,
        value = null,
        idFieldName = "aclGroupId"
    ) {
        return super.fetchFromSupabase(supabase, value, idFieldName);
    }

    static async existsInSupabase(
        supabase,
        value = null,
        idFieldName = "aclGroupId"
    ) {
        return super.existsInSupabase(supabase, value, idFieldName);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idFieldName = "aclGroupId"
    ) {
        return super.deleteFromSupabase(supabase, value, idFieldName);
    }
}

export class ACLGroupUsersModel extends SupabaseModel {
    static TABLE_NAME = "acl_group_users";

    constructor({
        authId,
        userId,
        aclGroupId,
        acl = UserACL.RO,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        organizationId
    }) {
        super();
        this.authId = authId;
        this.userId = userId;
        this.aclGroupId = aclGroupId;
        this.acl = acl;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.organizationId = organizationId;
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
        idFieldName = "aclGroupId"
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idFieldName
        );
    }

    static async fetchFromSupabase(
        supabase,
        value = null,
        idFieldName = "aclGroupId"
    ) {
        return super.fetchFromSupabase(supabase, value, idFieldName);
    }

    static async existsInSupabase(
        supabase,
        value = null,
        idFieldName = "aclGroupId"
    ) {
        return super.existsInSupabase(supabase, value, idFieldName);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idFieldName = "aclGroupId"
    ) {
        return super.deleteFromSupabase(supabase, value, idFieldName);
    }
}

export class ACLGroupUsersWithItems {
    constructor({
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
    }) {
        this.organizationId = organizationId;
        this.aclGroupId = aclGroupId;
        this.itemId = itemId;
        this.itemType = itemType;
        this.itemAcl = itemAcl;
        this.itemCreatedAt = itemCreatedAt;
        this.itemDisabled = itemDisabled;
        this.itemDisabledAt = itemDisabledAt;
        this.authId = authId;
        this.userAcl = userAcl;
        this.userId = userId;
        this.userCreatedAt = userCreatedAt;
        this.userDisabled = userDisabled;
        this.userDisabledAt = userDisabledAt;
    }
}
