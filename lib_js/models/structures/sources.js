/**
 * Enumeration for Google News feed types.
 */
export const GooglenewsFeedType = {
    SEARCH: "search",
    TOPIC: "topic",
    TOP_TOPICS: "top_topics",
    LOCATION: "location"
};

/**
 * GoogleNewsConfig class representing the configuration for Google News.
 */
export class GoogleNewsConfig {
    constructor({
        feed_type = null,
        lang = "en",
        country = "US",
        topic = null,
        query = null,
        location = null,
        since = "1d",
        articles = null
    } = {}) {
        this.feed_type = feed_type;
        this.lang = lang;
        this.country = country;
        this.topic = topic;
        this.query = query;
        this.location = location;
        this.since = since;
        this.articles = articles;
    }
}

/**
 * Enumeration for Hacker News feed types.
 */
export const HackerNewsFeedType = {
    NEWEST: "newest",
    NEWCOMMENTS: "newcomments",
    FRONT_PAGE: "frontpage",
    BEST_COMMENTS: "bestcomments",
    ASK: "ask",
    SHOW: "show",
    POLLS: "polls",
    JOBS: "jobs",
    WHOISHIRING: "whoishiring"
};

/**
 * HackerNewsConfig class representing the configuration for Hacker News.
 */
export class HackerNewsConfig {
    constructor({
        feed_type,
        query = null,
        points = null,
        comments = null,
        articles = null
    } = {}) {
        this.feed_type = feed_type;
        this.query = query;
        this.points = points;
        this.comments = comments;
        this.articles = articles;
    }
}

/**
 * TechCrunchNewsConfig class representing the configuration for TechCrunch News.
 */
export class TechCrunchNewsConfig {
    constructor({ articles = null } = {}) {
        this.articles = articles;
    }
}

/**
 * Enumeration for Yle feed types.
 */
export const YleFeedType = {
    MAJOR_HEADLINES: "majorHeadlines",
    MOST_READ: "mostRead",
    TOPICS: "topics"
};

/**
 * Enumeration for Yle languages.
 */
export const YleLanguage = {
    EN: "en",
    FI: "fi"
};

/**
 * YleNewsConfig class representing the configuration for Yle News.
 */
export class YleNewsConfig {
    constructor({
        feed_type = null,
        type = null,
        articles = null,
        topics = null,
        locations = null,
        lang = YleLanguage.FI
    } = {}) {
        this.feed_type = feed_type;
        this.type = type;
        this.articles = articles;
        this.topics = topics;
        this.locations = locations;
        this.lang = lang;
    }
}
