// models/UserInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import { UserData } from "./data/UserDataInterfaces";
import { OrganizationsModel } from "./supabase/organization";
import {
    UserProfile,
    OrganizationUsers,
    OrganizationTeam,
    OrganizationRole
} from "./supabase/organizationInterfaces";

export interface User {
    supabase: SupabaseClient;
    model: UserData | null;
    authId: string;
    _organizationDict: Record<string, OrganizationsModel>;
    _initializeTask: Promise<void> | null;

    // Getters
    readonly isInitialized: boolean;
    readonly userId: string;
    readonly accountDisabled: boolean;
    readonly activeOrganizationId: string;
    readonly activeConversationId: string;
    readonly organizationAccessDisabled: boolean;
    readonly isAdmin: boolean;
    readonly profile: UserProfile;
    readonly organizationUser: OrganizationUsers;
    readonly organization: OrganizationsModel;
    readonly teams: OrganizationTeam[];
    readonly roles: OrganizationRole[];
    readonly memberships: OrganizationUsers[];

    // Methods acting as setters
    setActiveOrganization(organizationId: string): Promise<void>;
    setActiveConversation(conversationId: string): Promise<void>;

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

    listen(callback: (model: User, ...args: unknown[]) => boolean | void): this;
    notifyListeners(...args: unknown[]): void;
}

export interface GetCurrentUserParams {
    supabase: SupabaseClient;
}
