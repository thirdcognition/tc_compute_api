// tc_api/CreateUserInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import { ApiConfig } from "../helpers/ApiHelper";
import { UserOrganizationRequestData } from "../models/structures/userData";

export declare class CreateUserParams {
    organizationId: string;
    requestData: UserOrganizationRequestData;
    apiConfig: ApiConfig;
}

export declare class CreateOrganizationUserParams {
    supabase: SupabaseClient;
    organizationId: string;
    requestData: UserOrganizationRequestData;
    apiConfig: ApiConfig;
}

export declare class ConvertToCreateOrganizationUserRequestDataParams {
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
declare const CreateUserAPI: {
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
};

export default CreateUserAPI;
