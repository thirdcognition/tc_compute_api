/**
 * HostProfile class representing a host's profile.
 */
export class HostProfile {
    constructor({
        name = "",
        persona = "",
        role = "",
        voice_config = undefined
    } = {}) {
        this.name = name;
        this.persona = persona;
        this.role = role;
        this.voice_config = voice_config;
    }
}

/**
 * ConversationConfig class representing the configuration for a conversation.
 */
export class ConversationConfig {
    constructor({
        output_language = "en",
        conversation_style = ["casual", "humorous"],
        person_roles = undefined,
        dialogue_structure = null,
        engagement_techniques = null,
        user_instructions = null,
        podcast_name = "",
        podcast_tagline = "",
        creativity = 0.7,
        word_count = 200,
        longform = false,
        location = "Finland",
        short_intro_and_conclusion = false,
        disable_intro_and_conclusion = false
    } = {}) {
        this.output_language = output_language;
        this.conversation_style = conversation_style;
        this.person_roles = person_roles;
        this.dialogue_structure = dialogue_structure;
        this.engagement_techniques = engagement_techniques;
        this.user_instructions = user_instructions;
        this.podcast_name = podcast_name;
        this.podcast_tagline = podcast_tagline;
        this.creativity = creativity;
        this.word_count = word_count;
        this.longform = longform;
        this.location = location;
        this.short_intro_and_conclusion = short_intro_and_conclusion;
        this.disable_intro_and_conclusion = disable_intro_and_conclusion;
    }
}

/**
 * PanelRequestData class representing the data for a panel request.
 */
export class PanelRequestData {
    constructor({
        title = "New public morning show",
        input_source = "",
        input_text = "",
        tts_model = "elevenlabs",
        longform = false,
        bucket_name = "public_panels",
        display_tag = "",
        podcast_name = "",
        podcast_tagline = "",
        conversation_config = new ConversationConfig(),
        tts_config = undefined,
        panel_id = null,
        transcript_parent_id = null,
        transcript_id = null,
        google_news = null,
        yle_news = null,
        techcrunch_news = null,
        hackernews = null,
        news_guidance = null,
        news_items = 5,
        segments = 5,
        languages = null,
        cronjob = null,
        owner_id = null,
        organization_id = null,
        is_public = true
    } = {}) {
        this.title = title;
        this.input_source = input_source;
        this.input_text = input_text;
        this.tts_model = tts_model;
        this.longform = longform;
        this.bucket_name = bucket_name;
        this.display_tag = display_tag;
        this.podcast_name = podcast_name;
        this.podcast_tagline = podcast_tagline;
        this.conversation_config = conversation_config;
        this.tts_config = tts_config;
        this.panel_id = panel_id;
        this.transcript_parent_id = transcript_parent_id;
        this.transcript_id = transcript_id;
        this.google_news = google_news;
        this.yle_news = yle_news;
        this.techcrunch_news = techcrunch_news;
        this.hackernews = hackernews;
        this.news_guidance = news_guidance;
        this.news_items = news_items;
        this.segments = segments;
        this.languages = languages;
        this.cronjob = cronjob;
        this.owner_id = owner_id;
        this.organization_id = organization_id;
        this.is_public = is_public;
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
        tts_config = undefined,
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
        this.title = title;
        this.input_source = input_source;
        this.input_text = input_text;
        this.tts_model = tts_model;
        this.longform = longform;
        this.display_tag = display_tag;
        this.conversation_config = conversation_config;
        this.tts_config = tts_config;
        this.google_news = google_news;
        this.yle_news = yle_news;
        this.techcrunch_news = techcrunch_news;
        this.hackernews = hackernews;
        this.news_guidance = news_guidance;
        this.news_items = news_items;
        this.segments = segments;
        this.languages = languages;
        this.description = description;
    }
}

export class TranscriptMetadata {
    constructor({
        images = undefined,
        longform = undefined,
        subjects = undefined,
        description = undefined,
        conversation_config = undefined,
        tts_config = undefined,
        tts_model = undefined
    } = {}) {
        this.images = images;
        this.longform = longform;
        this.subjects = subjects;
        this.description = description;
        this.conversation_config = conversation_config;
        this.tts_config = tts_config;
        this.tts_model = tts_model;
    }
}

export class AudioMetadata {
    constructor({
        tts_model = undefined,
        conversation_config = undefined,
        tts_config = undefined
    } = {}) {
        this.tts_model = tts_model;
        this.conversation_config = conversation_config;
        this.tts_config = tts_config;
    }
}
