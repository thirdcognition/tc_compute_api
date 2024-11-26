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
