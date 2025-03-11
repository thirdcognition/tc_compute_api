import { SupabaseClient } from "@supabase/supabase-js";
import { WebSource, SourceMetadata } from "./webSource";
import { SourceModel, SourceRelationshipModel } from "../supabase/sources";

export declare class WebSourceCollection {
    sourceModel: SourceModel | null;
    relationships: SourceRelationshipModel[] | null;
    webSources: WebSource[];
    sourceId: string | null;
    title: string | null;
    description: string | null;
    categories: string[];
    maxAmount: number | null;
    mainItem: boolean;
    image: string | null;
    publishDate: Date | null;
    ownerId: string | null;
    organizationId: string | null;
    lang: string | null;
    metadata: SourceMetadata | null;

    constructor(params: {
        webSources?: WebSource[];
        sourceModel?: SourceModel | null;
        relationships?: SourceRelationshipModel[] | null;
        title?: string | null;
        description?: string | null;
        categories?: string[];
        maxAmount?: number | null;
        mainItem?: boolean;
        image?: string | null;
        publishDate?: Date | null;
        ownerId?: string | null;
        organizationId?: string | null;
        sourceId?: string | null;
        lang?: string | null;
        metadata?: SourceMetadata | null;
    });

    shortId(): string;
    loadFromSupabase(supabase: SupabaseClient, id: string): Promise<void>;
    loadLinkedSourcesAsCollection(
        supabase: SupabaseClient,
        source: string | WebSource
    ): Promise<WebSourceCollection | null>;
    getUrl(): string[];
    findMatch(searchId: string): WebSource | WebSourceCollection | null;
}
