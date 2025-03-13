import { SupabaseClient } from "@supabase/supabase-js";
import { NotifierModel } from "../prototypes/notifierModel";

export declare class SupabaseModel<T> extends NotifierModel<T> {
    constructor(args: Record<string, unknown>);
    static saveToSupabase(
        supabase: SupabaseClient,
        instance: T,
        onConflict?: string[]
    ): Promise<T>;
    static upsertToSupabase(
        supabase: SupabaseClient,
        instances: T[],
        onConflict?: string[],
        idColumn?: string
    ): Promise<T[]>;
    static fetchFromSupabase(
        supabase: SupabaseClient,
        value?: Partial<T>,
        idColumn?: string
    ): Promise<T | null>;
    static fetchExistingFromSupabase(
        supabase: SupabaseClient,
        filter?: Partial<T>,
        values?: Partial<T>[],
        idColumn?: string
    ): Promise<T[]>;
    static existsInSupabase(
        supabase: SupabaseClient,
        value?: Partial<T>,
        idColumn?: string
    ): Promise<boolean>;
    static deleteFromSupabase(
        supabase: SupabaseClient,
        value?: Partial<T>,
        idColumn?: string
    ): Promise<boolean>;
    create(supabase: SupabaseClient): Promise<T>;
    read(supabase: SupabaseClient, idColumn?: string): Promise<T | null>;
    update(supabase: SupabaseClient): Promise<T>;
    delete(supabase: SupabaseClient, idColumn?: string): Promise<T>;
    exists(supabase: SupabaseClient, idColumn?: string): Promise<boolean>;
    updateFromInstance(instance: T): boolean;
}
