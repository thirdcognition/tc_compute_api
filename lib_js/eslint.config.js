import globals from "globals";
import pluginJs from "@eslint/js";
import prettierConfigRecommended from "eslint-plugin-prettier/recommended";
import tseslint from "typescript-eslint";

/** @type {import('eslint').Linter.Config[]} */
export default [
    {
        languageOptions: {
            globals: {
                ...globals.browser,
                ...globals.node,
                describe: "readonly",
                before: "readonly",
                it: "readonly",
                after: "readonly"
            }
        }
    },
    pluginJs.configs.recommended,
    ...tseslint.configs.recommended,
    // pluginReactHooks.configs.flat.recommended,
    prettierConfigRecommended,
    {
        files: ["**/*.{js,mjs,cjs,ts,jsx,tsx}"]
    },
    {
        ignores: [".config/*", "node_modules/*", ".next/*"]
    }
];
