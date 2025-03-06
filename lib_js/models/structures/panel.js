/**
 * HostProfile class representing a host's profile.
 */
export class HostProfile {
    constructor({ name = "", persona = "", role = "" } = {}) {
        this.name = name;
        this.persona = persona;
        this.role = role;
    }
}

/**
 * ConversationConfig class representing the configuration for a conversation.
 */
export class ConversationConfig {
    constructor({
        output_language = "English",
        conversation_style = ["casual", "humorous"],
        roles_person1 = null,
        roles_person2 = null,
        dialogue_structure = null,
        engagement_techniques = null,
        user_instructions = null,
        podcast_name = "",
        podcast_tagline = "",
        creativity = 0.7,
        word_count = 200,
        longform = false,
        text_to_speech = {},
        location = "Finland"
    } = {}) {
        this.output_language = output_language;
        this.conversation_style = conversation_style;
        this.roles_person1 = roles_person1;
        this.roles_person2 = roles_person2;
        this.dialogue_structure = dialogue_structure;
        this.engagement_techniques = engagement_techniques;
        this.user_instructions = user_instructions;
        this.podcast_name = podcast_name;
        this.podcast_tagline = podcast_tagline;
        this.creativity = creativity;
        this.word_count = word_count;
        this.longform = longform;
        this.text_to_speech = text_to_speech;
        this.location = location;
    }
}

/**
 * PanelRequestData class representing the data for a panel request.
 */
export class PanelRequestData {
    constructor({
        title = "New public morning show",
        inputSource = "",
        inputText = "",
        ttsModel = "elevenlabs",
        longform = false,
        bucketName = "public_panels",
        displayTag = "",
        conversationConfig = new ConversationConfig(),
        panelId = null,
        transcriptParentId = null,
        transcriptId = null,
        googleNews = null,
        yleNews = null,
        techcrunchNews = null,
        hackernews = null,
        newsGuidance = null,
        newsItems = 5,
        segments = 5,
        languages = null,
        cronjob = null,
        ownerId = null,
        organizationId = null,
        isPublic = true
    } = {}) {
        this.title = title;
        this.inputSource = inputSource;
        this.inputText = inputText;
        this.ttsModel = ttsModel;
        this.longform = longform;
        this.bucketName = bucketName;
        this.displayTag = displayTag;
        this.conversationConfig = conversationConfig;
        this.panelId = panelId;
        this.transcriptParentId = transcriptParentId;
        this.transcriptId = transcriptId;
        this.googleNews = googleNews;
        this.yleNews = yleNews;
        this.techcrunchNews = techcrunchNews;
        this.hackernews = hackernews;
        this.newsGuidance = newsGuidance;
        this.newsItems = newsItems;
        this.segments = segments;
        this.languages = languages;
        this.cronjob = cronjob;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.isPublic = isPublic;
    }
}

export class SummaryReference {
    constructor({
        id = null,
        title,
        image = null,
        url = null,
        publish_date = null
    }) {
        this.id = id;
        this.title = title;
        this.image = image;
        this.url = url;
        this.publish_date = publish_date;
    }
}

/**
 * SummarySubject class representing a summary subject.
 */
export class SummarySubject {
    constructor({ title, description, references = [] } = {}) {
        this.title = title;
        this.description = description;
        this.references = references;
    }
}

/**
 * TranscriptSummary class representing a transcript summary.
 */
export class TranscriptSummary {
    constructor({ subjects = [], description, title } = {}) {
        this.subjects = subjects;
        this.description = description;
        this.title = title;
    }
}

export class PanelMetadata {
    constructor({
        title = null,
        input_source = null,
        input_text = null,
        tts_model = null,
        longform = null,
        display_tag = null,
        conversation_config = null,
        google_news = null,
        yle_news = null,
        techcrunch_news = null,
        hackernews = null,
        news_guidance = null,
        news_items = null,
        segments = null,
        languages = null,
        description = null
    } = {}) {
        this.title = title; // Optional title.
        this.input_source = input_source; // Optional input source (string or string array).
        this.input_text = input_text; // Optional input text.
        this.tts_model = tts_model; // Optional TTS model.
        this.longform = longform; // Optional boolean indicating if long-form content.
        this.display_tag = display_tag; // Optional display tag.
        this.conversation_config = conversation_config; // Optional conversation configuration.
        this.google_news = google_news; // Optional Google News configuration (single or array).
        this.yle_news = yle_news; // Optional Yle News configuration (single or array).
        this.techcrunch_news = techcrunch_news; // Optional TechCrunch News configuration (single or array).
        this.hackernews = hackernews; // Optional Hacker News configuration (single or array).
        this.news_guidance = news_guidance; // Optional news guidance.
        this.news_items = news_items; // Optional number of news items.
        this.segments = segments; // Optional number of segments.
        this.languages = languages; // Optional list of languages.
        this.description = description; // Optional description.
    }
}

export class TranscriptMetadata {
    constructor({
        images,
        longform,
        subjects,
        description,
        conversation_config
    }) {
        this.images = images; // List of image URLs.
        this.longform = longform; // Indicates if it's long-form content.
        this.subjects = subjects; // List of subjects with descriptions and references.
        this.description = description; // Summary of the segment's discussion.
        this.conversation_config = conversation_config; // Details for panel setup and dialogue.
    }
}

export class AudioMetadata {
    constructor({ tts_model = null, conversation_config = null } = {}) {
        this.tts_model = tts_model; // Optional TTS model.
        this.conversation_config = conversation_config; // Optional conversation configuration.
    }
}
