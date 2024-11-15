import { SupabaseModel, Enum } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

class JourneyItemTypeEnum extends Enum {
    constructor() {
        super();
        this.JOURNEY = "journey";
        this.SECTION = "section";
        this.MODULE = "module";
        this.ACTION = "action";
        Object.freeze(this);
    }
}

export const JourneyItemType = new JourneyItemTypeEnum();

export class JourneyTemplateModel extends SupabaseModel {
    static TABLE_NAME = "journey_template";

    constructor(args) {
        super();
        const {
            id = null,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            currentVersionId = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            disabled: {
                value: disabled,
                type: "boolean",
                required: false,
                dbColumn: "disabled"
            },
            disabledAt: {
                value: disabledAt,
                type: "date",
                required: false,
                dbColumn: "disabled_at"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            },
            currentVersionId: {
                value: currentVersionId,
                type: "uuid",
                required: false,
                dbColumn: "current_version_id"
            }
        };
    }
}

export class JourneyTemplateVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_template_version";

    constructor(args) {
        super();
        const {
            id = null,
            templateId,
            name,
            description = null,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            versionOfId = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            templateId: {
                value: templateId,
                type: "uuid",
                required: true,
                dbColumn: "template_id"
            },
            name: {
                value: name,
                type: "string",
                required: true,
                dbColumn: "name"
            },
            description: {
                value: description,
                type: "string",
                required: false,
                dbColumn: "description"
            },
            disabled: {
                value: disabled,
                type: "boolean",
                required: false,
                dbColumn: "disabled"
            },
            disabledAt: {
                value: disabledAt,
                type: "date",
                required: false,
                dbColumn: "disabled_at"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            },
            versionOfId: {
                value: versionOfId,
                type: "uuid",
                required: false,
                dbColumn: "version_of_id"
            }
        };
    }

    static async fetchCurrentVersion(supabase, versionId) {
        if (await this.existsInSupabase(supabase, versionId)) {
            return await this.fetchFromSupabase(supabase, versionId);
        }
        return null;
    }
}

export class JourneyTemplateItemModel extends SupabaseModel {
    static TABLE_NAME = "journey_template_item";

    constructor(args) {
        super();
        const {
            id = null,
            templateVersionId,
            name,
            type = null,
            data = null,
            createdAt = null,
            updatedAt = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            templateVersionId: {
                value: templateVersionId,
                type: "uuid",
                required: true,
                dbColumn: "template_version_id"
            },
            name: {
                value: name,
                type: "string",
                required: true,
                dbColumn: "name"
            },
            type: {
                value: type,
                type: JourneyItemType,
                required: false,
                dbColumn: "type"
            },
            data: {
                value: data,
                type: "json",
                required: false,
                dbColumn: "data"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            }
        };
    }
}

export class JourneyTemplateStructureModel extends SupabaseModel {
    static TABLE_NAME = "journey_template_structure";

    constructor(args) {
        super();
        const {
            id = null,
            templateVersionId,
            journeyTemplateItemId,
            parentId = null,
            previousId = null,
            nextId = null,
            createdAt = null,
            updatedAt = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            templateVersionId: {
                value: templateVersionId,
                type: "uuid",
                required: true,
                dbColumn: "template_version_id"
            },
            journeyTemplateItemId: {
                value: journeyTemplateItemId,
                type: "uuid",
                required: true,
                dbColumn: "journey_template_item_id"
            },
            parentId: {
                value: parentId,
                type: "uuid",
                required: false,
                dbColumn: "parent_id"
            },
            previousId: {
                value: previousId,
                type: "uuid",
                required: false,
                dbColumn: "previous_id"
            },
            nextId: {
                value: nextId,
                type: "uuid",
                required: false,
                dbColumn: "next_id"
            },
            createdAt: {
                value: createdAt,
                type: "date",
                required: false,
                dbColumn: "created_at"
            },
            updatedAt: {
                value: updatedAt,
                type: "date",
                required: false,
                dbColumn: "updated_at"
            }
        };
    }
}
