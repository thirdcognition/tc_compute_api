/**
 * TypeScript interface representing the structure of a UrlResult.
 */
export interface UrlResult {
    origUrl?: string | null;
    resolvedUrl?: string | null;
    title?: string | null;
    source?: string | null;
    description?: string | null;
    image?: string | null;
    imageData?: Array<Record<string, unknown>> | null;
    publishDate?: Date | null;
    categories?: string[] | null;
    lang?: string | null;
    originalContent?: string | null;
    metadata?: string | null;
    humanReadableContent?: string | null;

    /**
     * Convert the UrlResult instance to a snake_case object.
     * @returns {Object} Snake_case representation of the UrlResult.
     */
    toSnakeCase(): object;

    /**
     * String representation of the UrlResult instance.
     * @returns {string} String representation.
     */
    toString(): string;
}
