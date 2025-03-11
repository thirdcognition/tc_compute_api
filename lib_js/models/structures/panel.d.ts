import {
    GoogleNewsConfig,
    YleNewsConfig,
    TechCrunchNewsConfig,
    HackerNewsConfig
} from "./sources";

/**
 * Interface representing the structure and methods of a HostProfile.
 */
export declare class HostProfile {
    name: string;
    persona: string;
    role: string;
}

/**
 * Interface representing the structure and methods of a ConversationConfig.
 */
export declare class ConversationConfig {
    output_language?: string;
    conversation_style?: string[];
    roles_person_1?: HostProfile | null;
    roles_person_2?: HostProfile | null;
    dialogue_structure?: string[] | null;
    engagement_techniques?: string[] | null;
    user_instructions?: string | null;
    podcast_name?: string;
    podcast_tagline?: string;
    creativity?: number;
    word_count?: number;
    longform?: boolean;
    text_to_speech?: Record<string, unknown>;
    location?: string;
}

/**
 * Interface representing the structure and methods of a PanelRequestData.
 */
export declare class PanelRequestData {
    title: string;
    inputSource: string | string[];
    inputText?: string;
    ttsModel: string;
    longform: boolean;
    bucketName: string;
    displayTag?: string;
    conversationConfig?: ConversationConfig;
    panelId?: string | null;
    transcriptParentId?: string | null;
    transcriptId?: string | null;
    googleNews?: GoogleNewsConfig | GoogleNewsConfig[] | null;
    yleNews?: YleNewsConfig | YleNewsConfig[] | null;
    techcrunchNews?: TechCrunchNewsConfig | TechCrunchNewsConfig[] | null;
    hackernews?: HackerNewsConfig | HackerNewsConfig[] | null;
    newsGuidance?: string | null;
    newsItems?: number;
    segments?: number;
    languages?: string[] | null;
    cronjob?: string | null;
    ownerId?: string | null;
    organizationId?: string | null;
    isPublic?: boolean;
}

export declare class SummaryReference {
    id?: string;
    title: string;
    image?: string | null;
    url?: string | null;
    publish_date?: Date | null;
}

/**
 * Interface representing the structure and methods of a SummarySubject.
 */
export declare class SummarySubject {
    title: string;
    description: string;
    references: (string | SummaryReference)[];
}

/**
 * Interface representing the structure and methods of a TranscriptSummary.
 */
export declare class TranscriptSummary {
    subjects: SummarySubject[];
    description: string;
    title: string;
}

export declare class PanelMetadata {
    title?: string; // Optional title.
    input_source?: string | string[]; // Optional input source (string or string array).
    input_text?: string; // Optional input text.
    tts_model?: string; // Optional TTS model.
    longform?: boolean; // Optional boolean indicating if long-form content.
    display_tag?: string; // Optional display tag.
    conversation_config?: ConversationConfig; // Optional conversation configuration.
    google_news?: GoogleNewsConfig | GoogleNewsConfig[]; // Optional Google News configuration (single or array).
    yle_news?: YleNewsConfig | YleNewsConfig[]; // Optional Yle News configuration (single or array).
    techcrunch_news?: TechCrunchNewsConfig | TechCrunchNewsConfig[]; // Optional TechCrunch News configuration (single or array).
    hackernews?: HackerNewsConfig | HackerNewsConfig[]; // Optional Hacker News configuration (single or array).
    news_guidance?: string; // Optional news guidance.
    news_items?: number; // Optional number of news items.
    segments?: number; // Optional number of segments.
    languages?: string[]; // Optional list of languages.
    description?: string; // Optional description.
}

export declare class TranscriptMetadata {
    images?: string[]; // List of image URLs.
    longform?: boolean; // Indicates if it's long-form content.
    subjects?: SummarySubject[]; // List of subjects with descriptions and references.
    description?: string; // Summary of the segment's discussion.
    conversation_config?: ConversationConfig; // Details for panel setup and dialogue.
}

export declare class AudioMetadata {
    tts_model?: string; // Optional TTS model.
    conversation_config?: ConversationConfig; // Optional conversation configuration.
}
