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
 * TTSConfigSection: Self-contained section for TTS Provider, TTS Language Configurations, and Person Roles.
 * - Manages its own state.
 * - Calls onChange({ ttsModel, ttsConfig, personRoles }) on any change.
 * - Accepts disableRoleFields to disable editing of person role identity fields.
 * - Accepts canEditRoles to control add/remove role buttons.
 * - No <Form> or submit handling.
 * - Languages are fixed by allowedLanguages prop.
 */
function TTSConfigSection({
    initialTtsModel = "elevenlabs",
    initialTtsConfig,
    initialPersonRoles,
    allowedLanguages,
    disableRoleFields = false,
    canEditRoles = false,
    onChange
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

    // --- State ---
    const [ttsModel, setTtsModel] = useState(initialTtsModel);
    const [personRoles, setPersonRoles] = useState(initialPersonRoles || {});
    const [ttsConfig, setTtsConfig] = useState({});

    // Helper to get the default config for the current provider
    const getProviderDefaultConfig = () => {
        const provider = getProvider(ttsModel);
        return getDefaultTTSConfigForProvider(provider);
    };

    // On mount, use initialTtsConfig if provided, otherwise use provider defaults
    useEffect(() => {
        const provider = getProvider(ttsModel);
        if (initialTtsConfig && Object.keys(initialTtsConfig).length > 0) {
            const config = {};
            const defaults = getDefaultTTSConfigForProvider(provider);
            allowedLanguages.forEach((lang) => {
                config[lang] = {
                    ...defaults,
                    ...(initialTtsConfig[lang] || {}),
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
            setTtsConfig(buildDefaultTTSConfig(provider, allowedLanguages));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []); // Only on mount

    // On ttsModel change, update only provider-specific fields in ttsConfig
    useEffect(() => {
        const provider = getProvider(ttsModel);
        setTtsConfig((prev) => {
            const updated = { ...prev };
            const providerDefaults = getDefaultTTSConfigForProvider(provider);
            allowedLanguages.forEach((lang) => {
                const prevLangConfig = prev[lang] || {};
                updated[lang] = {
                    ...prevLangConfig,
                    audio_format: providerDefaults.audio_format,
                    model: providerDefaults.model,
                    language: lang
                };

                if (!providerDefaults.model) {
                    delete updated[lang].model;
                }
            });
            return updated;
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [ttsModel]);

    // Initialize personRoles from props or default, for allowedLanguages and ttsModel
    useEffect(() => {
        const provider = getProvider(ttsModel);
        if (initialPersonRoles && Object.keys(initialPersonRoles).length > 0) {
            setPersonRoles(initialPersonRoles);
        } else {
            setPersonRoles(buildDefaultPersonRoles(provider, allowedLanguages));
        }
        // Only depend on ttsModel to avoid feedback loop
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [ttsModel]);

    // When ttsModel changes, update the voice field in each role's voice_config for each language
    useEffect(() => {
        const provider = getProvider(ttsModel);
        setPersonRoles((prev) => {
            const updated = {};
            Object.entries(prev).forEach(([roleIdx, roleObj]) => {
                const updatedRole = {
                    ...roleObj,
                    voice_config: { ...roleObj.voice_config }
                };
                allowedLanguages.forEach((lang) => {
                    updatedRole.voice_config[lang] = {
                        ...defaultSpeakerConfig,
                        ...(roleObj.voice_config?.[lang] || {}),
                        language: lang,
                        voice: getDefaultVoiceForProvider(provider, roleIdx)
                    };
                });
                updated[roleIdx] = updatedRole;
            });
            return updated;
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [ttsModel]);

    // Call onChange whenever any of the main state changes, but only if content actually changed
    const lastSent = useRef({ ttsModel, ttsConfig, personRoles });

    useEffect(() => {
        const current = JSON.parse(
            JSON.stringify({ ttsModel, ttsConfig, personRoles })
        );
        if (!deepEqual(current, lastSent.current)) {
            lastSent.current = current;
            if (onChange) {
                onChange(current);
            }
        }
    }, [ttsModel, ttsConfig, personRoles, onChange]);

    // --- Handlers ---
    const handleTTSConfigChange = (lang, field, value) => {
        setTtsConfig((prev) => ({
            ...prev,
            [lang]: {
                ...(prev[lang] || {
                    ...getProviderDefaultConfig(),
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
            allowedLanguages.forEach((lang) => {
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
                    {allowedLanguages.map((lang) => (
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
                            allowedLanguages={allowedLanguages}
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
