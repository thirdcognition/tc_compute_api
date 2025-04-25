// static/admin/src/js/helpers/languageHelpers.js
import { outputLanguageOptions } from "../options.js";

/**
 * Gets the full language name from a language code.
 * @param {string} code - The language code (e.g., "en").
 * @returns {string} The full language name and code (e.g., "English (en)") or just the code if not found.
 */
export function getLangName(code) {
    // Check if code exists in options, otherwise return the code itself
    return outputLanguageOptions[code]
        ? `${outputLanguageOptions[code]} (${code})`
        : code;
}

/**
 * Sorts an array of language codes with "en" placed first.
 * @param {string[]} codes - An array of language codes.
 * @returns {string[]} The sorted array of language codes.
 */
export const sortLangCodes = (codes) => {
    if (!codes) return [];
    const arr = [...codes];
    arr.sort((a, b) => {
        if (a === "en") return -1;
        if (b === "en") return 1;
        return a.localeCompare(b);
    });
    return arr;
};
