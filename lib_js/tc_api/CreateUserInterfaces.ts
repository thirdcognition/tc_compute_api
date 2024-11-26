// tc_api/CreateUserInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import { ApiConfig } from "../helpers/ApiHelperInterfaces";
import { UserOrganizationRequestData } from "../models/data/UserDataInterfaces";

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
