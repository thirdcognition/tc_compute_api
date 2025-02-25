/**
 * NewsArticle class representing a news article structure.
 */
export class NewsArticle {
    constructor({
        title,
        topic,
        subject = null,
        description,
        summary,
        article,
        lang,
        image = null,
        categories = []
    }) {
        this.title = title;
        this.topic = topic;
        this.subject = subject;
        this.description = description;
        this.summary = summary;
        this.article = article;
        this.lang = lang;
        this.image = image;
        this.categories = categories;
    }

    /**
     * String representation of the NewsArticle instance.
     * @returns {string} String representation.
     */
    toString() {
        return `NewsArticle:
Title: ${this.title}
Topic: ${this.topic}
Summary: ${this.summary}`;
    }
}
