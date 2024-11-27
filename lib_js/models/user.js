import { UserData } from "./data/userData.js";
import { OrganizationUsersModel } from "./supabase/organization.js";

class User {
    constructor(supabase, authId, userData = null) {
        this.listeners = [];
        this.boundNotifyListeners = (...args) => this.notifyListeners(...args);
        this.supabase = supabase;
        this.model = userData;
        this.authId = authId;
        this._organizationDict = {};
        this._initializeTask = null;
    }
    listen(callback) {
        if (
            typeof callback === "function" &&
            this.listeners.indexOf(callback) === -1
        ) {
            this.listeners.push(callback);
        }
        return this;
    }

    notifyListeners(...args) {
        this.listeners = this.listeners.filter(
            (listener) => listener(this, ...args) !== false
        );
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
            this.model = new UserData(this.supabase, this.authId).listen(
                this.boundNotifyListeners
            );
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
            ).listen(this.model.boundNotifyListeners);
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
        return this._organizationDict[this.activeOrganizationId];
    }

    async getOrganization() {
        return await this.getOrganizationById(this.activeOrganizationId);
    }

    async getTeams() {
        return await this.model.getTeamsByOrganization(
            this.activeOrganizationId
        );
    }

    async getRoles() {
        return await this.model.getRolesByOrganization(
            this.activeOrganizationId
        );
    }

    async getMemberships() {
        return await this.model.getMembershipsByOrganization(this.userId);
    }

    async _initOrganizations(refresh = false) {
        if (refresh || !this._organizationDict) {
            if (
                !this.model.organizations ||
                this.model.organizations.length === 0
            ) {
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
        if (
            Object.keys(this._organizationDict || {}).length === 0 ||
            !this._organizationDict[organizationId]
        ) {
            await this._initOrganizations(true);
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
