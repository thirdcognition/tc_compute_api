// models/UserInterfaces.ts

import { SupabaseClient } from "@supabase/supabase-js";
import { UserData } from "./data/UserDataInterfaces";
import { OrganizationsModel } from "./supabase/organization";

export interface User {
    supabase: SupabaseClient;
    model: UserData | null;
    authId: string;
    _organizationDict: Record<string, OrganizationsModel>;
    _initializeTask: Promise<void> | null;
}

export interface GetCurrentUserParams {
    supabase: SupabaseClient;
}
