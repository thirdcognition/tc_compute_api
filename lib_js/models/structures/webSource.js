import { SourceModel } from "../supabase/sources.js";

import { UrlResult } from "./urlResult.js";
import { NewsArticle } from "./newsArticle.js";

export const ResolveState = {
    FAILED: "failed",
    RESOLVED: "resolved",
    UNRESOLVED: "unresolved"
};

export class WebSource {
    constructor({
        title,
        originalSource,
        resolvedSource = null,
        source,
        rssSource = null,
        sourceId = null,
        description = null,
        originalContent = null,
        image = null,
        publishDate = null,
        categories = [],
        linkedItems = [],
        lang = null,
        metadata = null,
        ownerId = null,
        organizationId = null,
        urlResult = null,
        article = null,
        resolveState = ResolveState.UNRESOLVED
    }) {
        this.title = title;
        this.originalSource = originalSource;
        this.resolvedSource = resolvedSource;
        this.source = source;
        this.rssSource = rssSource;
        this.sourceId = sourceId;
        this.description = description;
        this.originalContent = originalContent;
        this.image = image;
        this.publishDate = publishDate;
        this.categories = categories;
        this.linkedItems = linkedItems;
        this.lang = lang;
        this.metadata = metadata;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.urlResult = urlResult ? new UrlResult(urlResult) : null;
        this.article = article ? new NewsArticle(article) : null;
        this.resolveState = resolveState;
    }

    /**
     * Update the WebSource instance based on the provided object.
     * Handles snake_case for SourceModel data and metadata only.
     * @param {UrlResult | NewsArticle | SourceModel} obj - The object to update from.
     */
    updateFrom(obj) {
        if (obj instanceof UrlResult) {
            this.title = obj.title || this.title;
            this.image = obj.image || this.image;
            this.description = obj.description || this.description;
            this.lang = obj.lang || this.lang;
            this.categories = obj.categories || this.categories;
            this.originalContent =
                obj.humanReadableContent || this.originalContent;
            this.resolvedSource = obj.resolvedUrl || this.resolvedSource;
            this.source = obj.source || this.source;
            this.publishDate = obj.publishDate || this.publishDate;
            this.metadata = obj.metadata || this.metadata;
            this.resolveState = ResolveState.RESOLVED;
        } else if (obj instanceof NewsArticle) {
            this.title = obj.title || this.title;
            if (this._verifyImage(obj.image)) {
                this.image = obj.image || this.image;
            }
            this.description = obj.description || this.description;
            this.lang = obj.lang || this.lang;
            this.categories = Array.isArray(obj.categories)
                ? obj.categories
                : this.categories;
            this.resolveState = ResolveState.RESOLVED;
        } else if (obj instanceof SourceModel) {
            this.resolvedSource = obj.resolved_source || this.resolvedSource;
            this.source = obj.data?.source || this.source;
            this.rssSource = obj.data?.rss_source || this.rssSource;
            this.linkedItems = obj.data?.linked_items || this.linkedItems;
            this.title = obj.title || this.title;
            this.image = obj.metadata?.image || this.image;
            this.description = obj.data?.description || this.description;
            this.lang = obj.lang || this.lang;
            this.categories = obj.data?.categories || this.categories;
            this.originalContent =
                obj.data?.original_content || this.originalContent;
            this.publishDate = obj.metadata?.publish_date
                ? new Date(obj.metadata.publish_date)
                : this.publishDate;
            this.sourceId = obj.id || this.sourceId;
            this.ownerId = obj.owner_id || this.ownerId;
            this.organizationId = obj.organization_id || this.organizationId;
            if (obj.data?.url_result) {
                this.urlResult = new UrlResult(obj.data.url_result);
            }
            if (obj.data?.article) {
                this.article = new NewsArticle(obj.data.article);
            }
            this.resolveState = obj.data?.resolve_state
                ? ResolveState[obj.data.resolve_state.toUpperCase()] ||
                  ResolveState.UNRESOLVED
                : this.resolveState;
        } else {
            throw new Error(`Unsupported object type: ${typeof obj}`);
        }
    }

    /**
     * Verify if the provided image exists in the UrlResult fields.
     * @param {string} articleImage - The image to verify.
     * @returns {boolean} True if the image exists, false otherwise.
     */
    _verifyImage(articleImage) {
        if (!this.urlResult || !articleImage) {
            return false;
        }
        return [
            this.urlResult.image,
            this.urlResult.metadata,
            this.urlResult.originalContent,
            this.urlResult.humanReadableContent
        ].some((field) => field && field.includes(articleImage));
    }

    getUrl() {
        return this.resolvedSource || this.originalSource || null;
    }

    findMatch(searchId) {
        const cleanedId = searchId.trim();
        if (
            this.shortId(this.title) === cleanedId ||
            this.sourceId === cleanedId
        ) {
            return this;
        }
        return null;
    }

    shortId() {
        if (this.sourceId) {
            return this.sourceId.split("-")[0];
        } else if (this.title) {
            return crypto
                .createHash("sha256")
                .update(this.title)
                .digest("hex")
                .slice(0, 8);
        }
        return "unknown_id";
    }

    async loadFromSupabase(supabase) {
        const result = await SourceModel.fetchFromSupabase(supabase, {
            value: this.originalSource,
            idColumn: "original_source"
        });
        if (result) {
            this.sourceModel = result;
            this.updateFrom(result);
        }
    }
}
