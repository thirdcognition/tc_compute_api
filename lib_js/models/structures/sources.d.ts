/**
 * Enumeration for Google News feed types.
 */
export enum GooglenewsFeedType {
    SEARCH = "search",
    TOPIC = "topic",
    TOP_TOPICS = "top_topics",
    LOCATION = "location"
}

/**
 * Interface representing the structure and methods of a GoogleNewsConfig.
 */
declare class GoogleNewsConfig {
    feed_type?: GooglenewsFeedType | null;
    lang?: string;
    country?: string;
    topic?: string | string[] | null;
    query?: string | null;
    location?: string | string[] | null;
    since?: string;
    articles?: number | null;
}

/**
 * Enumeration for Hacker News feed types.
 */
export enum HackerNewsFeedType {
    NEWEST = "newest",
    NEWCOMMENTS = "newcomments",
    FRONT_PAGE = "frontpage",
    BEST_COMMENTS = "bestcomments",
    ASK = "ask",
    SHOW = "show",
    POLLS = "polls",
    JOBS = "jobs",
    WHOISHIRING = "whoishiring"
}

/**
 * Interface representing the structure and methods of a HackerNewsConfig.
 */
declare class HackerNewsConfig {
    feed_type: HackerNewsFeedType;
    query?: string | null;
    points?: number | null;
    comments?: number | null;
    articles?: number | null;
}

/**
 * Interface representing the structure and methods of a TechCrunchNewsConfig.
 */
declare class TechCrunchNewsConfig {
    articles?: number | null;
}

/**
 * Enumeration for Yle feed types.
 */
export enum YleFeedType {
    MAJOR_HEADLINES = "majorHeadlines",
    MOST_READ = "mostRead",
    TOPICS = "topics"
}

/**
 * Enumeration for Yle languages.
 */
export enum YleLanguage {
    EN = "en",
    FI = "fi"
}

/**
 * Interface representing the structure and methods of a YleNewsConfig.
 */
declare class YleNewsConfig {
    feed_type?: YleFeedType | null;
    type?: YleFeedType | null;
    articles?: number | null;
    topics?: string[] | null;
    locations?: string[] | null;
    lang?: YleLanguage;
}
