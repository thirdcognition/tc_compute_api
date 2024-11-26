import { SupabaseClient } from "@supabase/supabase-js";
import { SupabaseModel } from "./SupabaseModelInterface";

export interface UserProfile extends SupabaseModel<UserProfile> {
    id?: string;
    authId?: string;
    email?: string;
    name?: string;
    profilePicture?: string;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    activeOrganizationId?: string;
    activeConversationId?: string;
}

export interface OrganizationRole extends SupabaseModel<OrganizationRole> {
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

export interface OrganizationTeam extends SupabaseModel<OrganizationTeam> {
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

export interface OrganizationTeamMembers
    extends SupabaseModel<OrganizationTeamMembers> {
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

export interface OrganizationUsers extends SupabaseModel<OrganizationUsers> {
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
}

export interface Organizations extends SupabaseModel<Organizations> {
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
