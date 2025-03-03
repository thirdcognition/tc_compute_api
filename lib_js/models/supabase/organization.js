import { SupabaseModel } from "./supabaseModel.js";
import { ACLGroupUsersModel } from "./acl.js"; // Import ACLGroupUsersModel

// Define UserProfileModel
export class UserProfileModel extends SupabaseModel {
    static TABLE_NAME = "user_profile";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },

        authId: { type: "uuid", required: false, dbColumn: "auth_id" },
        email: { type: "string", required: false, dbColumn: "email" },
        name: { type: "string", required: false, dbColumn: "name" },
        profilePicture: {
            type: "string",
            required: false,
            dbColumn: "profile_picture"
        },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        lang: { type: "string", required: false, dbColumn: "lang" },
        activePanelId: {
            type: "uuid",
            required: false,
            dbColumn: "active_panel_id"
        },
        preferences: { type: "json", required: false, dbColumn: "preferences" },
        paymentDetails: {
            type: "json",
            required: false,
            dbColumn: "payment_details"
        },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        activeOrganizationId: {
            type: "uuid",
            required: false,
            dbColumn: "active_organization_id"
        },
        activeConversationId: {
            type: "uuid",
            required: false,
            dbColumn: "active_conversation_id"
        }
    };
}

// Define UserDataModel
export class UserDataModel extends SupabaseModel {
    static TABLE_NAME = "user_data";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        authId: { type: "uuid", required: false, dbColumn: "auth_id" },
        item: { type: "string", required: true, dbColumn: "item" },
        targetId: { type: "uuid", required: false, dbColumn: "target_id" },
        data: { type: "json", required: false, dbColumn: "data" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" }
    };
}

// Define OrganizationRoleModel
export class OrganizationRoleModel extends SupabaseModel {
    static TABLE_NAME = "organization_role";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        name: { type: "string", required: true, dbColumn: "name" },
        description: {
            type: "string",
            required: false,
            dbColumn: "description"
        },
        seniority: { type: "number", required: true, dbColumn: "seniority" },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
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
}

// Define OrganizationTeamModel
export class OrganizationTeamModel extends SupabaseModel {
    static TABLE_NAME = "organization_team";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        name: { type: "string", required: true, dbColumn: "name" },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
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

// Define OrganizationTeamMembersModel
export class OrganizationTeamMembersModel extends SupabaseModel {
    static TABLE_NAME = "organization_team_members";
    static TABLE_FIELDS = {
        authId: { type: "uuid", required: true, dbColumn: "auth_id" },
        userId: { type: "uuid", required: true, dbColumn: "user_id" },
        teamId: { type: "uuid", required: true, dbColumn: "team_id" },
        roleId: { type: "uuid", required: true, dbColumn: "role_id" },
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
        onConflict = ["authId", "teamId"]
    ) {
        return super.saveToSupabase(supabase, instance, onConflict);
    }

    static async upsertToSupabase(
        supabase,
        instances,
        onConflict = ["authId", "teamId"],
        idColumn = null
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idColumn
        );
    }

    static async fetchFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId,
                teamId: value.attributes.teamId
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId,
                teamId: value.attributes.teamId
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId,
                teamId: value.attributes.teamId
            };
        }
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

// Define OrganizationUsersModel
export class OrganizationUsersModel extends SupabaseModel {
    static TABLE_NAME = "organization_users";
    static TABLE_FIELDS = {
        authId: { type: "uuid", required: false, dbColumn: "auth_id" },
        userId: { type: "uuid", required: false, dbColumn: "user_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        isAdmin: { type: "boolean", required: false, dbColumn: "is_admin" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" }
    };

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
        idColumn = null
    ) {
        return super.upsertToSupabase(
            supabase,
            instances,
            onConflict,
            idColumn
        );
    }

    static async fetchFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId,
                organizationId: value.attributes.organizationId
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId,
                organizationId: value.attributes.organizationId
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId,
                organizationId: value.attributes.organizationId
            };
        }
        return super.deleteFromSupabase(supabase, value, idColumn);
    }

    async inAclGroup(supabase, aclGroupId) {
        return await ACLGroupUsersModel.existsInSupabase(supabase, {
            userId: this.attributes.userId,
            aclGroupId
        });
    }

    async connectWithAclGroup(supabase, aclGroupId, acl) {
        // Attempt to fetch the existing relationship
        const existingAclGroupUser = await ACLGroupUsersModel.fetchFromSupabase(
            supabase,
            { userId: this.attributes.userId, aclGroupId }
        );

        if (existingAclGroupUser) {
            // If the relationship exists, update the ACL level
            existingAclGroupUser.attributes.acl = acl;
            await existingAclGroupUser.update();
        } else {
            // Otherwise, create a new ACL group user relationship
            const aclGroupUser = new ACLGroupUsersModel({
                userId: this.attributes.userId,
                authId: this.attributes.authId,
                aclGroupId,
                acl,
                organizationId: this.attributes.organizationId
            });
            await ACLGroupUsersModel.saveToSupabase(supabase, aclGroupUser);
        }
    }

    async disconnectWithAclGroup(supabase, aclGroupId) {
        await ACLGroupUsersModel.deleteFromSupabase(supabase, {
            userId: this.attributes.userId,
            aclGroupId
        });
    }

    async create(supabase, groupsWithLevels = null) {
        const orgUser = await this.saveToSupabase(supabase, this);

        if (groupsWithLevels) {
            for (const [aclGroupId, acl] of Object.entries(groupsWithLevels)) {
                await orgUser.connectWithAclGroup(supabase, aclGroupId, acl);
            }
        }

        return orgUser;
    }
}

// Define OrganizationsModel
export class OrganizationsModel extends SupabaseModel {
    static TABLE_NAME = "organizations";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        defaultAclGroupId: {
            type: "uuid",
            required: false,
            dbColumn: "default_acl_group_id"
        },
        defaultBucketId: {
            type: "string",
            required: false,
            dbColumn: "default_bucket_id"
        },
        name: { type: "string", required: false, dbColumn: "name" },
        website: { type: "string", required: false, dbColumn: "website" },
        logo: { type: "string", required: false, dbColumn: "logo" },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" }
    };
}
