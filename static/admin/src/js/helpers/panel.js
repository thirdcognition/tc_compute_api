import {
    createPanel,
    createTranscript,
    createAudio,
    deleteAudio,
    deleteTranscript,
    deletePanel,
    updatePanel
} from "./fetch.js";
import { outputLanguageOptions } from "../options.js";
import { capitalizeFirstLetter } from "./lib.js";
let dialogManager = {
    toggleDialog: null
};

export const setToggleDialog = (toggleDialog) => {
    dialogManager.toggleDialog = toggleDialog;
};

export const getToggleDialog = () => {
    return dialogManager.toggleDialog;
};

export const showConfirmationDialog = (message, onConfirm) => {
    const toggleDialog = getToggleDialog();
    if (toggleDialog) {
        toggleDialog(message, onConfirm);
    } else {
        console.error(
            "toggleDialog is not set. Please initialize it in App.jsx."
        );
    }
};

/**
 * Build a PanelRequestData-compliant payload for panel, transcript, or audio creation.
 * Only includes fields if data is present and applies filtering for arrays.
 */
function buildPanelRequestData(params) {
    // Build person_roles for conversation_config
    const personRoles = {};
    // const personRolesInput =
    //     params.personRoles ||
    //     (params.audioDetails && params.audioDetails.personRoles) ||
    //     {};
    // Object.entries(personRolesInput).forEach(([idx, roleObj]) => {
    //     const hostProfile = {
    //         name: roleObj.name,
    //         persona: roleObj.persona,
    //         role: roleObj.role,
    //         voice_config: roleObj.voice_config
    //     };
    // Only include voice_config if present (from audio details)
    // const audioDetails = params.audioDetails || {};
    // if (audioDetails.speaker_configs && audioDetails.speaker_configs[idx]) {
    //     hostProfile.voice_config = audioDetails.speaker_configs[idx];
    // }
    //     personRoles[idx] = hostProfile;
    // });

    // Filtering helpers
    const filterLinks = (links) =>
        Array.isArray(links)
            ? links.filter(
                  (link) => typeof link === "string" && link.trim() !== ""
              )
            : [];
    const filterNewsConfigs = (configs) =>
        Array.isArray(configs)
            ? configs.filter(
                  (config) =>
                      config &&
                      typeof config === "object" &&
                      Object.keys(config).length > 0
              )
            : [];

    // Build conversation_config
    const conversationConfig = {
        output_language: params.outputLanguage,
        conversation_style: params.conversationStyle,
        person_roles: params.personRoles, //Object.keys(personRoles).length ? personRoles : undefined,
        dialogue_structure: params.dialogueStructure,
        engagement_techniques: params.engagementTechniques,
        user_instructions: params.userInstructions,
        podcast_name: params.podcastName,
        podcast_tagline: params.podcastTagline,
        creativity: params.creativity,
        word_count: params.wordCount,
        longform: params.longForm,
        location: params.location,
        short_intro_and_conclusion: params.shortIntroAndConclusion,
        disable_intro_and_conclusion: params.disableIntroAndConclusion
    };
    // Remove undefined fields from conversationConfig
    Object.keys(conversationConfig).forEach(
        (key) =>
            (conversationConfig[key] === undefined ||
                conversationConfig[key] === null) &&
            delete conversationConfig[key]
    );

    // Build main payload with filtering
    const payload = {
        title: params.title,
        input_source: filterLinks(params.inputSource || params.links || []),
        input_text: params.inputText,
        tts_model: params.ttsModel,
        tts_config: params.ttsConfig,
        longform: params.longForm,
        bucket_name: "public_panels",
        display_tag: params.displayTag,
        podcast_name: params.podcastName,
        podcast_tagline: params.podcastTagline,
        conversation_config: Object.keys(conversationConfig).length
            ? conversationConfig
            : undefined,
        panel_id: params.panelId,
        transcript_id: params.transcriptId,
        transcript_parent_id: params.transcriptParentId,
        google_news: filterNewsConfigs(params.googleNewsConfigs),
        yle_news: filterNewsConfigs(params.yleNewsConfigs),
        techcrunch_news: filterNewsConfigs(params.techCrunchNewsConfigs),
        hackernews: filterNewsConfigs(params.hackerNewsConfigs),
        news_guidance: params.newsGuidance,
        news_items: params.newsItems,
        segments: params.segments,
        languages: params.languages,
        cronjob: params.cronjob,
        is_public: params.is_public
    };

    // Remove undefined fields from payload
    Object.keys(payload).forEach(
        (key) =>
            (payload[key] === undefined || payload[key] === null) &&
            delete payload[key]
    );

    return payload;
}

export const handleCreatePanel = async (params) => {
    try {
        const payload = buildPanelRequestData(params);
        const panelId = await createPanel(payload);
        return { panelId, success: true };
    } catch (error) {
        console.error("Error creating panel:", error);
        alert("Failed to create panel.");
        return { success: false };
    }
};

export const handleUpdatePanel = async (panelId, params) => {
    try {
        const panelRequestData = buildPanelRequestData(params);
        const { title, is_public, disabled, ...rest } = panelRequestData;
        const panelData = {
            title,
            metadata: { ...(params.metadata || {}), ...rest },
            ...(is_public !== undefined && { is_public }),
            ...(disabled !== undefined && { disabled })
        };

        const results = await updatePanel(panelId, panelData);
        return { success: true };
    } catch (error) {
        console.error("Error updating panel:", error);
        alert("Failed to update panel.");
        return { success: false };
    }
};

export const handleCreateTranscript = async (params) => {
    try {
        const payload = buildPanelRequestData(params);
        const taskId = await createTranscript(payload);
        return { taskId, success: true };
    } catch (error) {
        console.error("Error creating transcript:", error);
        alert("Failed to create transcript.");
        return { success: false };
    }
};

export const handleCreateAudio = async (params) => {
    try {
        const payload = buildPanelRequestData(params);
        const taskId = await createAudio(payload);
        return { taskId, success: true };
    } catch (error) {
        console.error("Error creating audio.", error);
        alert("Failed to create audio.");
        return { success: false };
    }
};

export const handleDeleteItem = async (deleteTarget, refreshCallback) => {
    try {
        if (deleteTarget.type === "audio") {
            await deleteAudio(deleteTarget.id);
        } else if (deleteTarget.type === "transcript") {
            await deleteTranscript(deleteTarget.id);
        } else if (deleteTarget.type === "panel") {
            await deletePanel(deleteTarget.id);
        } else {
            throw new Error(
                `Unsupported delete target type: ${deleteTarget.type}`
            );
        }
        if (refreshCallback) {
            refreshCallback();
        } else {
            window.location.reload();
        }
    } catch (error) {
        console.error(
            `Error deleting ${deleteTarget.type} with ID ${deleteTarget.id}:`,
            error
        );
    }
};
