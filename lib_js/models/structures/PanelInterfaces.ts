import {
    GoogleNewsConfig,
    YleNewsConfig,
    TechCrunchNewsConfig,
    HackerNewsConfig
} from "./SourcesInterfaces";

/**
 * Interface representing the structure and methods of a HostProfile.
 */
export interface HostProfile {
    name: string;
    persona: string;
    role: string;
}

/**
 * Interface representing the structure and methods of a ConversationConfig.
 */
export interface ConversationConfig {
    outputLanguage?: string;
    conversationStyle?: string[];
    rolesPerson1?: HostProfile | null;
    rolesPerson2?: HostProfile | null;
    dialogueStructure?: string[] | null;
    engagementTechniques?: string[] | null;
    userInstructions?: string | null;
    podcastName?: string;
    podcastTagline?: string;
    creativity?: number;
    wordCount?: number;
    longform?: boolean;
    textToSpeech?: Record<string, unknown>;
    location?: string;
}

/**
 * Interface representing the structure and methods of a PanelRequestData.
 */
export interface PanelRequestData {
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

export interface SummaryReference {
    id?: string;
    title: string;
    image?: string | null;
    url?: string | null;
    publish_date?: Date | null;
}

/**
 * Interface representing the structure and methods of a SummarySubject.
 */
export interface SummarySubject {
    title: string;
    description: string;
    references: (string | SummaryReference)[];
}

/**
 * Interface representing the structure and methods of a TranscriptSummary.
 */
export interface TranscriptSummary {
    subjects: SummarySubject[];
    description: string;
    title: string;
}

export interface PanelMetadata {
    title?: string; // Optional title.
    inputSource?: string | string[]; // Optional input source (string or string array).
    inputText?: string; // Optional input text.
    ttsModel?: string; // Optional TTS model.
    longform?: boolean; // Optional boolean indicating if long-form content.
    displayTag?: string; // Optional display tag.
    conversationConfig?: ConversationConfig; // Optional conversation configuration.
    googleNews?: GoogleNewsConfig | GoogleNewsConfig[]; // Optional Google News configuration (single or array).
    yleNews?: YleNewsConfig | YleNewsConfig[]; // Optional Yle News configuration (single or array).
    techcrunchNews?: TechCrunchNewsConfig | TechCrunchNewsConfig[]; // Optional TechCrunch News configuration (single or array).
    hackernews?: HackerNewsConfig | HackerNewsConfig[]; // Optional Hacker News configuration (single or array).
    newsGuidance?: string; // Optional news guidance.
    newsItems?: number; // Optional number of news items.
    segments?: number; // Optional number of segments.
    languages?: string[]; // Optional list of languages.
    description?: string; // Optional description.
}

export interface TranscriptMetadata {
    images?: string[]; // List of image URLs.
    longform?: boolean; // Indicates if it's long-form content.
    subjects?: SummarySubject[]; // List of subjects with descriptions and references.
    description?: string; // Summary of the segment's discussion.
    conversationConfig?: ConversationConfig; // Details for panel setup and dialogue.
}

export interface AudioMetadata {
    ttsModel?: string; // Optional TTS model.
    conversationConfig?: ConversationConfig; // Optional conversation configuration.
}
