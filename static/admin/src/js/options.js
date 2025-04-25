// --- Conversation Defaults ---

export const defaultConversationStyle = [
    "engaging",
    "fast-paced",
    "enthusiastic"
];

export const defaultDialogueStructure = [
    "Introduction",
    "Main Content Summary"
];

export const defaultEngagementTechniques = [
    "rhetorical questions",
    "anecdotes",
    "analogies",
    "humor"
];

// Base structure, voice_config added dynamically based on allowed languages
export const defaultPersonRolesBase = {
    1: { name: "Elton", persona: "", role: "main summarizer" },
    2: { name: "Julia", persona: "", role: "questioner/clarifier" }
};

// --- Existing Options ---

export const conversationStyleOptions = [
    "engaging",
    "fast-paced",
    "enthusiastic",
    "formal",
    "analytical",
    "casual",
    "humorous"
];

export const rolesPerson1Options = [
    "host",
    "interviewer",
    "main summarizer",
    "lead facilitator",
    "discussion leader",
    "narrator",
    "moderator"
];

export const rolesPerson2Options = [
    "questioner/clarifier",
    "guest",
    "panelist",
    "supporting commentator",
    "audience participator",
    "technical expert",
    "comic relief"
];

export const dialogueStructureOptions = [
    "Introduction",
    "Main Content Summary",
    "Conclusion",
    "Deep Dive Discussion",
    "Expert Commentary",
    "Storytelling Segment",
    "Actionable Insights",
    "Recurring Segment",
    "Case Studies",
    "Quick Tips",
    "Industry News Breakdown",
    "Closing Remarks"
];

export const engagementTechniquesOptions = [
    "rhetorical questions",
    "anecdotes",
    "analogies",
    "humor",
    "cliffhangers",
    "vivid imagery",
    "audience prompts",
    "thought experiments",
    "historical references"
];

export const outputLanguageOptions = {
    en: "English",
    fi: "Finnish",
    sv: "Swedish",
    da: "Danish",
    de: "German",
    fr: "French",
    nl: "Dutch",
    es: "Spanish",
    pt: "Portuguese",
    it: "Italian",
    el: "Greek",
    zh: "Chinese",
    ja: "Japanese",
    ru: "Russian",
    ar: "Arabic"
};

export const defaultTtsModelOptions = [
    {
        value: "elevenlabs",
        label: "ElevenLabs",
        roles: {
            1: "Liam",
            2: "Juniper"
        },
        model: "eleven_multilingual_v2",
        disabled: false
    },
    {
        value: "openai",
        label: "OpenAI",
        roles: {
            1: "echo",
            2: "shimmer"
        },
        model: "tts-1-hd",
        disabled: true
    },
    {
        value: "edge",
        label: "Edge",
        roles: {
            1: "en-US-JennyNeural",
            2: "en-US-EricNeural"
        },
        disabled: true
    },
    {
        value: "gemini",
        label: "Gemini",
        roles: {
            1: "en-US-Journey-D",
            2: "en-US-Journey-O"
        },
        disabled: false
    },
    {
        value: "geminimulti",
        label: "Gemini Multi",
        roles: {
            1: "R",
            2: "S"
        },
        model: "en-US-Studio-MultiSpeaker",
        disabled: true
    }
];

// --- Speaker Field Definitions ---

export const baseSpeakerFields = [
    "voice",
    "language",
    "pitch",
    "speaking_rate"
];

export const elevenLabsFields = [
    "stability",
    "similarity_boost",
    "style",
    "use_speaker_boost", // Added based on Python schema
    "use_emote",
    "emote_pause",
    "emote_merge_pause"
];

export const geminiFields = ["ssml_gender"];

// --- Default Configurations ---

// Default TTS configuration (may be used for initializing language defaults)
export const defaultTTSConfig = {
    audio_format: "mp3",
    // Model defaults by provider:
    // - elevenlabs: "eleven_multilingual_v2"
    // - openai: "tts-1-hd"
    // - edge: "en-US-JennyNeural"
    // - gemini: "en-US-Journey-D"
    // This is a generic default, should be overridden per provider in UI logic if needed.
    model: "eleven_multilingual_v2",
    speed: 1.0,
    language: "en"
    // Provider-specific (optional, not always shown in UI)
};

// Default Speaker configuration (matches SpeakerConfig schema)
export const defaultSpeakerConfig = {
    voice: "", // Provider/language specific default might be better
    language: "en", // Will be overridden by the language key
    pitch: "default",
    speaking_rate: 1.0,
    // ElevenLabs specific
    stability: 0.75,
    similarity_boost: 0.85,
    style: 0,
    use_speaker_boost: true, // Added based on Python schema
    use_emote: true,
    emote_pause: "1.5",
    emote_merge_pause: 500,
    // Gemini specific
    ssml_gender: "NEUTRAL"
    // Note: Allow extra fields via schema if needed for other providers
};
