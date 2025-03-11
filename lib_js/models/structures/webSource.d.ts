import { SupabaseClient } from "@supabase/supabase-js";
import { UrlResult } from "./urlResult";
import { NewsArticle } from "./newsArticle";
import { SourceModel } from "../supabase/sources";

export enum ResolveState {
    FAILED = "failed",
    RESOLVED = "resolved",
    UNRESOLVED = "unresolved"
}

export declare class WebSource {
    title: string;
    originalSource: string;
    resolvedSource?: string | null;
    source: string;
    rssSource?: string | null;
    sourceId?: string | null;
    description?: string | null;
    originalContent?: string | null;
    image?: string | null;
    publishDate?: Date | null;
    categories?: string[];
    linkedItems?: string[]; // Assuming linked items are strings
    lang?: string | null;
    metadata?: {
        image: string | null;
        publishDate: string | null;
        children:
            | {
                  image: string | null;
                  title: string | null;
                  publishDate: string | null;
                  url: string | null;
                  source: string | null;
              }[]
            | null;
    };
    ownerId?: string | null;
    organizationId?: string | null;
    urlResult?: UrlResult | null;
    article?: NewsArticle | null;
    resolveState: ResolveState; // Add resolveState field

    /**
     * Update the WebSource instance based on the provided object.
     * @param obj - The object to update from (UrlResult, NewsArticle, or SourceModel).
     */
    updateFrom(obj: UrlResult | NewsArticle | SourceModel): void;

    /**
     * Verify if the provided image exists in the UrlResult fields.
     * @param articleImage - The image to verify.
     * @returns True if the image exists, false otherwise.
     */
    _verifyImage(articleImage: string): boolean;

    /**
     * Get the URL of the WebSource.
     * @returns The resolved or original source URL.
     */
    getUrl(): string | null;

    /**
     * Find a match for the given search ID.
     * @param searchId - The ID to search for.
     * @returns The matching WebSource instance, or null if not found.
     */
    findMatch(searchId: string): WebSource | null;

    /**
     * Generate a short ID for the WebSource.
     * @returns A short ID string.
     */
    shortId(): string;

    /**
     * Load the WebSource from Supabase.
     * @param supabase - The Supabase client instance.
     */
    loadFromSupabase(supabase: SupabaseClient): Promise<void>;
}
