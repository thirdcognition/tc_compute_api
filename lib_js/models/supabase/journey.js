import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export const JourneyItemType = Object.freeze({
    JOURNEY: "journey",
    SECTION: "section",
    MODULE: "module",
    ACTION: "action"
});

export class JourneyModel extends SupabaseModel {
    static TABLE_NAME = "journey";

    constructor({
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
    }) {
        super();
        this.id = id || uuidv4();
        this.templateId = templateId;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.currentVersionId = currentVersionId;
        this.updatedBy = updatedBy;
    }
}

export class JourneyVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_version";

    constructor({
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
    }) {
        super();
        this.id = id || uuidv4();
        this.journeyId = journeyId;
        this.templateVersionId = templateVersionId;
        this.name = name;
        this.description = description;
        this.metadata = metadata;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.versionOfId = versionOfId;
    }

    static validateMetadata(v) {
        if (typeof v === "string") {
            return JSON.parse(v);
        } else if (typeof v === "object") {
            return JSON.stringify(v);
        }
        return v;
    }
}

export class JourneyItemModel extends SupabaseModel {
    static TABLE_NAME = "journey_item";

    constructor({
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
    }) {
        super();
        this.id = id || uuidv4();
        this.journeyId = journeyId;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.currentVersionId = currentVersionId;
        this.updatedBy = updatedBy;
    }
}

export class JourneyItemVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_item_version";

    constructor({
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
    }) {
        super();
        this.id = id || uuidv4();
        this.journeyId = journeyId;
        this.templateItemId = templateItemId;
        this.name = name;
        this.type = type;
        this.data = data;
        this.metadata = metadata;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.versionOfId = versionOfId;
    }

    static validateJsonFields(v) {
        if (typeof v === "string") {
            return JSON.parse(v);
        } else if (typeof v === "object") {
            return JSON.stringify(v);
        }
        return v;
    }
}

export class JourneyStructureModel extends SupabaseModel {
    static TABLE_NAME = "journey_structure";

    constructor({
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
    }) {
        super();
        this.id = id || uuidv4();
        this.journeyId = journeyId;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.currentVersionId = currentVersionId;
        this.updatedBy = updatedBy;
    }
}

export class JourneyStructureVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_structure_version";

    constructor({
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
    }) {
        super();
        this.id = id || uuidv4();
        this.journeyId = journeyId;
        this.journeyItemId = journeyItemId;
        this.versionId = versionId;
        this.parentId = parentId;
        this.nextId = nextId;
        this.previousId = previousId;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.ownerId = ownerId;
        this.organizationId = organizationId;
        this.versionOfId = versionOfId;
    }
}
