export declare class UrlResult {
    orig_url?: string | null;
    resolved_url?: string | null;
    title?: string | null;
    source?: string | null;
    description?: string | null;
    image?: string | null;
    image_data?: Array<Record<string, unknown>> | null;
    publish_date?: Date | null;
    categories?: string[] | null;
    lang?: string | null;
    original_content?: string | null;
    metadata?: string | null;
    human_readable_content?: string | null;

    /**
     * String representation of the UrlResult instance.
     * @returns {string} String representation.
     */
    toString(): string;
}
