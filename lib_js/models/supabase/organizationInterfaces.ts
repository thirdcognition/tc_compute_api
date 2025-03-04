import { SupabaseClient } from "@supabase/supabase-js";
import { SupabaseModel } from "./SupabaseModelInterface";

export interface UserProfileModel extends SupabaseModel<UserProfileModel> {
    id?: string;
    authId?: string;
    email?: string;
    name?: string;
    profilePicture?: string;
    metadata?: object;
    lang?: string;
    activePanelId?: string;
    preferences?: object;
    paymentDetails?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    activeOrganizationId?: string;
    activeConversationId?: string;
}

export interface UserDataModel extends SupabaseModel<UserDataModel> {
    id?: string;
    authId?: string;
    item: string;
    targetId?: string;
    data?: object;
    createdAt?: Date;
    updatedAt?: Date;
}

export interface OrganizationRoleModel
    extends SupabaseModel<OrganizationRoleModel> {
    id?: string;
    name: string;
    description?: string;
    seniority: number;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

export interface OrganizationTeamModel
    extends SupabaseModel<OrganizationTeamModel> {
    id?: string;
    name: string;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface OrganizationTeamMembersModel
    extends SupabaseModel<OrganizationTeamMembersModel> {
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

export interface OrganizationUsersModel
    extends SupabaseModel<OrganizationUsersModel> {
    authId?: string;
    userId?: string;
    organizationId?: string;
    metadata?: object;
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

export interface OrganizationsModel extends SupabaseModel<OrganizationsModel> {
    id?: string;
    defaultAclGroupId?: string;
    name?: string;
    website?: string;
    logo?: string;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
}
