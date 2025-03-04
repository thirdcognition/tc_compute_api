import "server-only";
import { UserOrganizationRequestData } from "../models/data/userData.js";
import { ApiConfig, fetchWithAuth } from "../helpers/ApiHelper.js";
import {
    UserProfileModel,
    OrganizationUsersModel
} from "../models/supabase/organization.js";

const CreateUserAPI = {
    convertToCreateOrganizationUserRequestData(requestData) {
        return {
            email: requestData.email,
            auth_id: requestData.authId,
            metadata: requestData.metadata,
            is_admin: requestData.isAdmin
        };
    },

    async createUser(organizationId, requestData, apiConfig) {
        if (!(requestData instanceof UserOrganizationRequestData)) {
            throw new Error(
                "requestData must be an instance of UserOrganizationRequestData"
            );
        }

        if (!(apiConfig instanceof ApiConfig)) {
            throw new Error("apiConfig must be an instance of ApiConfig");
        }

        const convertedData =
            this.convertToCreateOrganizationUserRequestData(requestData);

        return await fetchWithAuth(
            apiConfig,
            `/organization/${organizationId}/user`,
            "POST",
            convertedData
        );
    },

    async createOrganizationUser(
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
                const userData = await this.createUser(
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
                const userData = await this.createUser(
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
            const organizationUser = await this.createUser(
                organizationId,
                requestData,
                apiConfig
            );
            return new OrganizationUsersModel(organizationUser);
        }
    }
};

export default CreateUserAPI;
