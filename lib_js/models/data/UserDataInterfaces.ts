// models/data/UserDataInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import {
    UserProfileModel,
    OrganizationsModel,
    OrganizationTeamModel,
    OrganizationRoleModel,
    OrganizationTeamMembersModel,
    OrganizationUsersModel
} from "../supabase/organization";
import { ACLGroupUsersModel, ACLGroupModel } from "../supabase/acl";

export interface UserOrganizationRequestData {
    email: string | null;
    authId: string | null;
    metadata: Record<string, unknown>;
    isAdmin: boolean;
}

export interface UserData {
    authId: string;
    supabase: SupabaseClient;
    profile: UserProfileModel | null;
    organizations: OrganizationsModel[] | null;
    teams: Record<string, OrganizationTeamModel[]> | null;
    roles: Record<string, OrganizationRoleModel[]> | null;
    memberships: Record<string, OrganizationTeamMembersModel[]> | null;
    asUser: Record<string, OrganizationUsersModel> | null;
    userInAclGroup: ACLGroupUsersModel[] | null;
    aclGroup: ACLGroupModel[] | null;

    // Methods
    saveAllToSupabase(): Promise<void>;
    fetchUserProfile(refresh?: boolean): Promise<UserProfileModel | null>;
    fetchOrganizations(refresh?: boolean): Promise<OrganizationsModel[]>;
    fetchTeams(
        refresh?: boolean
    ): Promise<Record<string, OrganizationTeamModel[]>>;
    fetchRoles(
        refresh?: boolean
    ): Promise<Record<string, OrganizationRoleModel[]>>;
    fetchMemberships(
        refresh?: boolean
    ): Promise<Record<string, OrganizationTeamMembersModel[]>>;
    fetchAsUser(
        refresh?: boolean
    ): Promise<Record<string, OrganizationUsersModel>>;
    fetchAcl(refresh?: boolean): Promise<ACLGroupUsersModel[]>;
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
    getTeamsByOrganization(
        organizationId: string
    ): Promise<OrganizationTeamModel[]>;
    getRolesByOrganization(
        organizationId: string
    ): Promise<OrganizationRoleModel[]>;
    getMembershipsByOrganization(
        organizationId: string
    ): Promise<OrganizationTeamMembersModel[]>;
    inOrganization(organizationId: string): Promise<boolean>;
    isAdminInOrganization(organizationId: string): Promise<boolean>;

    listen(
        callback: (model: UserData, ...args: unknown[]) => boolean | void
    ): this;
    notifyListeners(...args: unknown[]): void;
}
