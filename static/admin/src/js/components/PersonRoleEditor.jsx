import React from "react";
import { Card, Accordion, Form } from "react-bootstrap";
import { getLangName } from "../helpers/languageHelpers";
import {
    getProvider,
    getSpeakerFields,
    getDefaultVoiceForProvider
} from "../helpers/audioHelpers";
import { defaultSpeakerConfig } from "../options";

/**
 * Renders the editable fields for a single person role, as a Card.
 * Uses only Bootstrap Card, Accordion, and Form components for structure.
 * Tailwind classes are used for styling only.
 * Does NOT render a <Form> tag (parent form handles that).
 *
 * TTS config is now handled at the per-language level in TranscriptDetailEdit.jsx,
 * so this component only renders speaker config per-role, per-language.
 */
function PersonRoleEditor({
    roleKey,
    roleObj,
    roleOptions,
    allowedLanguages,
    ttsModel,
    onPersonRoleChange
}) {
    const provider = getProvider(ttsModel);

    // Render the speaker config fields for a single language
    const renderSpeakerConfigBody = (language) => {
        // Speaker Config fields (voice, pitch, etc.)
        const speakerConfig =
            roleObj.voice_config && roleObj.voice_config[language]
                ? roleObj.voice_config[language]
                : {
                      ...defaultSpeakerConfig,
                      language,
                      // Only set default voice from provider/role if not set
                      voice: getDefaultVoiceForProvider(provider, roleKey)
                  };

        const speakerFields = getSpeakerFields(provider);
        const speakerFieldInputs = speakerFields.map((field) => {
            const isCheckbox = typeof defaultSpeakerConfig[field] === "boolean";
            let value =
                speakerConfig[field] ??
                defaultSpeakerConfig[field] ??
                (isCheckbox ? false : "");
            // For the "voice" field, use provider/role default if not set
            if (
                field === "voice" &&
                (!value || value === "") &&
                getDefaultVoiceForProvider(provider, roleKey)
            ) {
                value = getDefaultVoiceForProvider(provider, roleKey);
            }
            const inputType =
                typeof defaultSpeakerConfig[field] === "number"
                    ? "number"
                    : "text";
            const step = [
                "speaking_rate",
                "pitch",
                "stability",
                "similarity_boost"
            ].includes(field)
                ? "0.05"
                : field === "style"
                  ? "1"
                  : field === "emote_merge_pause"
                    ? "50"
                    : undefined;
            const fieldPath = `voice_config.${language}.${field}`;

            return (
                <Form.Group
                    key={fieldPath}
                    controlId={`person-${roleKey}-${fieldPath}`}
                    className="mb-3"
                >
                    <Form.Label className="block text-sm font-medium text-gray-700 mb-1">
                        {field}
                    </Form.Label>
                    {isCheckbox ? (
                        <Form.Check
                            type="switch"
                            checked={Boolean(value)}
                            onChange={(e) =>
                                onPersonRoleChange(
                                    roleKey,
                                    fieldPath,
                                    e.target.checked
                                )
                            }
                            className="h-5 w-5"
                        />
                    ) : (
                        <Form.Control
                            type={inputType}
                            step={step}
                            value={value}
                            onChange={(e) =>
                                onPersonRoleChange(
                                    roleKey,
                                    fieldPath,
                                    e.target.value
                                )
                            }
                            className="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                    )}
                </Form.Group>
            );
        });

        return (
            <Accordion.Body className="p-2">
                <Card className="mb-2 border border-gray-200 rounded bg-gray-50">
                    <Card.Header className="font-semibold text-sm">
                        Speaker Config
                    </Card.Header>
                    <Card.Body className="p-3">{speakerFieldInputs}</Card.Body>
                </Card>
            </Accordion.Body>
        );
    };

    return (
        <>
            <Form.Group className="mb-3" controlId={`personRoleName${roleKey}`}>
                <Form.Label className="block text-sm font-medium text-gray-700 mb-1">
                    Name:
                </Form.Label>
                <Form.Control
                    type="text"
                    value={roleObj.name || ""}
                    onChange={(e) =>
                        onPersonRoleChange(roleKey, "name", e.target.value)
                    }
                    className="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                />
            </Form.Group>
            <Form.Group
                className="mb-3"
                controlId={`personRolePersona${roleKey}`}
            >
                <Form.Label className="block text-sm font-medium text-gray-700 mb-1">
                    Persona:
                </Form.Label>
                <Form.Control
                    type="text"
                    value={roleObj.persona || ""}
                    onChange={(e) =>
                        onPersonRoleChange(roleKey, "persona", e.target.value)
                    }
                    className="w-full border border-gray-300 rounded px-2 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                />
            </Form.Group>
            <Form.Group className="mb-3" controlId={`personRoleRole${roleKey}`}>
                <Form.Label className="block text-sm font-medium text-gray-700 mb-1">
                    Role:
                </Form.Label>
                <Form.Control
                    as="select"
                    value={roleObj.role || ""}
                    onChange={(e) =>
                        onPersonRoleChange(roleKey, "role", e.target.value)
                    }
                    className="w-full border border-gray-300 rounded px-2 py-1 text-sm bg-white focus:ring-blue-500 focus:border-blue-500"
                >
                    {roleOptions.map((role) => (
                        <option value={role} key={role}>
                            {role}
                        </option>
                    ))}
                </Form.Control>
            </Form.Group>

            {/* Voice Configuration */}
            <Accordion className="mt-4">
                <Accordion.Item eventKey={`voice-config-${roleKey}`}>
                    <Accordion.Header>
                        <span className="text-sm font-medium text-gray-800">
                            Voice Configuration
                        </span>
                    </Accordion.Header>
                    <Accordion.Body className="p-0">
                        <Accordion alwaysOpen>
                            {allowedLanguages.map((lang) => (
                                <Accordion.Item eventKey={lang} key={lang}>
                                    <Accordion.Header>
                                        <span className="text-sm font-medium">
                                            {getLangName(lang)}
                                        </span>
                                    </Accordion.Header>
                                    {renderSpeakerConfigBody(lang)}
                                </Accordion.Item>
                            ))}
                        </Accordion>
                    </Accordion.Body>
                </Accordion.Item>
            </Accordion>
        </>
    );
}

export default PersonRoleEditor;
