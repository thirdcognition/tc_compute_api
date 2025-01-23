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
    "Scene Setting",
    "Character Introduction",
    "Rising Action",
    "Climax",
    "Resolution"
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

export const outputLanguageOptions = ["English", "Finnish", "Swedish"];

export const defaultTtsModelOptions = [
    {
        value: "elevenlabs",
        label: "ElevenLabs",
        defaultVoices: {
            question: "Liam",
            answer: "Juniper"
        },
        model: "eleven_multilingual_v2",
        disabled: false
    },
    {
        value: "openai",
        label: "OpenAI",
        defaultVoices: {
            question: "echo",
            answer: "shimmer"
        },
        model: "tts-1-hd",
        disabled: true
    },
    {
        value: "edge",
        label: "Edge",
        defaultVoices: {
            question: "en-US-JennyNeural",
            answer: "en-US-EricNeural"
        },
        disabled: true
    },
    {
        value: "gemini",
        label: "Gemini",
        defaultVoices: {
            question: "en-US-Journey-D",
            answer: "en-US-Journey-O"
        },
        disabled: false
    },
    {
        value: "geminimulti",
        label: "Gemini Multi",
        defaultVoices: {
            question: "R",
            answer: "S"
        },
        model: "en-US-Studio-MultiSpeaker",
        disabled: true
    }
];
