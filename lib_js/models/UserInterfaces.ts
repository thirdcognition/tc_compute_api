// models/UserInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import {
    UserData,
    UserAvatarData,
    UserPreferencesData
} from "./structures/UserDataInterfaces";
import {
    Organizations,
    UserProfile,
    UserData as UserDataModel,
    OrganizationUsers,
    OrganizationTeam,
    OrganizationRole
} from "./supabase/organizationInterfaces";

export interface User {
    supabase: SupabaseClient;
    model: UserData | null;
    authId: string;
    _organizationDict: Record<string, Organizations>;
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
    readonly profile: UserProfile;
    readonly organizationUser: OrganizationUsers;
    readonly organization: Organizations;
    readonly teams: OrganizationTeam[];
    readonly roles: OrganizationRole[];
    readonly memberships: OrganizationUsers[];

    // Methods acting as setters
    setActiveOrganization(organizationId: string): Promise<void>;
    setActiveConversation(conversationId: string): Promise<void>;
    setActivePanel(panelId: string): Promise<void>;
    setAvatar(newAvatar: UserAvatarData): Promise<void>;
    setPreferences(newPreferences: UserPreferencesData): Promise<void>;

    // Methods
    initialize(): Promise<void>;
    connectToOrganization(
        organization: Organizations,
        setAsAdmin?: boolean | null,
        updateExisting?: boolean
    ): Promise<void>;
    _initOrganizations(
        refresh?: boolean
    ): Promise<Record<string, Organizations>>;
    getOrganizationById(organizationId: string): Promise<Organizations>;
    fetchAclGroups(refresh?: boolean): Promise<void>;
    hasAccessToItem(itemId: string, itemType: string): Promise<boolean>;

    listen(callback: (model: User, ...args: unknown[]) => boolean | void): this;
    notifyListeners(...args: unknown[]): void;

    // New Getters
    getOrganization(): Promise<Organizations>;
    getTeams(): Promise<OrganizationTeam[]>;
    getRoles(): Promise<OrganizationRole[]>;
    getMemberships(): Promise<OrganizationUsers[]>;

    // New Methods for UserData
    getUserData(): Promise<UserDataModel[]>;
    updateUserData(userDataItem: UserDataModel): Promise<UserDataModel>;
    matchUserData(filters: Partial<UserDataModel>): Promise<UserDataModel[]>;
}

export interface GetCurrentUserParams {
    supabase: SupabaseClient;
}
