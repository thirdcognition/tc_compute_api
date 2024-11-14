import { SupabaseModel } from "./supabaseModel";
import { v4 as uuidv4 } from "uuid";

export class JourneyTemplateModel extends SupabaseModel {
    static TABLE_NAME = "journey_template";

    constructor({
        id = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        currentVersionId = null
    }) {
        super();
        this.id = id || uuidv4();
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.currentVersionId = currentVersionId;
    }
}

export class JourneyTemplateVersionModel extends SupabaseModel {
    static TABLE_NAME = "journey_template_version";

    constructor({
        id = null,
        templateId,
        name,
        description = null,
        disabled = false,
        disabledAt = null,
        createdAt = null,
        updatedAt = null,
        versionOfId = null
    }) {
        super();
        this.id = id || uuidv4();
        this.templateId = templateId;
        this.name = name;
        this.description = description;
        this.disabled = disabled;
        this.disabledAt = disabledAt;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.versionOfId = versionOfId;
    }
}

export class JourneyTemplateItemModel extends SupabaseModel {
    static TABLE_NAME = "journey_template_item";

    constructor({
        id = null,
        templateVersionId,
        name,
        type = null,
        data = null,
        createdAt = null,
        updatedAt = null
    }) {
        super();
        this.id = id || uuidv4();
        this.templateVersionId = templateVersionId;
        this.name = name;
        this.type = type;
        this.data = data;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
}

export class JourneyTemplateStructureModel extends SupabaseModel {
    static TABLE_NAME = "journey_template_structure";

    constructor({
        id = null,
        templateVersionId,
        journeyTemplateItemId,
        parentId = null,
        previousId = null,
        nextId = null,
        createdAt = null,
        updatedAt = null
    }) {
        super();
        this.id = id || uuidv4();
        this.templateVersionId = templateVersionId;
        this.journeyTemplateItemId = journeyTemplateItemId;
        this.parentId = parentId;
        this.previousId = previousId;
        this.nextId = nextId;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
}
