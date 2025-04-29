import { useState, useEffect, useMemo, useRef } from "react";
import { Form, Card, Accordion, Container } from "react-bootstrap";
import SectionCard from "./SectionCard.jsx";
import ItemListEditor from "./ItemListEditor.jsx";
import PersonRoleEditor from "./PersonRoleEditor.jsx";
import {
    rolesPerson1Options,
    rolesPerson2Options,
    outputLanguageOptions,
    defaultPersonRolesBase,
    defaultSpeakerConfig,
    defaultTtsModelOptions,
    defaultTTSConfig
} from "../options";
import {
    getProvider,
    getTTSFields,
    getDefaultTTSConfigForProvider,
    getDefaultVoiceForProvider,
    buildDefaultPersonRoles,
    buildDefaultTTSConfig
} from "../helpers/audioHelpers";
import { getLangName } from "../helpers/languageHelpers";
import { deepEqual } from "../helpers/lib.js";

/**
 * Helper to fill missing fields in personRoles.voice_config for all availableLanguages.
 * - If voice_config[lang] exists, fill missing fields from defaults.
 * - If not, copy first available voice_config (if any), set language, fill missing fields from defaults.
 * - If no voice_config exists, use provider/language defaults.
 * - Never add/remove/reorder roles; always use the structure of the input personRoles.
 */
function fillPersonRolesVoiceConfig(personRoles, availableLanguages, provider) {
    const result = {};
    Object.entries(personRoles).forEach(([roleIdx, roleObj]) => {
        const newRole = { ...roleObj, voice_config: {} };
        const existingVoiceConfigs = roleObj.voice_config || {};
        // Find first available voice_config (deep copy)
        let firstVoiceConfig = null;
        for (const v of Object.values(existingVoiceConfigs)) {
            if (v && typeof v === "object") {
                firstVoiceConfig = { ...v };
                break;
            }
        }
        availableLanguages.forEach((lang) => {
            let baseConfig = {};
            if (existingVoiceConfigs[lang]) {
                // Use existing, but fill missing fields from defaults
                baseConfig = { ...existingVoiceConfigs[lang] };
            } else if (firstVoiceConfig) {
                // Copy first available config, but set language
                baseConfig = { ...firstVoiceConfig, language: lang };
            } else {
                // Use provider/language defaults
                baseConfig = {
                    ...defaultSpeakerConfig,
                    language: lang,
                    voice: getDefaultVoiceForProvider(provider, roleIdx)
                };
            }
            // Fill missing fields from defaultSpeakerConfig and provider/language defaults
            const filledConfig = { ...defaultSpeakerConfig, ...baseConfig };
            filledConfig.language = lang;
            if (!filledConfig.voice) {
                filledConfig.voice = getDefaultVoiceForProvider(
                    provider,
                    roleIdx
                );
            }
            newRole.voice_config[lang] = filledConfig;
        });
        result[roleIdx] = newRole;
    });
    console.log("fillPersonRolesVoiceConfig", result);
    return result;
}

/**
 * TTSConfigSection: Self-contained section for TTS Provider, TTS Language Configurations, and Person Roles.
 * - Manages its own state.
 * - Calls onChange({ ttsModel, ttsConfig, personRoles }) on any change.
 * - Accepts a single `metadata` prop (from transcript or audio instance).
 * - Extracts ttsModel, ttsConfig, personRoles from metadata (with fallback to defaults).
 * - Accepts disableRoleFields to disable editing of person role identity fields.
 * - Accepts canEditRoles to control add/remove role buttons.
 * - No <Form> or submit handling.
 * - Languages are fixed by availableLanguages prop.
 */
function TTSConfigSection({
    metadata = {},
    allowedLanguages,
    disableRoleFields = false,
    canEditRoles = false,
    onChange,
    key
}) {
    // Compose role options from both sets
    const roleOptions = useMemo(
        () =>
            Array.from(
                new Set([
                    ...(rolesPerson1Options || []),
                    ...(rolesPerson2Options || [])
                ])
            ),
        []
    );

    const availableLanguages = useMemo(
        () =>
            Array.isArray(allowedLanguages)
                ? allowedLanguages
                : [allowedLanguages],
        [allowedLanguages]
    );

    // --- Extract from metadata with fallback to defaults ---
    const initialTtsModel = metadata?.tts_model || "elevenlabs";
    const initialTtsConfig = metadata?.tts_config || {};
    const initialPersonRoles =
        metadata?.conversation_config?.person_roles || {};

    // --- State ---
    const [ttsModel, setTtsModel] = useState(initialTtsModel);
    const [personRoles, setPersonRoles] = useState(
        Object.keys(initialPersonRoles).length > 0
            ? fillPersonRolesVoiceConfig(
                  initialPersonRoles,
                  availableLanguages,
                  getProvider(initialTtsModel)
              )
            : buildDefaultPersonRoles(
                  getProvider(initialTtsModel),
                  availableLanguages
              )
    );
    const [ttsConfig, setTtsConfig] = useState(
        Object.keys(initialTtsConfig).length > 0
            ? (() => {
                  const provider = getProvider(initialTtsModel);
                  const config = {};
                  const defaults = getDefaultTTSConfigForProvider(provider);
                  availableLanguages.forEach((lang) => {
                      config[lang] = {
                          ...defaults,
                          ...(initialTtsConfig[lang] || {}),
                          language: lang
                      };
                      if (!config[lang].audio_format)
                          config[lang].audio_format =
                              defaultTTSConfig.audio_format;
                      if (!config[lang].model)
                          config[lang].model =
                              defaults.model || defaultTTSConfig.model;
                      if (!config[lang].language) config[lang].language = lang;
                  });
                  return config;
              })()
            : buildDefaultTTSConfig(
                  getProvider(initialTtsModel),
                  availableLanguages
              )
    );

    // Keep ttsModel in sync with metadata
    useEffect(() => {
        setTtsModel(metadata?.tts_model || "elevenlabs");
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [metadata?.tts_model]);

    // Sync ttsConfig with metadata, ttsModel, andavailableLanguages
    useEffect(() => {
        const provider = getProvider(ttsModel);
        const metaConfig = metadata?.tts_config || {};
        if (Object.keys(metaConfig).length > 0) {
            const config = {};
            const defaults = getDefaultTTSConfigForProvider(provider);
            availableLanguages.forEach((lang) => {
                config[lang] = {
                    ...defaults,
                    ...(metaConfig[lang] || {}),
                    language: lang
                };
                if (!config[lang].audio_format)
                    config[lang].audio_format = defaultTTSConfig.audio_format;
                if (!config[lang].model)
                    config[lang].model =
                        defaults.model || defaultTTSConfig.model;
                if (!config[lang].language) config[lang].language = lang;
            });
            setTtsConfig(config);
        } else {
            setTtsConfig(buildDefaultTTSConfig(provider, availableLanguages));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [metadata?.tts_model, ttsModel, allowedLanguages]);

    // Sync personRoles with metadata, ttsModel, and availableLanguages, RESETTING on key change
    useEffect(() => {
        const provider = getProvider(ttsModel);
        const metaRoles = metadata?.conversation_config?.person_roles || {};
        let newPersonRoles;

        if (Object.keys(metaRoles).length > 0) {
            // Calculate roles based on metadata
            newPersonRoles = fillPersonRolesVoiceConfig(
                metaRoles,
                availableLanguages,
                provider
            );
        } else {
            // Calculate default roles
            newPersonRoles = buildDefaultPersonRoles(
                provider,
                availableLanguages
            );
        }

        // Always set the state when this effect runs (triggered by key or other deps).
        // React handles optimization if the state is identical.
        // This ensures a 'reset' semantic when the key changes, even if the resulting
        // roles happen to be the same as the previous state.
        if (!deepEqual(newPersonRoles, personRoles)) {
            setPersonRoles(newPersonRoles);
        }

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [
        metadata?.conversation_config?.person_roles,
        key,
        ttsModel,
        allowedLanguages
    ]); // Explicitly list dependencies

    // When ttsModel or availableLanguages changes, fill missing fields in current personRoles state
    useEffect(() => {
        const provider = getProvider(ttsModel);
        setPersonRoles((prev) =>
            fillPersonRolesVoiceConfig(prev, availableLanguages, provider)
        );
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [ttsModel, allowedLanguages]);

    // Call onChange whenever any of the main state changes, but only if content actually changed
    const lastSent = useRef({ ttsModel, ttsConfig, personRoles });

    useEffect(() => {
        const current = JSON.parse(
            JSON.stringify({ ttsModel, ttsConfig, personRoles })
        );
        if (!deepEqual(current, lastSent.current)) {
            console.log("change", lastSent.current, current);
            lastSent.current = current;
            if (onChange) {
                onChange(current);
            }
        }
    }, [ttsModel, ttsConfig, personRoles, onChange]);

    // --- Handlers ---
    const handleTTSConfigChange = (lang, field, value) => {
        const providerDefaults = getDefaultTTSConfigForProvider(
            getProvider(ttsModel)
        );
        setTtsConfig((prev) => ({
            ...prev,
            [lang]: {
                ...(prev[lang] || {
                    ...providerDefaults,
                    language: lang
                }),
                [field]: value
            }
        }));
    };

    // Person Role Handlers (add/remove only if canEditRoles)
    const handleAddPersonRole = () => {
        const keys = Object.keys(personRoles).map((k) => parseInt(k, 10));
        const nextKey = keys.length ? Math.max(...keys) + 1 : 1;
        setPersonRoles((prev) => {
            const newRoles = { ...prev };
            newRoles[nextKey] = {
                ...(defaultPersonRolesBase[nextKey] || {
                    name: "",
                    persona: "",
                    role: roleOptions[0] || ""
                }),
                voice_config: {}
            };
            availableLanguages.forEach((lang) => {
                newRoles[nextKey].voice_config[lang] = {
                    ...defaultSpeakerConfig,
                    language: lang,
                    voice: getDefaultVoiceForProvider(
                        getProvider(ttsModel),
                        nextKey
                    )
                };
            });
            return newRoles;
        });
    };

    const handleRemovePersonRole = (keyToRemove) => {
        setPersonRoles((prev) => {
            const updated = { ...prev };
            delete updated[keyToRemove];
            return updated;
        });
    };

    const handlePersonRoleChange = (key, field, value) => {
        setPersonRoles((prev) => {
            const updatedRoles = { ...prev };
            const roleToUpdate = { ...updatedRoles[key] };
            const pathParts = field.split(".");

            let currentLevel = roleToUpdate;
            for (let i = 0; i < pathParts.length - 1; i++) {
                const part = pathParts[i];
                if (!currentLevel[part]) {
                    currentLevel[part] = {};
                }
                currentLevel = currentLevel[part];
            }

            currentLevel[pathParts[pathParts.length - 1]] = value;
            updatedRoles[key] = roleToUpdate;
            return updatedRoles;
        });
    };

    // --- Render Functions ---
    const provider = getProvider(ttsModel);
    const ttsFields = getTTSFields(provider);

    return (
        <Container fluid className="p-0">
            <SectionCard title="TTS Provider">
                <Form.Group controlId="ttsModel" className="mb-4">
                    <Form.Label className="font-semibold">
                        Select TTS Provider:
                    </Form.Label>
                    <Form.Select
                        value={ttsModel}
                        onChange={(e) => setTtsModel(e.target.value)}
                        className="rounded border-gray-300 focus:ring-blue-500 focus:border-blue-500"
                    >
                        {defaultTtsModelOptions.map((model) => (
                            <option
                                value={model.value}
                                key={model.value}
                                disabled={model.disabled}
                            >
                                {model.label}
                            </option>
                        ))}
                    </Form.Select>
                </Form.Group>
                <Card.Title className="text-lg font-semibold mt-4 mb-2">
                    TTS Language Configurations
                </Card.Title>
                <Accordion alwaysOpen>
                    {availableLanguages.map((lang) => (
                        <Accordion.Item
                            eventKey={lang + "-" + ttsModel}
                            key={lang + "-" + ttsModel}
                        >
                            <Accordion.Header>
                                <span className="font-semibold">
                                    {outputLanguageOptions[lang] ||
                                        getLangName(lang)}
                                </span>
                            </Accordion.Header>
                            <Accordion.Body>
                                <div className="flex flex-wrap gap-3">
                                    {ttsFields.map((field) => (
                                        <Form.Group
                                            key={field + "-" + ttsModel}
                                            controlId={`ttsConfig-${lang}-${field}`}
                                            className="flex-1 min-w-[150px]"
                                        >
                                            <Form.Label className="block text-sm font-medium text-gray-700 mb-1">
                                                {field}
                                            </Form.Label>
                                            <Form.Control
                                                type={
                                                    typeof ttsConfig[lang]?.[
                                                        field
                                                    ] === "number"
                                                        ? "number"
                                                        : "text"
                                                }
                                                step={
                                                    field === "speed"
                                                        ? "0.1"
                                                        : undefined
                                                }
                                                value={
                                                    ttsConfig[lang]?.[field] !==
                                                        undefined &&
                                                    ttsConfig[lang]?.[field] !==
                                                        ""
                                                        ? ttsConfig[lang][field]
                                                        : getDefaultTTSConfigForProvider(
                                                                provider
                                                            )[field] !==
                                                            undefined
                                                          ? getDefaultTTSConfigForProvider(
                                                                provider
                                                            )[field]
                                                          : defaultTTSConfig[
                                                                field
                                                            ] || ""
                                                }
                                                onChange={(e) =>
                                                    handleTTSConfigChange(
                                                        lang,
                                                        field,
                                                        e.target.value
                                                    )
                                                }
                                                className="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                                            />
                                        </Form.Group>
                                    ))}
                                </div>
                            </Accordion.Body>
                        </Accordion.Item>
                    ))}
                </Accordion>
            </SectionCard>
            <SectionCard title="Person roles" headerAs="h5">
                <ItemListEditor
                    items={Object.entries(personRoles)}
                    onAddItem={canEditRoles ? handleAddPersonRole : undefined}
                    onRemoveItem={
                        canEditRoles
                            ? (index) =>
                                  handleRemovePersonRole(
                                      Object.keys(personRoles)[index]
                                  )
                            : undefined
                    }
                    renderItem={(item) => (
                        <PersonRoleEditor
                            roleKey={item[0]}
                            roleObj={item[1]}
                            roleOptions={roleOptions}
                            allowedLanguages={availableLanguages}
                            ttsModel={ttsModel}
                            onPersonRoleChange={handlePersonRoleChange}
                            disableRoleFields={disableRoleFields}
                        />
                    )}
                    renderItemHeader={(item) => `Person ${item[0]}`}
                    addButtonLabel="Add Person"
                    alwaysKeepOneItem={true}
                    showAddButton={canEditRoles}
                    showRemoveButton={canEditRoles}
                />
            </SectionCard>
        </Container>
    );
}

export default TTSConfigSection;
