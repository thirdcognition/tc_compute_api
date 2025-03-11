import { SupabaseClient } from "@supabase/supabase-js";
import { SupabaseModel } from "./supabaseModel";

declare class UserProfileModel extends SupabaseModel<UserProfileModel> {
    id?: string;
    authId?: string;
    email?: string;
    name?: string;
    profilePicture?: string;
    metadata?: Record<string, unknown>;
    lang?: string;
    activePanelId?: string;
    preferences?: Record<string, unknown>;
    paymentDetails?: Record<string, unknown>;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    activeOrganizationId?: string;
    activeConversationId?: string;
}

declare class UserDataModel extends SupabaseModel<UserDataModel> {
    id?: string;
    authId?: string;
    item: string;
    targetId?: string;
    data?: Record<string, unknown>;
    createdAt?: Date;
    updatedAt?: Date;
}

declare class OrganizationRoleModel extends SupabaseModel<OrganizationRoleModel> {
    id?: string;
    name: string;
    description?: string;
    seniority: number;
    metadata?: Record<string, unknown>;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

declare class OrganizationTeamModel extends SupabaseModel<OrganizationTeamModel> {
    id?: string;
    name: string;
    metadata?: Record<string, unknown>;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

declare class OrganizationTeamMembersModel extends SupabaseModel<OrganizationTeamMembersModel> {
    authId: string;
    userId: string;
    teamId: string;
    roleId: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

declare class OrganizationUsersModel extends SupabaseModel<OrganizationUsersModel> {
    authId?: string;
    userId?: string;
    organizationId?: string;
    metadata?: Record<string, unknown>;
    isAdmin?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;

    inAclGroup(supabase: SupabaseClient, aclGroupId: string): Promise<boolean>;

    connectWithAclGroup(
        supabase: SupabaseClient,
        aclGroupId: string,
        acl: string
    ): Promise<void>;

    disconnectWithAclGroup(
        supabase: SupabaseClient,
        aclGroupId: string
    ): Promise<void>;

    create(
        supabase: SupabaseClient,
        groupsWithLevels?: Record<string, string>
    ): Promise<OrganizationUsersModel>;
}

declare class OrganizationsModel extends SupabaseModel<OrganizationsModel> {
    id?: string;
    defaultAclGroupId?: string;
    name?: string;
    website?: string;
    logo?: string;
    metadata?: Record<string, unknown>;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
}
