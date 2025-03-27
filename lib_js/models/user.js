import { UserData } from "./structures/userData.js";
import { OrganizationUsersModel } from "./supabase/organization.js";
import { NotifierModel } from "./prototypes/notifierModel.js";

class User extends NotifierModel {
    constructor(supabase, authId, userData = null) {
        super();

        this.supabase = supabase;
        this.model = userData;
        this.authId = authId;
        this._organizationDict = {};
        this._initializeTask = null;
        this._avatar = null;
        this._preferences = null;
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

    get activePanelId() {
        return this.model.profile.activePanelId;
    }

    async setActivePanel(panelId) {
        this.model.profile.activePanelId = panelId;
        await this.model.profile.update(this.supabase);
    }

    get avatar() {
        if (!this._avatar) {
            this._avatar = {
                email: this.model.profile.email,
                name: this.model.profile.name,
                profilePicture: this.model.profile.profilePicture
            };
        }
        return this._avatar;
    }

    async setAvatar(newAvatar) {
        this.model.profile.email = newAvatar.email;
        this.model.profile.name = newAvatar.name;
        this.model.profile.profilePicture = newAvatar.profilePicture;
        this._avatar = newAvatar;
        await this.model.profile.update(this.supabase);
    }

    get preferences() {
        if (!this._preferences && this.model?.profile) {
            this._preferences = JSON.parse(
                JSON.stringify({
                    lang: this.model.profile.lang,
                    metadata: this.model.profile.metadata,
                    preferences: this.model.profile.preferences,
                    paymentDetails: this.model.profile.paymentDetails,
                    notificationData: this.model.profile.notificationData
                })
            );
        }
        return this._preferences;
    }

    async setPreferences(newPreferences) {
        const clonedPreferences = JSON.parse(JSON.stringify(newPreferences));
        this.model.profile.lang = clonedPreferences.lang;
        this.model.profile.metadata = clonedPreferences.metadata;
        this.model.profile.preferences = clonedPreferences.preferences;
        this.model.profile.paymentDetails = clonedPreferences.paymentDetails;
        this.model.profile.notificationData =
            clonedPreferences.notificationData;
        this._preferences = clonedPreferences;
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

    // New Methods for UserData
    async getUserData(refresh = false) {
        return await this.model.fetchUserData(refresh);
    }

    async updateUserData(userDataItem) {
        return await this.model.defineUserData(userDataItem);
    }

    async matchUserData(filters) {
        return await this.model.matchUserData(filters);
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
