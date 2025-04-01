const Constants = Object.freeze({
    userData: Object.freeze({
        PANEL_SUB: "panel_subscription",
        EPISODE_PROGRESS: "episode_playback_progress",
        EPISODE_COMPLETED: "episode_playback_completed",
        EPISODE_LIKED: "episode_liked",
        EPISODE_DISLIKED: "episode_disliked"
    })
});

export const defaultLanguages = {
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

export default Constants;
