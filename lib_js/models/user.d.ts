// models/UserInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import {
    UserData,
    UserAvatarData,
    UserPreferencesData
} from "./structures/userData";
import {
    OrganizationsModel,
    UserProfileModel,
    UserDataModel,
    OrganizationUsersModel,
    OrganizationTeamModel,
    OrganizationRoleModel
} from "./supabase/organization";
import { NotifierModel } from "./prototypes/notifierModel";

declare class User extends NotifierModel<User> {
    supabase: SupabaseClient;
    model: UserData | null;
    authId: string;
    _organizationDict: Record<string, OrganizationsModel>;
    _initializeTask: Promise<void> | null;
    _avatar: UserAvatarData | null;
    _preferences: UserPreferencesData | null;

    // Getters
    readonly isInitialized: boolean;
    readonly userId: string;
    readonly accountDisabled: boolean;
    readonly activeOrganizationId: string;
    readonly activeConversationId: string;
    readonly activePanelId: string;
    readonly organizationAccessDisabled: boolean;
    readonly isAdmin: boolean;
    readonly avatar: UserAvatarData;
    readonly preferences: UserPreferencesData;
    readonly profile: UserProfileModel;
    readonly organizationUser: OrganizationUsersModel;
    readonly organization: OrganizationsModel;
    readonly teams: OrganizationTeamModel[];
    readonly roles: OrganizationRoleModel[];
    readonly memberships: OrganizationUsersModel[];

    // Methods acting as setters
    setActiveOrganization(organizationId: string): Promise<void>;
    setActiveConversation(conversationId: string): Promise<void>;
    setActivePanel(panelId: string): Promise<void>;
    setAvatar(newAvatar: UserAvatarData): Promise<void>;
    setPreferences(newPreferences: UserPreferencesData): Promise<void>;

    // Methods
    initialize(): Promise<void>;
    connectToOrganization(
        organization: OrganizationsModel,
        setAsAdmin?: boolean | null,
        updateExisting?: boolean
    ): Promise<void>;
    _initOrganizations(
        refresh?: boolean
    ): Promise<Record<string, OrganizationsModel>>;
    getOrganizationById(organizationId: string): Promise<OrganizationsModel>;
    fetchAclGroups(refresh?: boolean): Promise<void>;
    hasAccessToItem(itemId: string, itemType: string): Promise<boolean>;

    // New Getters
    getOrganization(): Promise<OrganizationsModel>;
    getTeams(): Promise<OrganizationTeamModel[]>;
    getRoles(): Promise<OrganizationRoleModel[]>;
    getMemberships(): Promise<OrganizationUsersModel[]>;

    // New Methods for UserData
    getUserData(refresh?: boolean): Promise<UserDataModel[]>;
    updateUserData(userDataItem: UserDataModel): Promise<UserDataModel>;
    matchUserData(filters: Partial<UserDataModel>): Promise<UserDataModel[]>;
}

declare class GetCurrentUserParams {
    supabase: SupabaseClient;
}
