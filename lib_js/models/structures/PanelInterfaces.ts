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
