/**
 * TypeScript interface representing the structure and methods of a NewsArticle.
 */
export interface NewsArticle {
    title: string;
    topic: string;
    subject?: string | null;
    description: string;
    summary: string;
    article: string;
    lang: string;
    image?: string | null;
    categories?: string[];

    /**
     * Convert the NewsArticle instance to a JSON object.
     * @returns {Object} JSON representation of the NewsArticle.
     */
    toJSON(): object;

    /**
     * Create a NewsArticle instance from a JSON object.
     * @param {Object} json - JSON object to deserialize.
     * @returns {NewsArticle} A new NewsArticle instance.
     */
    fromJSON(json: object): NewsArticle;

    /**
     * String representation of the NewsArticle instance.
     * @returns {string} String representation.
     */
    toString(): string;
}
