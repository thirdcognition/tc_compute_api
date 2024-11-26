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
}
