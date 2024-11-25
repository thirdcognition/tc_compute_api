import "server-only";
import { UserOrganizationRequestData } from "../models/data/userData.js";
import { ApiConfig, fetchWithAuth } from "../helpers/ApiHelper.js";

function convertToCreateOrganizationUserRequestData(requestData) {
    return {
        email: requestData.email,
        auth_id: requestData.authId,
        metadata: requestData.metadata,
        is_admin: requestData.isAdmin
    };
}

export async function createUser(organizationId, requestData, apiConfig) {
    if (!(requestData instanceof UserOrganizationRequestData)) {
        throw new Error(
            "requestData must be an instance of UserOrganizationRequestData"
        );
    }

    if (!(apiConfig instanceof ApiConfig)) {
        throw new Error("apiConfig must be an instance of ApiConfig");
    }

    const convertedData =
        convertToCreateOrganizationUserRequestData(requestData);

    return await fetchWithAuth(
        apiConfig,
        `/organization/${organizationId}/user`,
        "POST",
        convertedData
    );
}
