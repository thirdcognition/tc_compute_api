import { SupabaseModel } from "./supabaseModel";
import {
    JourneyItemType,
    JourneyTemplateVersionModel,
    JourneyTemplateItemModel,
    JourneyTemplateStructureModel
} from "./journeyTemplate";
import { v4 as uuidv4 } from "uuid";

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

    static async createFromTemplate(
        supabase,
        templateVersionId,
        ownerId,
        organizationId
    ) {
        // Generate a new UUID for the journey
        const journeyId = uuidv4();

        // Create a new JourneyModel instance
        const journey = new JourneyModel({
            id: journeyId,
            templateId: templateVersionId,
            ownerId: ownerId,
            organizationId: organizationId
        });
        await journey.create(supabase);

        // Create a new JourneyVersionModel instance
        const journeyVersion = await JourneyVersionModel.createNewVersion(
            supabase,
            journeyId,
            templateVersionId,
            ownerId,
            organizationId
        );

        // Create JourneyItemModel and JourneyItemVersionModel instances
        const { journeyItems, journeyItemVersions } =
            await JourneyItemModel.createItemsFromTemplate(
                supabase,
                journeyId,
                templateVersionId,
                ownerId,
                organizationId
            );

        // Create JourneyStructureModel and JourneyStructureVersionModel instances
        const { journeyStructures, journeyStructureVersions } =
            await JourneyStructureModel.createStructuresFromTemplate(
                supabase,
                journeyId,
                templateVersionId,
                journeyItems,
                ownerId,
                organizationId
            );

        return {
            journey,
            journeyVersion,
            journeyItems,
            journeyItemVersions,
            journeyStructures,
            journeyStructureVersions
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

    static async createNewVersion(
        supabase,
        journeyId,
        templateVersionId,
        ownerId,
        organizationId
    ) {
        // Fetch template version details
        const templateVersion =
            await JourneyTemplateVersionModel.fetchCurrentVersion(
                supabase,
                templateVersionId
            );

        const versionId = uuidv4();
        const version = new JourneyVersionModel({
            id: versionId,
            journeyId: journeyId,
            templateVersionId: templateVersionId,
            name: templateVersion.name,
            description: templateVersion.description,
            ownerId: ownerId,
            organizationId: organizationId,
            versionOfId: journeyId
        });
        await version.create(supabase);
        return version;
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

    static async createItemsFromTemplate(
        supabase,
        journeyId,
        templateVersionId,
        ownerId,
        organizationId
    ) {
        // Fetch template items and create journey items
        const templateItems =
            await JourneyTemplateItemModel.fetchExistingFromSupabase(supabase, {
                filter: templateVersionId,
                idColumn: "template_version_id"
            });

        const journeyItems = [];
        const journeyItemVersions = [];
        for (const templateItem of templateItems) {
            const itemId = uuidv4();
            const journeyItem = new JourneyItemModel({
                id: itemId,
                journeyId: journeyId,
                ownerId: ownerId,
                organizationId: organizationId,
                templateItemId: templateItem.id
            });
            journeyItems.push(journeyItem);

            // Create corresponding JourneyItemVersionModel
            const versionId = uuidv4();
            const itemVersion = new JourneyItemVersionModel({
                id: versionId,
                journeyId: journeyId,
                name: templateItem.name,
                type: templateItem.type,
                data: templateItem.data,
                ownerId: ownerId,
                organizationId: organizationId,
                versionOfId: itemId
            });

            journeyItemVersions.push(itemVersion);
        }

        if (journeyItems.length > 0) {
            await JourneyItemModel.upsertToSupabase(supabase, journeyItems);
        }
        if (journeyItemVersions.length > 0) {
            await JourneyItemVersionModel.upsertToSupabase(
                supabase,
                journeyItemVersions
            );
        }
        return { journeyItems, journeyItemVersions };
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

    static async createStructuresFromTemplate(
        supabase,
        journeyId,
        templateVersionId,
        journeyItems,
        ownerId,
        organizationId
    ) {
        // Fetch template structures and create journey structures
        const templateStructures =
            await JourneyTemplateStructureModel.fetchExistingFromSupabase(
                supabase,
                { filter: templateVersionId, idColumn: "template_version_id" }
            );

        const journeyStructures = [];
        const journeyStructureVersions = [];
        const journeyItemMap = new Map(
            journeyItems.map((item) => [item.templateItemId, item.id])
        );
        const structureTemplateMap = new Map(
            journeyItems.map((item) => [item.id, item.templateItemId])
        );

        // Create a map to hold the structure version IDs
        const structureVersionMap = new Map();

        for (const templateStructure of templateStructures) {
            const structureId = uuidv4();
            const journeyStructure = new JourneyStructureModel({
                id: structureId,
                journeyId: journeyId,
                ownerId: ownerId,
                organizationId: organizationId
            });
            journeyStructures.push(journeyStructure);

            const versionId = uuidv4();
            const structureVersion = new JourneyStructureVersionModel({
                id: versionId,
                journeyId: journeyId,
                journeyItemId: journeyItemMap.get(
                    templateStructure.journeyTemplateItemId
                ),
                versionId: structureId,
                ownerId: ownerId,
                organizationId: organizationId,
                versionOfId: structureId
            });

            journeyStructureVersions.push(structureVersion);

            // Map the structure version ID
            structureVersionMap.set(templateStructure.id, structureVersion.id);

            journeyStructure.currentVersionId = structureVersion.id;
        }

        if (journeyStructures.length > 0) {
            await JourneyStructureModel.upsertToSupabase(
                supabase,
                journeyStructures
            );
        }

        if (journeyStructureVersions.length > 0) {
            await JourneyItemVersionModel.upsertToSupabase(
                supabase,
                journeyStructureVersions
            );
        }

        for (const structureVersion of journeyStructureVersions) {
            const templateStructureId = structureTemplateMap.get(
                structureVersion.journeyItemId
            );
            const templateStructure = templateStructures.find(
                (ts) => ts.id === templateStructureId
            );
            if (templateStructure) {
                structureVersion.parentId = structureVersionMap.get(
                    templateStructure.parentId
                );
                structureVersion.nextId = structureVersionMap.get(
                    templateStructure.nextId
                );
                structureVersion.previousId = structureVersionMap.get(
                    templateStructure.previousId
                );
            }
        }

        if (journeyStructureVersions.length > 0) {
            await JourneyItemVersionModel.upsertToSupabase(
                supabase,
                journeyStructureVersions
            );
        }

        return { journeyStructures, journeyStructureVersions };
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
