/**
 * UrlResult class representing a URL result structure.
 */
export class UrlResult {
    constructor(data) {
        this.origUrl = data.orig_url || data.origUrl || null;
        this.resolvedUrl = data.resolved_url || data.resolvedUrl || null;
        this.title = data.title || null;
        this.source = data.source || null;
        this.description = data.description || null;
        this.image = data.image || null;
        this.imageData = data.image_data || data.imageData || null;
        this.publishDate = data.publish_date || data.publishDate || null;
        this.categories = data.categories || null;
        this.lang = data.lang || null;
        this.originalContent =
            data.original_content || data.originalContent || null;
        this.metadata = data.metadata || null;
        this.humanReadableContent =
            data.human_readable_content || data.humanReadableContent || null;
    }

    /**
     * Convert the UrlResult instance to a snake_case object.
     * @returns {Object} Snake_case representation of the UrlResult.
     */
    toSnakeCase() {
        return {
            orig_url: this.origUrl,
            resolved_url: this.resolvedUrl,
            title: this.title,
            source: this.source,
            description: this.description,
            image: this.image,
            image_data: this.imageData,
            publish_date: this.publishDate,
            categories: this.categories,
            lang: this.lang,
            original_content: this.originalContent,
            metadata: this.metadata,
            human_readable_content: this.humanReadableContent
        };
    }

    /**
     * String representation of the UrlResult instance.
     * @returns {string} String representation.
     */
    toString() {
        return `Original URL: ${this.orig_url}, Resolved URL: ${this.resolved_url}, Title: ${this.title}, Source: ${this.source}, Description: ${this.description}, Image: ${this.image}, Publish Date: ${this.publish_date}, Categories: ${this.categories}, Language: ${this.lang}`;
    }
}
