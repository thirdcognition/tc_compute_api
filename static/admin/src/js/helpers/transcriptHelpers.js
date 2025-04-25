// static/admin/src/js/helpers/transcriptHelpers.js

/**
 * Calculates the effective number of articles/segments based on panel data configuration.
 * Used to estimate transcript length.
 * @param {object} data - The panel data object (discussionData).
 * @returns {number} The calculated article/segment count.
 */
export const calculateArticleCount = (data) => {
    if (!data || !data.metadata) return 1; // Default to 1 if no data

    const metadata = data.metadata;
    const linksArray = metadata.input_source || []; // Assuming input_source holds links
    const googleNewsArray = metadata.google_news || [];
    const yleNewsArray = metadata.yle_news || [];
    const techCrunchNewsArray = metadata.techcrunch_news || [];
    const hackerNewsArray = metadata.hackernews || [];

    const newsSources = [
        googleNewsArray,
        yleNewsArray,
        techCrunchNewsArray,
        hackerNewsArray
    ];

    let totalArticles = 0;
    newsSources.forEach((sourceArray) => {
        // Ensure sourceArray is an array before reducing
        if (Array.isArray(sourceArray)) {
            totalArticles +=
                sourceArray.reduce(
                    (val, config) => val + (config.articles || 0), // Default articles to 0 if missing
                    0
                ) || 0;
        }
    });

    // Ensure linksArray is an array before getting length
    const linkCount = Array.isArray(linksArray) ? linksArray.length : 0;

    // Combine counts and compare with segment/news_items settings
    return Math.max(
        totalArticles + linkCount,
        metadata.segments || metadata.news_items || 1, // Use segments or news_items as minimum
        1 // Ensure at least 1
    );
};

/**
 * Prepares the parameters needed to create a duplicate transcript based on an existing one.
 * @param {object} transcript - The original transcript object.
 * @param {object} panelData - The associated panel data (discussionData).
 * @returns {object} The parameters object ready for handleCreateTranscript.
 */
export const prepareDuplicateTranscriptParams = (transcript, panelData) => {
    if (!transcript || !panelData) {
        console.error(
            "prepareDuplicateTranscriptParams: Missing transcript or panelData"
        );
        return null;
    }

    const config = transcript.metadata?.conversation_config || {};
    const metadata = transcript.metadata || {};

    // Build personRoles (consistent with Edit view logic)
    let personRoles = {};
    if (config.person_roles) {
        personRoles = config.person_roles;
    } else {
        // Backward compatibility
        const roles = {};
        if (config.roles_person1) roles[1] = config.roles_person1;
        if (config.roles_person2) roles[2] = config.roles_person2;
        personRoles = Object.keys(roles).length
            ? roles
            : {
                  1: { name: "Elton", persona: "", role: "main summarizer" },
                  2: {
                      name: "Julia",
                      persona: "",
                      role: "questioner/clarifier"
                  }
              };
    }

    // Prepare params for handleCreateTranscript (matching Edit view)
    const params = {
        panelId: transcript.panel_id,
        discussionData: panelData, // Use fetched discussion data
        personRoles,
        outputLanguage: config.output_language,
        conversationStyle: config.conversation_style,
        dialogueStructure: config.dialogue_structure,
        engagementTechniques: config.engagement_techniques,
        userInstructions: config.user_instructions,
        creativity: config.creativity, // Assuming creativity is stored/needed
        wordCount: config.word_count,
        longForm: metadata.longform,
        shortIntroAndConclusion: config.short_intro_and_conclusion,
        disableIntroAndConclusion: config.disable_intro_and_conclusion,
        cronjob: "", // Always empty for duplicate
        // Include audio details if they were part of the original metadata?
        ttsModel: metadata.tts_model,
        ttsConfig: metadata.tts_config
        // speakerConfigs: metadata.speaker_configs // Assuming speaker_configs might be stored
    };

    // Remove undefined/null fields before sending
    Object.keys(params).forEach(
        (key) =>
            (params[key] === undefined || params[key] === null) &&
            delete params[key]
    );

    return params;
};

/**
 * Initializes or updates the voice_config for a given set of person roles based on allowed languages and defaults.
 * @param {object} roles - The current person roles object.
 * @param {string[]} allowedLanguages - Array of allowed language codes.
 * @param {object} perLanguageDefaults - Object mapping language codes to default speaker configs.
 * @param {object} baseSpeakerConfig - The ultimate fallback default speaker config.
 * @returns {object} The updated person roles object with initialized/synchronized voice_configs.
 */
export const initializeVoiceConfigForRoles = (
    roles,
    allowedLanguages,
    perLanguageDefaults,
    baseSpeakerConfig
) => {
    const updatedRoles = JSON.parse(JSON.stringify(roles)); // Deep copy to avoid mutation

    Object.keys(updatedRoles).forEach((key) => {
        const currentConfig = updatedRoles[key].voice_config || {};
        const newVoiceConfig = {};

        allowedLanguages.forEach((lang) => {
            // Start with the base default, overlay language default, then existing person-specific config
            newVoiceConfig[lang] = {
                ...baseSpeakerConfig, // Base defaults
                ...(perLanguageDefaults[lang] || {}), // Per-language defaults
                ...(currentConfig[lang] || {}), // Existing specific config for this person/lang
                language: lang // Ensure language is correctly set
            };
        });
        updatedRoles[key].voice_config = newVoiceConfig;
    });

    return updatedRoles;
};
