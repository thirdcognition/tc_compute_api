// tc_api/CreateUserInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import { ApiConfig } from "../helpers/ApiHelperInterfaces";
import { UserOrganizationRequestData } from "../models/structures/UserDataInterfaces";

export interface CreateUserParams {
    organizationId: string;
    requestData: UserOrganizationRequestData;
    apiConfig: ApiConfig;
}

export interface CreateOrganizationUserParams {
    supabase: SupabaseClient;
    organizationId: string;
    requestData: UserOrganizationRequestData;
    apiConfig: ApiConfig;
}

export interface ConvertToCreateOrganizationUserRequestDataParams {
    email: string;
    authId: string;
    metadata: Record<string, unknown>; // JSON object
    isAdmin: boolean;
}

export type CreateOrganizationUserRequestData = {
    email: string;
    auth_id: string;
    metadata: Record<string, unknown>; // JSON object
    is_admin: boolean;
};

/**
 * Interface for the CreateUserAPI object.
 */
export interface CreateUserAPI {
    convertToCreateOrganizationUserRequestData(
        requestData: ConvertToCreateOrganizationUserRequestDataParams
    ): CreateOrganizationUserRequestData;

    createUser(
        organizationId: string,
        requestData: UserOrganizationRequestData,
        apiConfig: ApiConfig
    ): Promise<unknown>;

    createOrganizationUser(
        supabase: SupabaseClient,
        organizationId: string,
        requestData: UserOrganizationRequestData,
        apiConfig: ApiConfig
    ): Promise<unknown>;
}
