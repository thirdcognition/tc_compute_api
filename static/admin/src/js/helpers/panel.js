import { createPanel, createTranscript, createAudio } from "./fetch.js";

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
    try {
        const panelId = await createPanel({
            title: params.title,
            input_text: params.inputText,
            input_source: linksArray,
            google_news: googleNewsArray,
            yle_news: yleNewsArray
        });
        return { panelId, success: true };
    } catch (error) {
        console.error("Error creating panel:", error);
        alert("Failed to create panel.");
        return { success: false };
    }
};

export const handleCreateTranscript = async (params) => {
    const longForm = params.longForm || false;
    const linksArray = params.discussionData?.metadata?.input_source || [];
    const googleNewsArray = params.discussionData?.metadata?.google_news || [];
    const yleNewsArray = params.discussionData?.metadata?.yle_news || [];
    const inputText = params.discussionData?.metadata?.input_text || "";
    const articleCount = Math.max(
        (googleNewsArray.reduce((val, config) => val + config.articles, 0) ||
            0) +
            (yleNewsArray.reduce((val, config) => val + config.articles, 0) ||
                0) +
            (googleNewsArray.reduce(
                (val, config) => val + config.articles,
                0
            ) || 0) +
            (linksArray || []).length,
        1
    );
    const maxNumChunks = Math.max(
        longForm ? Math.ceil((params.wordCount * 5) / 8192) : 1,
        longForm ? articleCount : 1
    );
    const minChunkSize = Math.max(
        Math.min(300, params.wordCount),
        Math.min(
            Math.floor((params.wordCount / (longForm ? articleCount : 1)) * 3),
            8192
        )
    );
    const targetWordCount =
        (params.wordCount / (longForm ? articleCount : 1)) * 2 < 8192
            ? params.wordCount / (longForm ? articleCount : 1)
            : Math.ceil(8192 / 2);
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
                    `Use ${longForm ? "up to" : "at least"} ${targetWordCount} words when generating the response. Make sure to ${longForm ? "fit your response into" : "not use less than"} ${targetWordCount} words! ` +
                    (params.outputLanguage !== "English"
                        ? " Make sure to write numbers as text in the specified language. So e.g. in English 10 in is ten, and 0.1 is zero point one."
                        : "") +
                    params.userInstructions +
                    ` Generate the response with ${targetWordCount} words.`,
                output_language: params.outputLanguage,
                max_num_chunks: maxNumChunks,
                min_chunk_size: minChunkSize
            },
            max_output_tokens: Math.min(params.wordCount * 5, 8192),
            longform: params.longForm,
            bucket_name: "public_panels",
            panel_id: params.panelId,
            update_cycle: params.updateCycle
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
        const taskId = await createAudio({
            title: params.title,
            tts_model: params.ttsModel,
            conversation_config: {
                text_to_speech: {
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
