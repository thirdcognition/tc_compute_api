import {
    GoogleNewsConfig,
    YleNewsConfig,
    TechCrunchNewsConfig,
    HackerNewsConfig
} from "./sources";

/**
 * SpeakerConfig interface for TTS speaker properties.
 */
export interface SpeakerConfig {
    voice?: string;
    language?: string;
    pitch?: string;
    speaking_rate?: string | number;
    stability?: number;
    similarity_boost?: number;
    style?: number;
    use_speaker_boost?: boolean;
    ssml_gender?: string;
    use_emote?: boolean;
    emote_pause?: string;
    emote_merge_pause?: number;
    [key: string]: any; // Allow extra fields for provider-specific options
}

/**
 * TTSConfig interface for Text-to-Speech system and providers.
 */
export interface TTSConfig {
    audio_format?: string;
    output_directories?: { [key: string]: string };
    temp_audio_dir?: string;
    api_base?: string;
    api_key?: string;
    api_version?: string;
    deployment?: string;
    model?: string;
    streaming?: boolean;
    speed?: number;
    language?: string;
    [key: string]: any; // Allow extra fields for provider-specific options
}

/**
 * HostProfile class representing a host's profile.
 */
export declare class HostProfile {
    name: string;
    persona: string;
    role: string;
    voice_config?: { [language: string]: { [index: number]: SpeakerConfig } };

    constructor(params: {
        name?: string;
        persona?: string;
        role?: string;
        voice_config?: {
            [language: string]: { [index: number]: SpeakerConfig };
        };
    });
}

/**
 * ConversationConfig class representing the configuration for a conversation.
 */
export declare class ConversationConfig {
    output_language?: string;
    conversation_style?: string[];
    person_roles?: { [index: number]: HostProfile };
    dialogue_structure?: string[] | null;
    engagement_techniques?: string[] | null;
    user_instructions?: string | null;
    podcast_name?: string;
    podcast_tagline?: string;
    creativity?: number;
    word_count?: number;
    longform?: boolean;
    location?: string;
    short_intro_and_conclusion?: boolean;
    disable_intro_and_conclusion?: boolean;

    constructor(params: {
        output_language?: string;
        conversation_style?: string[];
        person_roles?: { [index: number]: HostProfile };
        dialogue_structure?: string[] | null;
        engagement_techniques?: string[] | null;
        user_instructions?: string | null;
        podcast_name?: string;
        podcast_tagline?: string;
        creativity?: number;
        word_count?: number;
        longform?: boolean;
        location?: string;
        short_intro_and_conclusion?: boolean;
        disable_intro_and_conclusion?: boolean;
    });
}

/**
 * PanelRequestData class representing the data for a panel request.
 */
export declare class PanelRequestData {
    title: string;
    input_source: string | string[];
    input_text?: string;
    tts_model: string;
    longform: boolean;
    bucket_name: string;
    display_tag?: string;
    podcast_name?: string;
    podcast_tagline?: string;
    conversation_config?: ConversationConfig;
    tts_config?: { [language: string]: TTSConfig };
    panel_id?: string | null;
    transcript_parent_id?: string | null;
    transcript_id?: string | null;
    google_news?: GoogleNewsConfig | GoogleNewsConfig[] | null;
    yle_news?: YleNewsConfig | YleNewsConfig[] | null;
    techcrunch_news?: TechCrunchNewsConfig | TechCrunchNewsConfig[] | null;
    hackernews?: HackerNewsConfig | HackerNewsConfig[] | null;
    news_guidance?: string | null;
    news_items?: number;
    segments?: number;
    languages?: string[] | null;
    cronjob?: string | null;
    owner_id?: string | null;
    organization_id?: string | null;
    is_public?: boolean;

    constructor(params: {
        title?: string;
        input_source?: string | string[];
        input_text?: string;
        tts_model?: string;
        longform?: boolean;
        bucket_name?: string;
        display_tag?: string;
        podcast_name?: string;
        podcast_tagline?: string;
        conversation_config?: ConversationConfig;
        tts_config?: { [language: string]: TTSConfig };
        panel_id?: string | null;
        transcript_parent_id?: string | null;
        transcript_id?: string | null;
        google_news?: GoogleNewsConfig | GoogleNewsConfig[] | null;
        yle_news?: YleNewsConfig | YleNewsConfig[] | null;
        techcrunch_news?: TechCrunchNewsConfig | TechCrunchNewsConfig[] | null;
        hackernews?: HackerNewsConfig | HackerNewsConfig[] | null;
        news_guidance?: string | null;
        news_items?: number;
        segments?: number;
        languages?: string[] | null;
        cronjob?: string | null;
        owner_id?: string | null;
        organization_id?: string | null;
        is_public?: boolean;
    });
}

export declare class SummaryReference {
    id?: string;
    title: string;
    image?: string | null;
    url?: string | null;
    publish_date?: Date | null;

    constructor(params: {
        id?: string;
        title: string;
        image?: string | null;
        url?: string | null;
        publish_date?: Date | null;
    });
}

/**
 * SummarySubject class representing a summary subject.
 */
export declare class SummarySubject {
    title: string;
    description: string;
    references: (string | SummaryReference)[];

    constructor(params: {
        title: string;
        description: string;
        references: (string | SummaryReference)[];
    });
}

/**
 * TranscriptSummary class representing a transcript summary.
 */
export declare class TranscriptSummary {
    subjects: SummarySubject[];
    description: string;
    title: string;

    constructor(params: {
        subjects: SummarySubject[];
        description: string;
        title: string;
    });
}

export declare class PanelMetadata {
    title?: string;
    input_source?: string | string[];
    input_text?: string;
    tts_model?: string;
    longform?: boolean;
    display_tag?: string;
    conversation_config?: ConversationConfig;
    tts_config?: { [language: string]: TTSConfig };
    google_news?: GoogleNewsConfig | GoogleNewsConfig[];
    yle_news?: YleNewsConfig | YleNewsConfig[];
    techcrunch_news?: TechCrunchNewsConfig | TechCrunchNewsConfig[];
    hackernews?: HackerNewsConfig | HackerNewsConfig[];
    news_guidance?: string;
    news_items?: number;
    segments?: number;
    languages?: string[];
    description?: string;

    constructor(params: {
        title?: string;
        input_source?: string | string[];
        input_text?: string;
        tts_model?: string;
        longform?: boolean;
        display_tag?: string;
        conversation_config?: ConversationConfig;
        tts_config?: { [language: string]: TTSConfig };
        google_news?: GoogleNewsConfig | GoogleNewsConfig[];
        yle_news?: YleNewsConfig | YleNewsConfig[];
        techcrunch_news?: TechCrunchNewsConfig | TechCrunchNewsConfig[];
        hackernews?: HackerNewsConfig | HackerNewsConfig[];
        news_guidance?: string;
        news_items?: number;
        segments?: number;
        languages?: string[];
        description?: string;
    });
}

export declare class TranscriptMetadata {
    images?: string[];
    longform?: boolean;
    subjects?: SummarySubject[];
    description?: string;
    conversation_config?: ConversationConfig;
    tts_config?: { [language: string]: TTSConfig };
    tts_model?: string;

    constructor(params: {
        images?: string[];
        longform?: boolean;
        subjects?: SummarySubject[];
        description?: string;
        conversation_config?: ConversationConfig;
        tts_config?: { [language: string]: TTSConfig };
        tts_model?: string;
    });
}

export declare class AudioMetadata {
    tts_model?: string;
    conversation_config?: ConversationConfig;
    tts_config?: { [language: string]: TTSConfig };

    constructor(params: {
        tts_model?: string;
        conversation_config?: ConversationConfig;
        tts_config?: { [language: string]: TTSConfig };
    });
}
