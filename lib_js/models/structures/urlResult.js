export class UrlResult {
    constructor(data) {
        this.orig_url = data.orig_url || data.origUrl || null;
        this.resolved_url = data.resolved_url || data.resolvedUrl || null;
        this.title = data.title || null;
        this.source = data.source || null;
        this.description = data.description || null;
        this.image = data.image || null;
        this.image_data = data.image_data || data.imageData || null;
        this.publish_date = data.publish_date || data.publishDate || null;
        this.categories = data.categories || null;
        this.lang = data.lang || null;
        this.original_content =
            data.original_content || data.originalContent || null;
        this.metadata = data.metadata || null;
        this.human_readable_content =
            data.human_readable_content || data.humanReadableContent || null;
    }

    toString() {
        return `Original URL: ${this.orig_url}, Resolved URL: ${this.resolved_url}, Title: ${this.title}, Source: ${this.source}, Description: ${this.description}, Image: ${this.image}, Publish Date: ${this.publish_date}, Categories: ${this.categories}, Language: ${this.lang}`;
    }
}
