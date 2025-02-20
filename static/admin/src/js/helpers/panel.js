import {
    createPanel,
    createTranscript,
    createAudio,
    deleteAudio,
    deleteTranscript,
    deletePanel,
    updatePanel
} from "./fetch.js";
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

export const handleCreatePanel = async (params) => {
    const linksArray = params.links
        ? params.links.filter((link) => link.trim() !== "")
        : [];
    const googleNewsArray = params.googleNewsConfigs
        ? params.googleNewsConfigs.filter(
              (config) => Object.keys(config).length > 0
          )
        : [];
    const yleNewsArray = params.yleNewsConfigs
        ? params.yleNewsConfigs.filter(
              (config) => Object.keys(config).length > 0
          )
        : [];
    const techCrunchNewsArray = params.techCrunchNewsConfigs
        ? params.techCrunchNewsConfigs.filter(
              (config) => Object.keys(config).length > 0
          )
        : [];
    const hackerNewsArray = params.hackerNewsConfigs
        ? params.hackerNewsConfigs.filter(
              (config) => Object.keys(config).length > 0
          )
        : [];
    try {
        const panelId = await createPanel({
            title: params.title,
            display_tag: params.displayTag,
            input_text: params.inputText,
            input_source: linksArray,
            google_news: googleNewsArray,
            yle_news: yleNewsArray,
            techcrunch_news: techCrunchNewsArray,
            hackernews: hackerNewsArray,
            news_guidance: params.newsGuidance,
            news_items: parseInt(params.newsItems || 5),
            segments: parseInt(params.segments || 5),
            ...(params.is_public !== undefined && {
                is_public: params.is_public
            })
        });
        return { panelId, success: true };
    } catch (error) {
        console.error("Error creating panel:", error);
        alert("Failed to create panel.");
        return { success: false };
    }
};

export const handleUpdatePanel = async (panelId, params) => {
    const linksArray = params.links
        ? params.links.filter((link) => link.trim() !== "")
        : [];
    const googleNewsArray = params.googleNewsConfigs
        ? params.googleNewsConfigs.filter(
              (config) => Object.keys(config).length > 0
          )
        : [];
    const yleNewsArray = params.yleNewsConfigs
        ? params.yleNewsConfigs.filter(
              (config) => Object.keys(config).length > 0
          )
        : [];
    const techCrunchNewsArray = params.techCrunchNewsConfigs
        ? params.techCrunchNewsConfigs.filter(
              (config) => Object.keys(config).length > 0
          )
        : [];
    const hackerNewsArray = params.hackerNewsConfigs
        ? params.hackerNewsConfigs.filter(
              (config) => Object.keys(config).length > 0
          )
        : [];
    try {
        const panelData = {
            title: params.title,
            input_text: params.inputText,
            input_source: linksArray,
            metadata: {
                ...params.metadata,
                display_tag: params.displayTag,
                news_guidance: params.newsGuidance,
                news_items: parseInt(params.newsItems || 5),
                segments: parseInt(params.segments || 5),
                google_news: googleNewsArray,
                yle_news: yleNewsArray,
                techcrunch_news: techCrunchNewsArray,
                hackernews: hackerNewsArray,
                languages: params.languages
            },
            ...(params.is_public !== undefined && {
                is_public: params.is_public
            }),
            ...(params.disabled !== undefined && { disabled: params.disabled })
        };

        const results = await updatePanel(panelId, panelData);
        console.log(results);
        return { success: true };
    } catch (error) {
        console.error("Error updating panel:", error);
        alert("Failed to update panel.");
        return { success: false };
    }
};

export const handleCreateTranscript = async (params) => {
    const longForm = params.longForm || false;
    const linksArray = params.discussionData?.metadata?.input_source || [];
    const googleNewsArray = params.discussionData?.metadata?.google_news || [];
    const yleNewsArray = params.discussionData?.metadata?.yle_news || [];
    const techCrunchNewsArray =
        params.discussionData?.metadata?.techcrunch_news || [];
    const hackerNewsArray = params.discussionData?.metadata?.hackernews || [];
    const inputText = params.discussionData?.metadata?.input_text || "";
    const newsSources = [
        googleNewsArray,
        yleNewsArray,
        techCrunchNewsArray,
        hackerNewsArray
    ];
    let totalArticles = 0;
    newsSources.forEach((sourceArray) => {
        totalArticles +=
            sourceArray.reduce((val, config) => val + config.articles, 0) || 0;
    });
    const articleCount = Math.max(totalArticles + (linksArray || []).length, 1);
    const maxNumChunks = Math.max(
        longForm ? Math.ceil((params.wordCount * 5) / 8192) : 1,
        longForm ? articleCount : 1
    );
    const minChunkSize = Math.max(
        Math.min(300, params.wordCount),
        Math.min(Math.floor((params.wordCount / articleCount) * 3), 8192)
    );
    try {
        const taskId = await createTranscript({
            title: params.title,
            input_source: linksArray,
            input_text: inputText,
            conversation_config: {
                word_count: params.wordCount,
                creativity: params.creativity,
                conversation_style: params.conversationStyle,
                roles_person1: params.rolesPerson1,
                roles_person2: params.rolesPerson2,
                dialogue_structure: params.dialogueStructure,
                engagement_techniques: params.engagementTechniques,
                user_instructions:
                    params.outputLanguage !== "English" &&
                    params.userInstructions.indexOf(
                        "Make sure to write numbers as text in the specified language"
                    ) !== -1
                        ? params.userInstructions
                        : (params.outputLanguage !== "English"
                              ? " Make sure to write numbers as text in the specified language. So e.g. in English 10 in is ten, and 0.1 is zero point one."
                              : "") + params.userInstructions,
                output_language: params.outputLanguage,
                max_num_chunks: maxNumChunks,
                min_chunk_size: minChunkSize
            },
            max_output_tokens: Math.min(params.wordCount * 5, 8192),
            longform: params.longForm,
            bucket_name: "public_panels",
            panel_id: params.panelId,
            cronjob: params.cronjob
        });
        return { taskId, success: true };
    } catch (error) {
        console.error("Error creating transcript:", error);
        alert("Failed to create transcript.");
        return { success: false };
    }
};

export const handleCreateAudio = async (params) => {
    try {
        const textToSpeechConfig = {
            elevenlabs: {
                default_voices: {
                    question: params.defaultVoiceQuestion,
                    answer: params.defaultVoiceAnswer
                },
                model: "eleven_multilingual_v2"
            },
            gemini: {
                default_voices: {
                    question: params.defaultVoiceQuestion,
                    answer: params.defaultVoiceAnswer
                }
            }
        };

        const taskId = await createAudio({
            title: params.title,
            tts_model: params.ttsModel,
            conversation_config: {
                text_to_speech: {
                    [params.ttsModel]: textToSpeechConfig[params.ttsModel]
                }
            },
            bucket_name: "public_panels",
            panel_id: params.panelId,
            transcript_id: params.transcriptId
        });
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
