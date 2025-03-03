// models/data/UserDataInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import {
    UserProfile,
    Organizations,
    OrganizationTeam,
    OrganizationRole,
    OrganizationTeamMembers,
    OrganizationUsers,
    UserData as UserDataModel
} from "../supabase/organizationInterfaces";
import { ACLGroupUsers, ACLGroup } from "../supabase/aclInterfaces";

export interface UserAvatarData {
    email: string | null;
    name: string | null;
    profilePicture: string | null;
}

export interface UserPreferencesData {
    lang: string | null;
    metadata: Record<string, unknown> | null;
    preferences: Record<string, unknown> | null;
    paymentDetails: Record<string, unknown> | null;
}

export interface UserOrganizationRequestData {
    email: string | null;
    authId: string | null;
    metadata: Record<string, unknown>;
    isAdmin: boolean;
}

export interface UserData {
    authId: string;
    supabase: SupabaseClient;
    profile: UserProfile | null;
    organizations: Organizations[] | null;
    teams: Record<string, OrganizationTeam[]> | null;
    roles: Record<string, OrganizationRole[]> | null;
    memberships: Record<string, OrganizationTeamMembers[]> | null;
    asUser: Record<string, OrganizationUsers> | null;
    userInAclGroup: ACLGroupUsers[] | null;
    aclGroup: ACLGroup[] | null;
    userData: UserDataModel[] | null;

    // Methods
    saveAllToSupabase(): Promise<void>;
    fetchUserProfile(refresh?: boolean): Promise<UserProfile | null>;
    fetchOrganizations(refresh?: boolean): Promise<Organizations[]>;
    fetchTeams(refresh?: boolean): Promise<Record<string, OrganizationTeam[]>>;
    fetchRoles(refresh?: boolean): Promise<Record<string, OrganizationRole[]>>;
    fetchMemberships(
        refresh?: boolean
    ): Promise<Record<string, OrganizationTeamMembers[]>>;
    fetchAsUser(refresh?: boolean): Promise<Record<string, OrganizationUsers>>;
    fetchAcl(refresh?: boolean): Promise<ACLGroupUsers[]>;
    inAclGroup(aclGroupId: string): Promise<boolean>;
    hasAccessToItem(itemId: string, itemType: string): Promise<boolean>;
    connectWithAclGroup(
        organizationId: string,
        aclGroupId: string,
        acl: string
    ): Promise<void>;
    disconnectFromAclGroup(
        organizationId: string,
        aclGroupId: string
    ): Promise<void>;
    getTeamsByOrganization(organizationId: string): Promise<OrganizationTeam[]>;
    getRolesByOrganization(organizationId: string): Promise<OrganizationRole[]>;
    getMembershipsByOrganization(
        organizationId: string
    ): Promise<OrganizationTeamMembers[]>;
    inOrganization(organizationId: string): Promise<boolean>;
    isAdminInOrganization(organizationId: string): Promise<boolean>;

    listen(
        callback: (model: UserData, ...args: unknown[]) => boolean | void
    ): this;
    notifyListeners(...args: unknown[]): void;

    // New Methods for UserData
    fetchUserData(refresh?: boolean): Promise<UserDataModel[]>;
    defineUserData(
        userDataItem: UserDataModel,
        replace?: boolean
    ): Promise<UserDataModel>;
    matchUserData(filters: Partial<UserDataModel>): Promise<UserDataModel[]>;
}
