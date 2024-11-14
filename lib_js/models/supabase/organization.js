import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export class UserProfileModel extends SupabaseModel {
    static TABLE_NAME = "user_profile";

    constructor({
        id = null,
        authId = null,
        email = null,
        name = null,
        profilePicture = null,
        metadata = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        activeOrganizationId = null,
        activeConversationId = null
    }) {
        super();
        this.id = id || uuidv4();
        this.authId = authId;
        this.email = email;
        this.name = name;
        this.profilePicture = profilePicture;
        this.metadata = metadata;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.activeOrganizationId = activeOrganizationId;
        this.activeConversationId = activeConversationId;
    }
}

export class OrganizationRoleModel extends SupabaseModel {
    static TABLE_NAME = "organization_role";

    constructor({
        id = null,
        name,
        description = null,
        seniority,
        metadata = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        organizationId
    }) {
        super();
        this.id = id || uuidv4();
        this.name = name;
        this.description = description;
        this.seniority = seniority;
        this.metadata = metadata;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.organizationId = organizationId;
    }
}

export class OrganizationTeamModel extends SupabaseModel {
    static TABLE_NAME = "organization_team";

    constructor({
        id = null,
        name,
        metadata = null,
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
        this.metadata = metadata;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
    }
}

export class OrganizationTeamMembersModel extends SupabaseModel {
    static TABLE_NAME = "organization_team_members";

    constructor({
        authId,
        userId,
        teamId,
        roleId,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        organizationId
    }) {
        super();
        this.authId = authId;
        this.userId = userId;
        this.teamId = teamId;
        this.roleId = roleId;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.organizationId = organizationId;
    }

    static async saveToSupabase(
        supabase,
        instance,
        onConflict = ["authId", "teamId"]
    ) {
        return super.saveToSupabase(supabase, instance, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["authId", "teamId"],
        idFieldName = null
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idFieldName
        );
    }

    static async fetchFromSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = { authId: value.authId, teamId: value.teamId };
        }
        return super.fetchFromSupabase(supabase, value, idFieldName);
    }

    static async existsInSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = { authId: value.authId, teamId: value.teamId };
        }
        return super.existsInSupabase(supabase, value, idFieldName);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idFieldName = null
    ) {
        if (value instanceof this) {
            value = { authId: value.authId, teamId: value.teamId };
        }
        return super.deleteFromSupabase(supabase, value, idFieldName);
    }
}

export class OrganizationUsersModel extends SupabaseModel {
    static TABLE_NAME = "organization_users";

    constructor({
        authId = null,
        userId = null,
        organizationId,
        metadata = null,
        isAdmin = false,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null
    }) {
        super();
        this.authId = authId;
        this.userId = userId;
        this.organizationId = organizationId;
        this.metadata = metadata;
        this.isAdmin = isAdmin;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    static async saveToSupabase(
        supabase,
        instance,
        onConflict = ["authId", "organizationId"]
    ) {
        return super.saveToSupabase(supabase, instance, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["authId", "organizationId"],
        idFieldName = null
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idFieldName
        );
    }

    static async fetchFromSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = {
                authId: value.authId,
                organizationId: value.organizationId
            };
        }
        return super.fetchFromSupabase(supabase, value, idFieldName);
    }

    static async existsInSupabase(supabase, value = null, idFieldName = null) {
        if (value instanceof this) {
            value = {
                authId: value.authId,
                organizationId: value.organizationId
            };
        }
        return super.existsInSupabase(supabase, value, idFieldName);
    }

    static async deleteFromSupabase(
        supabase,
        value = null,
        idFieldName = null
    ) {
        if (value instanceof this) {
            value = {
                authId: value.authId,
                organizationId: value.organizationId
            };
        }
        return super.deleteFromSupabase(supabase, value, idFieldName);
    }
}

export class OrganizationsModel extends SupabaseModel {
    static TABLE_NAME = "organizations";

    constructor({
        id = null,
        name = null,
        website = null,
        logo = null,
        metadata = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        ownerId = null
    }) {
        super();
        this.id = id || uuidv4();
        this.name = name;
        this.website = website;
        this.logo = logo;
        this.metadata = metadata;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
    }
}
