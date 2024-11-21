import { v4 as uuidv4 } from "uuid";
import { UserData } from "./data/userData";
import { OrganizationUsersModel } from "./supabase/organization";

class User {
    constructor(supabase, authId, userData = null) {
        this.supabase = supabase;
        this.model = userData;
        this.authId = uuidv4(authId);
        this._organizationDict = {};
        this._initializeTask = null;
    }

    get isInitialized() {
        return this._initializeTask !== null && this._initializeTask.done;
    }

    async initialize() {
        if (this._initializeTask === null) {
            this._initializeTask = this._initialize();
        }
        await this._initializeTask;
    }

    async _initialize() {
        if (this.model === null) {
            this.model = new UserData(this.authId);
        }
        await this.model.fetchUserProfile();
        await this.model.fetchOrganizations();
    }

    async connectToOrganization(
        organization,
        setAsAdmin = null,
        updateExisting = false
    ) {
        if (this.model.asUser === null) {
            await this.model.fetchAsUser();
        }

        const isMember = organization.id in this.model.asUser;
        if (isMember) {
            if (setAsAdmin !== null && updateExisting) {
                this.model.asUser[organization.id].isAdmin = setAsAdmin;
            }
        } else {
            if (setAsAdmin === null) {
                setAsAdmin = false;
            }
            this.model.asUser[organization.id] = new OrganizationUsersModel(
                this.model.authId,
                organization.id,
                setAsAdmin
            );
        }
        this.model.saveAllToSupabase(this.supabase);
    }

    get userId() {
        return this.model.profile.id;
    }

    get accountDisabled() {
        return this.model.profile.disabled;
    }

    get activeOrganizationId() {
        return this.model.profile.activeOrganizationId;
    }

    async setActiveOrganization(organizationId) {
        if (organizationId in this.model.organizations) {
            this.model.profile.activeOrganizationId = organizationId;
            await this.model.profile.update(this.supabase);
        }
    }

    get activeConversationId() {
        return this.model.profile.activeConversationId;
    }

    async setActiveConversation(conversationId) {
        this.model.profile.activeConversationId = conversationId;
        await this.model.profile.update(this.supabase);
    }

    get organizationAccessDisabled() {
        return this.model.asUser[this.activeOrganizationId].disabled;
    }

    get isAdmin() {
        return this.model.asUser[this.activeOrganizationId].isAdmin;
    }

    get profile() {
        return this.model.profile;
    }

    get organizationUser() {
        return this.model.asUser[this.activeConversationId];
    }

    get organization() {
        return this.getOrganizationById(this.activeOrganizationId);
    }

    get teams() {
        return this.model.getTeamsByOrganization(this.activeOrganizationId);
    }

    get roles() {
        return this.model.getRolesByOrganization(this.activeOrganizationId);
    }

    get memberships() {
        return this.model.getMembershipsByOrganization(this.userId);
    }

    async _initOrganizations(refresh = false) {
        if (refresh || !this._organizationDict) {
            if (!this.model.organizations) {
                await this.model.fetchOrganizations();
            }
            if (!this._organizationDict) {
                this._organizationDict = {};
            }

            for (const organization of this.model.organizations) {
                this._organizationDict[organization.id] = organization;
            }

            for (const organizationId of Object.keys(this._organizationDict)) {
                if (
                    !this.model.organizations.some(
                        (org) => org.id === organizationId
                    )
                ) {
                    delete this._organizationDict[organizationId];
                }
            }
        }
        return this._organizationDict;
    }

    async getOrganizationById(organizationId) {
        if (!this._organizationDict) {
            await this._initOrganizations();
        }
        return this._organizationDict[organizationId];
    }

    async fetchAclGroups(refresh = false) {
        await this.model.fetchAclGroups(refresh);
    }

    async hasAccessToItem(itemId, itemType) {
        return await this.model.hasAccessToItem(itemId, itemType);
    }
}

async function getCurrentUser(supabase) {
    const session = await supabase.auth.getSession();
    const user = new User(supabase, session.user.id);

    if (!user.isInitialized) {
        await user.initialize();
    }

    return user;
}

export { User, getCurrentUser };
