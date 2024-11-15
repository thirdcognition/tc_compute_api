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

export class JourneyModel extends SupabaseModel {
    static TABLE_NAME = "journey";

    constructor(args) {
        super();
        const {
            id = null,
            templateId,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId,
            currentVersionId = null,
            updatedBy = null
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
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            },
            currentVersionId: {
                value: currentVersionId,
                type: "uuid",
                required: false,
                dbColumn: "current_version_id"
            },
            updatedBy: {
                value: updatedBy,
                type: "uuid",
                required: false,
                dbColumn: "updated_by"
            }
        };
    }
}

export class JourneyVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_version";

    constructor(args) {
        super();
        const {
            id = null,
            journeyId,
            templateVersionId,
            name,
            description = null,
            metadata = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId,
            versionOfId = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            journeyId: {
                value: journeyId,
                type: "uuid",
                required: true,
                dbColumn: "journey_id"
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
            description: {
                value: description,
                type: "string",
                required: false,
                dbColumn: "description"
            },
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
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
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            },
            versionOfId: {
                value: versionOfId,
                type: "uuid",
                required: false,
                dbColumn: "version_of_id"
            }
        };
    }
}

export class JourneyItemModel extends SupabaseModel {
    static TABLE_NAME = "journey_item";

    constructor(args) {
        super();
        const {
            id = null,
            journeyId,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId,
            currentVersionId = null,
            updatedBy = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            journeyId: {
                value: journeyId,
                type: "uuid",
                required: true,
                dbColumn: "journey_id"
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
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            },
            currentVersionId: {
                value: currentVersionId,
                type: "uuid",
                required: false,
                dbColumn: "current_version_id"
            },
            updatedBy: {
                value: updatedBy,
                type: "uuid",
                required: false,
                dbColumn: "updated_by"
            }
        };
    }
}

export class JourneyItemVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_item_version";

    constructor(args) {
        super();
        const {
            id = null,
            journeyId,
            templateItemId = null,
            name,
            type = null,
            data = null,
            metadata = null,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId,
            versionOfId = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            journeyId: {
                value: journeyId,
                type: "uuid",
                required: true,
                dbColumn: "journey_id"
            },
            templateItemId: {
                value: templateItemId,
                type: "uuid",
                required: false,
                dbColumn: "template_item_id"
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
            metadata: {
                value: metadata,
                type: "json",
                required: false,
                dbColumn: "metadata"
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
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            },
            versionOfId: {
                value: versionOfId,
                type: "uuid",
                required: false,
                dbColumn: "version_of_id"
            }
        };
    }
}

export class JourneyStructureModel extends SupabaseModel {
    static TABLE_NAME = "journey_structure";

    constructor(args) {
        super();
        const {
            id = null,
            journeyId,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId,
            currentVersionId = null,
            updatedBy = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            journeyId: {
                value: journeyId,
                type: "uuid",
                required: true,
                dbColumn: "journey_id"
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
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            },
            currentVersionId: {
                value: currentVersionId,
                type: "uuid",
                required: false,
                dbColumn: "current_version_id"
            },
            updatedBy: {
                value: updatedBy,
                type: "uuid",
                required: false,
                dbColumn: "updated_by"
            }
        };
    }
}

export class JourneyStructureVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_structure_version";

    constructor(args) {
        super();
        const {
            id = null,
            journeyId,
            journeyItemId,
            versionId,
            parentId = null,
            nextId = null,
            previousId = null,
            disabled = false,
            disabledAt = null,
            createdAt = null,
            updatedAt = null,
            ownerId = null,
            organizationId,
            versionOfId = null
        } = args;
        this.attributes = {
            id: {
                value: id || uuidv4(),
                type: "uuid",
                required: false,
                dbColumn: "id"
            },
            journeyId: {
                value: journeyId,
                type: "uuid",
                required: true,
                dbColumn: "journey_id"
            },
            journeyItemId: {
                value: journeyItemId,
                type: "uuid",
                required: true,
                dbColumn: "journey_item_id"
            },
            versionId: {
                value: versionId,
                type: "uuid",
                required: true,
                dbColumn: "version_id"
            },
            parentId: {
                value: parentId,
                type: "uuid",
                required: false,
                dbColumn: "parent_id"
            },
            nextId: {
                value: nextId,
                type: "uuid",
                required: false,
                dbColumn: "next_id"
            },
            previousId: {
                value: previousId,
                type: "uuid",
                required: false,
                dbColumn: "previous_id"
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
            ownerId: {
                value: ownerId,
                type: "uuid",
                required: false,
                dbColumn: "owner_id"
            },
            organizationId: {
                value: organizationId,
                type: "uuid",
                required: true,
                dbColumn: "organization_id"
            },
            versionOfId: {
                value: versionOfId,
                type: "uuid",
                required: false,
                dbColumn: "version_of_id"
            }
        };
    }
}
