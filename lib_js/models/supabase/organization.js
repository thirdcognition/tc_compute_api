import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export class UserProfileModel extends SupabaseModel {
    static TABLE_NAME = "user_profile";

    constructor(args) {
        super();
        const {
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
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            authId: {
                value: authId,
                type: "uuid",
                required: false,
                dbColumn: "auth_id"
            },
            email: {
                value: email,
                type: "string",
                required: false,
                dbColumn: "email"
            },
            name: {
                value: name,
                type: "string",
                required: false,
                dbColumn: "name"
            },
            profilePicture: {
                value: profilePicture,
                type: "string",
                required: false,
                dbColumn: "profile_picture"
            },
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
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
            activeOrganizationId: {
                value: activeOrganizationId,
                type: "uuid",
                required: false,
                dbColumn: "active_organization_id"
            },
            activeConversationId: {
                value: activeConversationId,
                type: "uuid",
                required: false,
                dbColumn: "active_conversation_id"
            }
        };
    }
}

export class OrganizationRoleModel extends SupabaseModel {
    static TABLE_NAME = "organization_role";

    constructor(args) {
        super();
        const {
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
            seniority: {
                value: seniority,
                type: "number",
                required: true,
                dbColumn: "seniority"
            },
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
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
                required: false,
                dbColumn: "organization_id"
            }
        };
    }
}

export class OrganizationTeamModel extends SupabaseModel {
    static TABLE_NAME = "organization_team";

    constructor(args) {
        super();
        const {
            id = null,
            name,
            metadata = null,
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
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
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
                required: false,
                dbColumn: "organization_id"
            }
        };
    }
}

export class OrganizationTeamMembersModel extends SupabaseModel {
    static TABLE_NAME = "organization_team_members";

    constructor(args) {
        super();
        const {
            authId,
            userId,
            teamId,
            roleId,
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
            teamId: {
                value: teamId,
                type: "uuid",
                required: true,
                dbColumn: "team_id"
            },
            roleId: {
                value: roleId,
                type: "uuid",
                required: true,
                dbColumn: "role_id"
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
                required: false,
                dbColumn: "organization_id"
            }
        };
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
                authId: value.attributes.authId.value,
                teamId: value.attributes.teamId.value
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId.value,
                teamId: value.attributes.teamId.value
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId.value,
                teamId: value.attributes.teamId.value
            };
        }
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

export class OrganizationUsersModel extends SupabaseModel {
    static TABLE_NAME = "organization_users";

    constructor(args) {
        super();
        const {
            authId = null,
            userId = null,
            organizationId,
            metadata = null,
            isAdmin = false,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null
        } = args;
        this.attributes = {
            authId: {
                value: authId,
                type: "uuid",
                required: false,
                dbColumn: "auth_id"
            },
            userId: {
                value: userId,
                type: "uuid",
                required: false,
                dbColumn: "user_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: false,
                dbColumn: "organization_id"
            },
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
            },
            isAdmin: {
                value: isAdmin,
                type: "boolean",
                required: false,
                dbColumn: "is_admin"
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
            }
        };
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
                authId: value.attributes.authId.value,
                organizationId: value.attributes.organizationId.value
            };
        }
        return super.fetchFromSupabase(supabase, value, idColumn);
    }

    static async existsInSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId.value,
                organizationId: value.attributes.organizationId.value
            };
        }
        return super.existsInSupabase(supabase, value, idColumn);
    }

    static async deleteFromSupabase(supabase, value = null, idColumn = null) {
        if (value instanceof this) {
            value = {
                authId: value.attributes.authId.value,
                organizationId: value.attributes.organizationId.value
            };
        }
        return super.deleteFromSupabase(supabase, value, idColumn);
    }
}

export class OrganizationsModel extends SupabaseModel {
    static TABLE_NAME = "organizations";

    constructor(args) {
        super();
        const {
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
                required: false,
                dbColumn: "name"
            },
            website: {
                value: website,
                type: "string",
                required: false,
                dbColumn: "website"
            },
            logo: {
                value: logo,
                type: "string",
                required: false,
                dbColumn: "logo"
            },
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
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
            }
        };
    }
}
