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
        outputLanguage = "English",
        conversationStyle = ["casual", "humorous"],
        rolesPerson1 = null,
        rolesPerson2 = null,
        dialogueStructure = null,
        engagementTechniques = null,
        userInstructions = null,
        podcastName = "",
        podcastTagline = "",
        creativity = 0.7,
        wordCount = 200,
        longform = false,
        textToSpeech = {},
        location = "Finland"
    } = {}) {
        this.outputLanguage = outputLanguage;
        this.conversationStyle = conversationStyle;
        this.rolesPerson1 = rolesPerson1;
        this.rolesPerson2 = rolesPerson2;
        this.dialogueStructure = dialogueStructure;
        this.engagementTechniques = engagementTechniques;
        this.userInstructions = userInstructions;
        this.podcastName = podcastName;
        this.podcastTagline = podcastTagline;
        this.creativity = creativity;
        this.wordCount = wordCount;
        this.longform = longform;
        this.textToSpeech = textToSpeech;
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
