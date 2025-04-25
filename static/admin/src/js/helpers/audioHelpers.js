// static/admin/src/js/helpers/audioHelpers.js
// --- TTS/Speaker Field Logic ---
import {
    baseSpeakerFields,
    elevenLabsFields,
    geminiFields,
    defaultTtsModelOptions,
    defaultTTSConfig,
    defaultPersonRolesBase,
    defaultSpeakerConfig
} from "../options.js";

/**
 * Fetches an audio file from a URL and triggers a browser download.
 * @param {string} audioUrl - The URL of the audio file.
 * @param {object} audio - The audio object containing title and id.
 */
export const downloadAudio = async (audioUrl, audio) => {
    if (!audioUrl || !audio) {
        console.error("Download failed: Missing audioUrl or audio object.");
        alert("Failed to download audio: Invalid data.");
        return;
    }
    try {
        const response = await fetch(audioUrl);
        if (!response.ok)
            throw new Error(`HTTP error! status: ${response.status}`);
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        // Construct filename: use title or 'audio', add part of ID for uniqueness
        const filename = `${audio.title || "audio"}-${audio.id ? audio.id.substring(0, 6) : "unknown"}.mp3`;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error("Download failed", error);
        alert("Failed to download audio.");
    }
};

/**
 * For a given language, get all hosts with a voice_config for that language.
 * @param {string} lang - The language code.
 * @param {object} personRoles - The person_roles object from conversation_config.
 * @returns {Array<object>} An array of host objects with their voice config for the specified language.
 */
export const getHostsForLang = (lang, personRoles = {}) => {
    return Object.entries(personRoles)
        .map(([roleIdx, host]) => {
            // Check if voice_config exists and has the specific language key
            if (host.voice_config && host.voice_config[lang]) {
                return {
                    roleIdx,
                    host, // Contains name, role, persona
                    voiceConfig: host.voice_config[lang] // The actual config object for this lang
                };
            }
            return null;
        })
        .filter(Boolean); // Remove null entries
};

/**
 * Determines the TTS provider based on the model name.
 * @param {string} ttsModel - The TTS model string.
 * @returns {string} The provider name (e.g., "elevenlabs", "gemini") or the model string itself as fallback.
 */
export function getProvider(ttsModel) {
    if (!ttsModel) return "";
    if (ttsModel.includes("elevenlabs")) return "elevenlabs";
    if (ttsModel.includes("gemini")) return "gemini";
    if (ttsModel.includes("openai")) return "openai";
    if (ttsModel.includes("edge")) return "edge";
    return ttsModel; // Fallback
}

/**
 * Gets the relevant speaker configuration fields for a given TTS provider.
 * @param {string} provider - The TTS provider name.
 * @returns {string[]} An array of speaker field names.
 */
export function getSpeakerFields(provider) {
    if (provider === "elevenlabs") {
        return [...baseSpeakerFields, ...elevenLabsFields];
    }
    if (provider === "gemini") {
        return [...baseSpeakerFields, ...geminiFields];
    }
    // OpenAI, Edge, etc. just base fields
    return baseSpeakerFields;
}

/**
 * Gets the relevant TTS configuration fields editable for a given provider in the UI.
 * @param {string} provider - The TTS provider name.
 * @returns {string[]} An array of TTS field names.
 */
export function getTTSFields(provider) {
    // Return actual fields based on the backend TTSConfig schema and provider-specific logic.
    // See transcript_to_audio/tts/providers/ for provider-specific fields.

    // Common fields for all providers
    const commonFields = ["audio_format", "language"];

    // Provider-specific fields
    switch (provider) {
        case "openai":
            return ["audio_format", "model", "speed", "language"];
        case "elevenlabs":
            return ["audio_format", "model", "language"];
        case "geminimulti":
            return ["audio_format", "model", "language"];
        case "gemini":
        case "edge":
        default:
            return commonFields;
    }
}

/**
 * Returns the default TTS config for a given provider, using defaultTtsModelOptions and defaultTTSConfig.
 * @param {string} provider
 * @returns {object}
 */
export function getDefaultTTSConfigForProvider(provider) {
    const modelOption = defaultTtsModelOptions.find(
        (opt) => opt.value === provider
    );
    console.log(
        "get provider defaults",
        provider,
        modelOption,
        defaultTtsModelOptions
    );
    return {
        ...defaultTTSConfig,
        model:
            modelOption && modelOption.model
                ? modelOption.model
                : defaultTTSConfig.model
    };
}

/**
 * Gets the default voice for a given provider and role index.
 * @param {string} provider - The TTS provider name.
 * @param {string|number} roleIdx - The role index (as string or number).
 * @returns {string} The default voice for the provider/role, or "" if not found.
 */
export function getDefaultVoiceForProvider(provider, roleIdx) {
    const opt = defaultTtsModelOptions.find((o) => o.value === provider);
    if (opt && opt.roles && opt.roles[roleIdx]) {
        return opt.roles[roleIdx];
    }
    return "";
}

/**
 * Build the default personRoles structure for the given provider and allowedLanguages.
 */
export function buildDefaultPersonRoles(provider, allowedLanguages) {
    const roles = {};
    Object.entries(defaultPersonRolesBase).forEach(([roleIdx, baseRole]) => {
        const roleObj = {
            ...baseRole,
            voice_config: {}
        };
        allowedLanguages.forEach((lang) => {
            roleObj.voice_config[lang] = {
                ...defaultSpeakerConfig,
                language: lang,
                voice: getDefaultVoiceForProvider(provider, roleIdx)
            };
        });
        roles[roleIdx] = roleObj;
    });
    return roles;
}

/**
 * Build the default TTS config object for all allowed languages for a given provider.
 * @param {string} provider - The TTS provider name.
 * @param {string[]} allowedLanguages - Array of language codes.
 * @returns {object} TTS config object keyed by language.
 */
export function buildDefaultTTSConfig(provider, allowedLanguages) {
    const providerDefault = getDefaultTTSConfigForProvider(provider);
    const config = {};
    allowedLanguages.forEach((lang) => {
        config[lang] = {
            ...providerDefault,
            language: lang
        };
    });
    return config;
}
