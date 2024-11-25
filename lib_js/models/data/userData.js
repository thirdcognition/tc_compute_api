import {
    UserProfileModel,
    OrganizationsModel,
    OrganizationTeamModel,
    OrganizationRoleModel,
    OrganizationTeamMembersModel,
    OrganizationUsersModel
} from "../supabase/organization.js";
import {
    ACLGroupUsersModel,
    ACLGroupUsersWithItems,
    ACLGroupModel
} from "../supabase/acl.js";
import { createUser } from "../../tc_api/createUser.js";

export class UserOrganizationRequestData {
    constructor(email = null, authId = null, metadata = null, isAdmin = false) {
        this.email = email;
        this.authId = authId;
        this.metadata = metadata;
        this.isAdmin = isAdmin;
    }
}

export class UserData {
    constructor(supabase, authId, userData = null) {
        this.authId = authId;
        this.supabase = supabase;
        this.profile = userData;
        this.organizations = null;
        this.teams = null;
        this.roles = null;
        this.memberships = null;
        this.asUser = null;
        this.userInAclGroup = null;
        this.aclGroup = null;
    }

    static async createOrganizationUser(
        supabase,
        organizationId,
        requestData,
        apiConfig
    ) {
        if (!(requestData instanceof UserOrganizationRequestData)) {
            throw new Error(
                "requestData must be an instance of UserOrganizationRequestData"
            );
        }

        let authId = null;
        let userProfile = null;

        if (requestData.email) {
            const userExists = await UserProfileModel.existsInSupabase(
                supabase,
                requestData.email,
                "email"
            );

            if (userExists) {
                userProfile = await UserProfileModel.fetchFromSupabase(
                    supabase,
                    requestData.email,
                    "email"
                );
                authId = userProfile.authId;
            } else {
                const userData = await createUser(
                    organizationId,
                    requestData,
                    apiConfig
                );
                authId = userData.id;
            }
        } else if (requestData.authId) {
            const userExists = await UserProfileModel.existsInSupabase(
                supabase,
                requestData.authId,
                "auth_id"
            );

            if (userExists) {
                userProfile = await UserProfileModel.fetchFromSupabase(
                    supabase,
                    requestData.authId,
                    "auth_id"
                );
                authId = requestData.authId;
            } else {
                const userData = await createUser(
                    organizationId,
                    requestData,
                    apiConfig
                );
                authId = userData.id;
            }
        } else {
            throw new Error("Either email or authId must be provided");
        }

        if (authId) {
            const userExistsInOrg =
                await OrganizationUsersModel.existsInSupabase(
                    supabase,
                    { auth_id: authId, organization_id: organizationId },
                    "auth_id"
                );

            if (userExistsInOrg) {
                throw new Error("User is already a member of the organization");
            } else {
                const organizationUser = new OrganizationUsersModel({
                    authId: authId,
                    organizationId: organizationId,
                    isAdmin: requestData.isAdmin,
                    userId: userProfile ? userProfile.id : null
                });
                await organizationUser.create(supabase);
                return organizationUser;
            }
        } else {
            const organizationUser = await createUser(
                organizationId,
                requestData,
                apiConfig
            );
            return new OrganizationUsersModel(organizationUser);
        }
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
        }
        return this.profile || null;
    }

    async fetchOrganizations(refresh = false) {
        if (!this.organizations || refresh) {
            const response = await this.supabase
                .from("organization_users")
                .select("organization_id, organizations(*)")
                .eq("auth_id", this.authId)
                .select();
            this.organizations = response.data.map(
                (data) => new OrganizationsModel(data)
            );
        }
        return this.organizations;
    }

    async fetchTeams(refresh = false) {
        if (!this.teams || refresh) {
            if (!this.organizations) await this.fetchOrganizations();
            if (this.organizations) {
                this.teams = {};
                for (const organization of this.organizations) {
                    this.teams[organization.id] =
                        await OrganizationTeamModel.fetchExistingFromSupabase(
                            this.supabase,
                            { organizationId: organization.id }
                        );
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
                    this.roles[organization.id] =
                        await OrganizationRoleModel.fetchExistingFromSupabase(
                            this.supabase,
                            { organization_id: organization.id }
                        );
                }
            }
        }
        return this.roles;
    }

    async fetchMemberships(refresh = false) {
        if (!this.memberships || refresh) {
            this.memberships = {};
            const memberships =
                await OrganizationTeamMembersModel.fetchExistingFromSupabase(
                    this.supabase,
                    { auth_id: this.authId }
                );
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
            const users =
                await OrganizationUsersModel.fetchExistingFromSupabase(
                    this.supabase,
                    { auth_id: this.authId }
                );
            for (const user of users) {
                this.asUser[user.organizationId] = user;
            }
        }
        return this.asUser;
    }

    async fetchAcl(refresh = false) {
        if (!this.userInAclGroup || refresh) {
            this.userInAclGroup =
                await ACLGroupUsersModel.fetchExistingFromSupabase(
                    this.supabase,
                    { auth_id: this.authId }
                );
            const aclGroupIds = this.userInAclGroup.map(
                (group) => group.aclGroupId
            );
            this.aclGroup = await ACLGroupModel.fetchExistingFromSupabase(
                this.supabase,
                { id: aclGroupIds }
            );
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
}
