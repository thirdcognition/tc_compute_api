import { SupabaseModel, Enum } from "./supabaseModel.js";
import { v4 as uuidv4 } from "uuid";

// Define JourneyItemType Enum
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

// Define JourneyModel
export class JourneyModel extends SupabaseModel {
    static TABLE_NAME = "journey";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        templateId: { type: "uuid", required: false, dbColumn: "template_id" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        currentVersionId: {
            type: "uuid",
            required: false,
            dbColumn: "current_version_id"
        },
        updatedBy: { type: "uuid", required: false, dbColumn: "updated_by" }
    };

    static async copyFrom(supabase, journeyId, journeyVersionId = null) {
        let existingJourney = null;
        let existingVersion = null;

        if (journeyId !== null) {
            // Fetch the existing journey
            existingJourney = await this.fetchFromSupabase(supabase, journeyId);
            if (!existingJourney) {
                throw new Error("Journey not found");
            }

            // Determine the version to copy
            journeyVersionId =
                journeyVersionId || existingJourney.currentVersionId;
            if (!journeyVersionId) {
                throw new Error(
                    "No version specified and no current version available"
                );
            }
        }

        if (journeyVersionId !== null) {
            // Fetch the existing journey version
            existingVersion = await JourneyVersionModel.fetchFromSupabase(
                supabase,
                journeyVersionId
            );
            if (!existingVersion) {
                throw new Error("Journey version not found");
            }

            if (existingJourney === null) {
                journeyId = existingVersion.journeyId;
                existingJourney = await this.fetchFromSupabase(
                    supabase,
                    journeyId
                );
                if (!existingJourney) {
                    throw new Error("Journey not found");
                }
            }
        }

        // Create a new JourneyModel instance
        const newJourneyId = uuidv4();
        const newJourney = new JourneyModel({
            id: newJourneyId,
            templateId: existingJourney.templateId
        });
        await newJourney.create(supabase);

        // Create a new JourneyVersionModel instance
        const newVersion = await JourneyVersionModel.createNewVersion(
            supabase,
            newJourneyId,
            existingVersion
        );

        // Copy JourneyItemModel and JourneyItemVersionModel instances
        const { journeyItems, journeyItemVersions, itemMap } =
            await JourneyItemModel.copyItemsFromJourney(
                supabase,
                newJourneyId,
                journeyId
            );

        // Copy JourneyStructureModel and JourneyStructureVersionModel instances
        const { journeyStructures, journeyStructureVersions } =
            await JourneyStructureModel.copyStructuresFromJourney(
                supabase,
                newJourneyId,
                journeyId,
                itemMap
            );

        return {
            newJourney,
            newVersion,
            journeyItems,
            journeyItemVersions,
            journeyStructures,
            journeyStructureVersions
        };
    }
}

// Define JourneyVersionModel
export class JourneyVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_version";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        journeyId: { type: "uuid", required: true, dbColumn: "journey_id" },
        templateId: { type: "uuid", required: false, dbColumn: "template_id" },
        name: { type: "string", required: true, dbColumn: "name" },
        description: {
            type: "string",
            required: false,
            dbColumn: "description"
        },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        versionOfId: {
            type: "uuid",
            required: false,
            dbColumn: "version_of_id"
        }
    };

    static async createNewVersion(supabase, journeyId, oldVersion = null) {
        const versionId = uuidv4();
        const version = new JourneyVersionModel({
            id: versionId,
            journeyId: journeyId,
            templateId: oldVersion.id,
            name: oldVersion.name,
            description: oldVersion.description,
            versionOfId: journeyId
        });
        await version.create(supabase);
        return version;
    }
}

// Define JourneyItemModel
export class JourneyItemModel extends SupabaseModel {
    static TABLE_NAME = "journey_item";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        journeyId: { type: "uuid", required: true, dbColumn: "journey_id" },
        templateItemId: {
            type: "uuid",
            required: false,
            dbColumn: "template_item_id"
        },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        currentVersionId: {
            type: "uuid",
            required: false,
            dbColumn: "current_version_id"
        },
        updatedBy: { type: "uuid", required: false, dbColumn: "updated_by" }
    };

    static async copyItemsFromJourney(supabase, newJourneyId, oldJourneyId) {
        // Fetch existing journey items
        const existingItems = await this.fetchExistingFromSupabase(supabase, {
            filter: oldJourneyId,
            idColumn: "journey_id"
        });
        // Fetch all item versions
        const existingItemVersions =
            await JourneyItemVersionModel.fetchExistingFromSupabase(supabase, {
                filter: oldJourneyId,
                idColumn: "journey_id"
            });

        const journeyItems = [];
        const journeyItemVersions = [];
        const itemMap = new Map();
        for (const existingItem of existingItems) {
            // Only copy items that are set in current_version_id
            if (existingItem.currentVersionId) {
                const itemId = uuidv4();
                const journeyItem = new JourneyItemModel({
                    id: itemId,
                    journeyId: newJourneyId,
                    templateItemId: existingItem.templateItemId
                });
                journeyItems.push(journeyItem);
                itemMap.set(existingItem.id, itemId);

                // Filter the corresponding item version
                const itemVersion = existingItemVersions.find(
                    (version) => version.id === existingItem.currentVersionId
                );
                if (itemVersion) {
                    const versionId = uuidv4();
                    const newItemVersion = new JourneyItemVersionModel({
                        id: versionId,
                        journeyId: newJourneyId,
                        name: itemVersion.name,
                        type: itemVersion.type,
                        data: itemVersion.data,
                        versionOfId: itemId
                    });
                    journeyItemVersions.push(newItemVersion);

                    // Update the current_version_id in the new journey item
                    itemMap.set(itemVersion.id, versionId);
                }
            }
        }

        if (journeyItems.length > 0) {
            await this.upsertToSupabase(supabase, journeyItems);
        }
        if (journeyItemVersions.length > 0) {
            await JourneyItemVersionModel.upsertToSupabase(
                supabase,
                journeyItemVersions
            );
        }
        if (journeyItems.length > 0) {
            for (const journeyItem of journeyItems) {
                journeyItem.currentVersionId = itemMap.get(journeyItem.id);
            }
            await JourneyItemModel.upsertToSupabase(supabase, journeyItems);
        }
        return { journeyItems, journeyItemVersions, itemMap };
    }
}

// Define JourneyItemVersionModel
export class JourneyItemVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_item_version";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        journeyId: { type: "uuid", required: true, dbColumn: "journey_id" },
        templateItemId: {
            type: "uuid",
            required: false,
            dbColumn: "template_item_id"
        },
        name: { type: "string", required: true, dbColumn: "name" },
        type: { type: JourneyItemType, required: false, dbColumn: "type" },
        data: { type: "json", required: false, dbColumn: "data" },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        versionOfId: {
            type: "uuid",
            required: false,
            dbColumn: "version_of_id"
        }
    };
}

// Define JourneyStructureModel
export class JourneyStructureModel extends SupabaseModel {
    static TABLE_NAME = "journey_structure";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        journeyId: { type: "uuid", required: true, dbColumn: "journey_id" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        currentVersionId: {
            type: "uuid",
            required: false,
            dbColumn: "current_version_id"
        },
        updatedBy: { type: "uuid", required: false, dbColumn: "updated_by" }
    };

    static async copyStructuresFromJourney(
        supabase,
        newJourneyId,
        oldJourneyId,
        itemMap
    ) {
        // Fetch existing journey structures
        const existingStructures = await this.fetchExistingFromSupabase(
            supabase,
            {
                filter: oldJourneyId,
                idColumn: "journey_id"
            }
        );
        // Fetch all structure versions
        const existingStructureVersions =
            await JourneyStructureVersionModel.fetchExistingFromSupabase(
                supabase,
                {
                    filter: oldJourneyId,
                    idColumn: "journey_id"
                }
            );

        const journeyStructures = [];
        const journeyStructureVersions = [];
        const structureVersionMap = new Map();

        for (const existingStructure of existingStructures) {
            // Only copy structures that are set in current_version_id
            if (existingStructure.currentVersionId) {
                const structureId = uuidv4();
                const journeyStructure = new JourneyStructureModel({
                    id: structureId,
                    journeyId: newJourneyId
                });
                journeyStructures.push(journeyStructure);
                structureVersionMap.set(existingStructure.id, structureId);

                // Filter the corresponding structure version
                const structureVersion = existingStructureVersions.find(
                    (version) =>
                        version.id === existingStructure.currentVersionId
                );
                if (structureVersion) {
                    const versionId = uuidv4();
                    const newStructureVersion =
                        new JourneyStructureVersionModel({
                            id: versionId,
                            journeyId: newJourneyId,
                            journeyItemId: itemMap.get(
                                structureVersion.journeyItemId
                            ),
                            versionId: itemMap.get(structureVersion.versionId),
                            versionOfId: structureId
                        });
                    journeyStructureVersions.push(newStructureVersion);

                    // Map the structure version ID
                    structureVersionMap.set(
                        structureVersion.id,
                        newStructureVersion.id
                    );

                    // Update the current_version_id in the new journey structure
                    itemMap.set(structureVersion.id, versionId);
                }
            }
        }

        if (journeyStructures.length > 0) {
            await this.upsertToSupabase(supabase, journeyStructures);
        }
        if (journeyStructureVersions.length > 0) {
            await JourneyStructureVersionModel.upsertToSupabase(
                supabase,
                journeyStructureVersions
            );
        }
        if (journeyStructures.length > 0) {
            for (const journeyStructure of journeyStructures) {
                journeyStructure.currentVersionId = structureVersionMap.get(
                    journeyStructure.id
                );
            }
            await JourneyStructureModel.upsertToSupabase(
                supabase,
                journeyStructures
            );
        }

        // Update parent_id, next_id, and previous_id for the new structure versions
        for (const structureVersion of journeyStructureVersions) {
            const originalVersion = existingStructureVersions.find(
                (version) => version.id === structureVersion.versionOfId
            );
            if (originalVersion) {
                structureVersion.parentId = structureVersionMap.get(
                    originalVersion.parentId
                );
                structureVersion.nextId = structureVersionMap.get(
                    originalVersion.nextId
                );
                structureVersion.previousId = structureVersionMap.get(
                    originalVersion.previousId
                );
            }
        }

        if (journeyStructureVersions.length > 0) {
            await JourneyStructureVersionModel.upsertToSupabase(
                supabase,
                journeyStructureVersions
            );
        }

        return { journeyStructures, journeyStructureVersions };
    }
}

// Define JourneyStructureVersionModel
export class JourneyStructureVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_structure_version";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        journeyId: { type: "uuid", required: true, dbColumn: "journey_id" },
        journeyItemId: {
            type: "uuid",
            required: true,
            dbColumn: "journey_item_id"
        },
        journeyItemVersionId: {
            type: "uuid",
            required: true,
            dbColumn: "journey_item_version_id"
        },
        parentId: { type: "uuid", required: false, dbColumn: "parent_id" },
        nextId: { type: "uuid", required: false, dbColumn: "next_id" },
        previousId: { type: "uuid", required: false, dbColumn: "previous_id" },
        disabled: { type: "boolean", required: false, dbColumn: "disabled" },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        },
        versionOfId: {
            type: "uuid",
            required: false,
            dbColumn: "version_of_id"
        }
    };
}
