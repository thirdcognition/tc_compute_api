import {
    UserProfileModel,
    OrganizationsModel,
    OrganizationTeamModel,
    OrganizationRoleModel,
    OrganizationTeamMembersModel,
    OrganizationUsersModel,
    UserDataModel
} from "../supabase/organization.js";
import {
    ACLGroupUsersModel,
    ACLGroupUsersWithItems,
    ACLGroupModel
} from "../supabase/acl.js";
import { NotifierModel } from "../prototypes/notifierModel.js";
import { rolesPerson1Options } from "../../../static/admin/src/js/options.js";

export class UserAvatarData {
    constructor(email = null, name = null, profilePicture = null) {
        this.email = email;
        this.name = name;
        this.profilePicture = profilePicture;
    }
}

export class UserPreferencesData {
    constructor(
        lang = null,
        metadata = null,
        preferences = null,
        paymentDetails = null
    ) {
        this.lang = lang;
        this.metadata = metadata;
        this.preferences = preferences;
        this.paymentDetails = paymentDetails;
    }
}

export class UserOrganizationRequestData {
    constructor(email = null, authId = null, metadata = null, isAdmin = false) {
        this.email = email;
        this.authId = authId;
        this.metadata = metadata;
        this.isAdmin = isAdmin;
    }
}

export class UserData extends NotifierModel {
    constructor(supabase, authId, userProfileData = null) {
        super();
        this.authId = authId;
        this.supabase = supabase;
        this.profile = userProfileData;
        this.organizations = null;
        this.teams = null;
        this.roles = null;
        this.memberships = null;
        this.asUser = null;
        this.userInAclGroup = null;
        this.aclGroup = null;
        this.userData = null; // To store fetched user_data
    }

    async saveAllToSupabase() {
        const profilesToUpsert = [];
        const organizationsToUpsert = [];
        const teamsToUpsert = [];
        const rolesToUpsert = [];
        const membershipsToUpsert = [];
        const usersToUpsert = [];

        if (this.profile) profilesToUpsert.push(this.profile);
        if (this.organizations)
            organizationsToUpsert.push(...this.organizations);
        if (this.teams)
            Object.values(this.teams).forEach((teams) =>
                teamsToUpsert.push(...teams)
            );
        if (this.roles)
            Object.values(this.roles).forEach((roles) =>
                rolesToUpsert.push(...roles)
            );
        if (this.memberships)
            Object.values(this.memberships).forEach((memberships) =>
                membershipsToUpsert.push(...memberships)
            );
        if (this.asUser) usersToUpsert.push(...Object.values(this.asUser));

        const upsertTasks = [];

        if (profilesToUpsert.length) {
            upsertTasks.push(
                profilesToUpsert[0].upsertToSupabase(
                    this.supabase,
                    profilesToUpsert
                )
            );
        }
        if (organizationsToUpsert.length) {
            upsertTasks.push(
                organizationsToUpsert[0].upsertToSupabase(
                    this.supabase,
                    organizationsToUpsert
                )
            );
        }
        if (teamsToUpsert.length) {
            upsertTasks.push(
                teamsToUpsert[0].upsertToSupabase(this.supabase, teamsToUpsert)
            );
        }
        if (rolesToUpsert.length) {
            upsertTasks.push(
                rolesToUpsert[0].upsertToSupabase(this.supabase, rolesToUpsert)
            );
        }
        if (membershipsToUpsert.length) {
            upsertTasks.push(
                membershipsToUpsert[0].upsertToSupabase(
                    this.supabase,
                    membershipsToUpsert
                )
            );
        }
        if (usersToUpsert.length) {
            upsertTasks.push(
                usersToUpsert[0].upsertToSupabase(this.supabase, usersToUpsert)
            );
        }

        await Promise.all(upsertTasks);
    }

    async fetchUserProfile(refresh = false) {
        if (!this.profile || refresh) {
            this.profile = await UserProfileModel.fetchFromSupabase(
                this.supabase,
                { auth_id: this.authId }
            );
            if (this.profile) {
                this.profile.listen(this.boundNotifyListeners);
            } else {
                // let retryCount = 1;
                // const retryProfile = setInterval(async () => {
                //     this.profile = await UserProfileModel.fetchFromSupabase(
                //         this.supabase,
                //         { auth_id: this.authId }
                //     );
                //     if (this.profile) {
                //         this.profile.listen(this.boundNotifyListeners);
                //         if (this.organizations.length == 0) {
                //             this.fetchOrganizations(refresh);
                //         }
                //         clearInterval(retryProfile);
                //     } else {
                //         console.log(
                //             "Retry profile init fail",
                //             this.authId,
                //             retryCount++
                //         );
                //     }
                // }, 500);
                console.log("Unable to initialize user profile", this.authId);
            }
        }
        return this.profile || null;
    }

    async fetchOrganizations(refresh = false) {
        if (!this.organizations || refresh) {
            const response = await this.supabase
                .from("organizations")
                .select("*, organization_users(auth_id)")
                .eq("organization_users.auth_id", this.authId);
            this.organizations = response.data.map((data) => {
                const org = new OrganizationsModel(data);
                org.listen(this.boundNotifyListeners);
                return org;
            });
        }
        return this.organizations;
    }

    async fetchTeams(refresh = false) {
        if (!this.teams || refresh) {
            if (!this.organizations) await this.fetchOrganizations();
            if (this.organizations) {
                this.teams = {};
                for (const organization of this.organizations) {
                    this.teams[organization.id] = (
                        await OrganizationTeamModel.fetchExistingFromSupabase(
                            this.supabase,
                            { organizationId: organization.id }
                        )
                    ).listen(this.boundNotifyListeners);
                }
            }
        }
        return this.teams;
    }

    async fetchRoles(refresh = false) {
        if (!this.roles || refresh) {
            if (!this.organizations) await this.fetchOrganizations();
            if (this.organizations) {
                this.roles = {};
                for (const organization of this.organizations) {
                    this.roles[organization.id] = (
                        await OrganizationRoleModel.fetchExistingFromSupabase(
                            this.supabase,
                            { organization_id: organization.id }
                        )
                    ).listen(this.boundNotifyListeners);
                }
            }
        }
        return this.roles;
    }

    async fetchMemberships(refresh = false) {
        if (!this.memberships || refresh) {
            this.memberships = {};
            const memberships = (
                await OrganizationTeamMembersModel.fetchExistingFromSupabase(
                    this.supabase,
                    { auth_id: this.authId }
                )
            ).listen(this.boundNotifyListeners);
            for (const membership of memberships) {
                const organizationId = membership.organizationId;
                if (!this.memberships[organizationId]) {
                    this.memberships[organizationId] = [];
                }
                this.memberships[organizationId].push(membership);
            }
        }
        return this.memberships;
    }

    async fetchAsUser(refresh = false) {
        if (!this.asUser || refresh) {
            this.asUser = {};
            const users = (
                await OrganizationUsersModel.fetchExistingFromSupabase(
                    this.supabase,
                    { auth_id: this.authId }
                )
            ).listen(this.boundNotifyListeners);
            for (const user of users) {
                this.asUser[user.organizationId] = user;
            }
        }
        return this.asUser;
    }

    async fetchAcl(refresh = false) {
        if (!this.userInAclGroup || refresh) {
            this.userInAclGroup = (
                await ACLGroupUsersModel.fetchExistingFromSupabase(
                    this.supabase,
                    { auth_id: this.authId }
                )
            ).listen(this.boundNotifyListeners);
            const aclGroupIds = this.userInAclGroup.map(
                (group) => group.aclGroupId
            );
            this.aclGroup = (
                await ACLGroupModel.fetchExistingFromSupabase(this.supabase, {
                    id: aclGroupIds
                })
            ).listen(this.boundNotifyListeners);
        }
        return this.userInAclGroup;
    }

    async inAclGroup(aclGroupId) {
        if (!this.userInAclGroup) await this.fetchAcl();
        return this.userInAclGroup.some(
            (group) => group.aclGroupId === aclGroupId
        );
    }

    async hasAccessToItem(itemId, itemType) {
        return await ACLGroupUsersWithItems.existsInSupabase(this.supabase, {
            authId: this.authId,
            itemId: itemId,
            itemType: itemType
        });
    }

    async connectWithAclGroup(organizationId, aclGroupId, acl) {
        await this.asUser[organizationId].connectWithAclGroup(
            this.supabase,
            aclGroupId,
            acl
        );
        await this.fetchAcl(true);
    }

    async disconnectFromAclGroup(organizationId, aclGroupId) {
        await this.asUser[organizationId].disconnectWithAclGroup(
            this.supabase,
            aclGroupId
        );
        await this.fetchAcl(true);
    }

    async getTeamsByOrganization(organizationId) {
        if (!this.teams) await this.fetchTeams();
        return this.teams[organizationId] || [];
    }

    async getRolesByOrganization(organizationId) {
        if (!this.roles) await this.fetchRoles();
        return this.roles[organizationId] || [];
    }

    async getMembershipsByOrganization(organizationId) {
        if (!this.memberships) await this.fetchMemberships();
        return this.memberships[organizationId] || [];
    }

    async inOrganization(organizationId) {
        if (!this.organizations) await this.fetchOrganizations();
        return this.organizations.some(
            (organization) => organization.id === organizationId
        );
    }

    async isAdminInOrganization(organizationId) {
        if (!this.organizations) await this.fetchOrganizations();
        if (!this.asUser) await this.fetchAsUser();

        if (
            this.organizations.some(
                (organization) =>
                    organization.id === organizationId &&
                    organization.ownerId === this.authId
            )
        ) {
            return true;
        }

        if (this.asUser[organizationId]) {
            return this.asUser[organizationId].isAdmin;
        }
        return false;
    }

    // New Methods for UserData
    async fetchUserData(refresh = false) {
        if (!this.userData || refresh) {
            this.userData = this.userData || [];
            const newUserData = await UserDataModel.fetchExistingFromSupabase(
                this.supabase,
                { authId: this.authId }
            );
            const existingDataMap = new Map(
                this.userData.map((instance) => [instance.id, instance])
            );

            newUserData.forEach((newInstance) => {
                if (existingDataMap.has(newInstance.id)) {
                    existingDataMap
                        .get(newInstance.id)
                        .updateFromInstance(newInstance);
                } else {
                    this.userData.push(newInstance);
                    newInstance.listen(this.boundNotifyListeners);
                }
            });
            const newUserDataIds = new Set(
                newUserData.map((instance) => instance.id)
            );
            this.userData = this.userData.filter((instance) =>
                newUserDataIds.has(instance.id)
            );
        }
        return this.userData;
    }

    async defineUserData(userDataItem, replace = false) {
        userDataItem.authId = this.authId;

        if (replace && !userDataItem.id) {
            const existingItems = await UserDataModel.fetchExistingFromSupabase(
                this.supabase,
                {
                    authId: this.authId,
                    item: userDataItem.item,
                    targetId: userDataItem.targetId
                }
            );

            if (existingItems.length > 0) {
                existingItems.sort(
                    (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
                );
                userDataItem.id = existingItems[0].id;
            }
        }

        const item = await userDataItem.create(this.supabase);
        if (this.userData) {
            const existingItemIndex = this.userData.findIndex(
                (existingItem) => existingItem.id === item.id
            );

            if (existingItemIndex > -1) {
                this.userData[existingItemIndex] = item;
            } else {
                this.userData.push(item);
            }
        }
        return item;
    }

    async matchUserData(filters, refresh = false) {
        if (!this.userData) {
            await this.fetchUserData(refresh);
        }

        return this.userData.filter((userDataItem) =>
            Object.entries(filters).every(
                ([key, value]) => userDataItem[key] === value
            )
        );
    }
}
