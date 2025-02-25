import { WebSource } from "./webSource.js";
import { SourceModel, SourceRelationshipModel } from "../supabase/sources.js";

export class WebSourceCollection {
    constructor({
        webSources = [],
        sourceModel = null,
        relationships = [],
        title = null,
        description = null,
        categories = [],
        maxAmount = null,
        mainItem = false,
        image = null,
        publishDate = null,
        ownerId = null,
        organizationId = null,
        sourceId = null,
        lang = null,
        metadata = null
    }) {
        this.webSources = webSources;
        this.sourceModel = sourceModel;
        this.relationships = relationships;
        this.title = title;
        this.description = description;
        this.categories = categories;
        this.maxAmount = maxAmount;
        this.mainItem = mainItem;
        this.image = image;
        this.publishDate = publishDate;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.sourceId = sourceId;
        this.lang = lang;
        this.metadata = metadata;
    }

    shortId() {
        if (this.sourceModel && this.sourceModel.id) {
            return this.sourceModel.id.split("-")[0];
        } else if (this.title) {
            return crypto
                .createHash("sha256")
                .update(this.title)
                .digest("hex")
                .slice(0, 8);
        }
        return "unknown_id";
    }

    async loadFromSupabase(supabase, id) {
        const result = await SourceModel.fetchFromSupabase(supabase, {
            value: id,
            idColumn: "id"
        });

        if (!result) {
            throw new Error(`No collection found with ID: ${id}`);
        }

        // Save the sourceModel instance
        this.sourceModel = result;

        // Populate fields
        this.title = result.title || this.title;
        this.description = result.data?.description || this.description;
        this.categories = result.data?.categories || this.categories;
        this.image = result.data?.image || this.image;
        this.publishDate = result.metadata?.publishDate
            ? new Date(result.metadata.publishDate)
            : this.publishDate;
        this.ownerId = result.ownerId || this.ownerId;
        this.organizationId = result.organizationId || this.organizationId;
        this.sourceId = result.id || this.sourceId;
        this.maxAmount = result.data?.maxAmount || this.maxAmount;
        this.mainItem = result.data?.mainItem || this.mainItem;

        // Fetch relationships and populate webSources
        const relationships = await SourceRelationshipModel.fetchFromSupabase(
            supabase,
            { value: id, idColumn: "source_id" }
        );
        this.relationships = relationships;

        const linkedSources = [];
        for (const relationship of relationships) {
            const relatedSource = await SourceModel.fetchFromSupabase(
                supabase,
                { value: relationship.relatedSourceId, idColumn: "id" }
            );
            if (relatedSource) {
                linkedSources.push(new WebSource(relatedSource));
            }
        }
        this.webSources = linkedSources;
    }

    static async loadLinkedSourcesAsCollection(supabase, source) {
        const relationships = await SourceRelationshipModel.fetchFromSupabase(
            supabase,
            {
                value: source.sourceId || source,
                idColumn: "source_id"
            }
        );

        if (!relationships || relationships.length === 0) {
            return null;
        }

        const linkedSources = [];
        for (const relationship of relationships) {
            const relatedSource = await SourceModel.fetchFromSupabase(
                supabase,
                { value: relationship.relatedSourceId, idColumn: "id" }
            );
            if (relatedSource) {
                linkedSources.push(new WebSource(relatedSource));
            }
        }

        return new WebSourceCollection({
            webSources: linkedSources
        });
    }

    getUrl() {
        const urls = [];
        for (const source of this.webSources) {
            if (source.resolvedSource) {
                urls.push(source.resolvedSource);
            } else if (source.originalSource) {
                urls.push(source.originalSource);
            }
        }
        return urls;
    }

    findMatch(searchId) {
        const cleanedId = searchId.trim();
        if (this.sourceId === cleanedId) {
            return this;
        }

        for (const webSource of this.webSources) {
            if (webSource.sourceId === cleanedId) {
                return webSource;
            }
        }

        return null;
    }
}
