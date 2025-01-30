// Import necessary modules and base class
import { SupabaseModel, Enum } from "./supabaseModel.js";

// Define ProcessState Enum
class ProcessStateEnum extends Enum {
    constructor() {
        super();
        this.NONE = "none";
        this.WAITING = "waiting";
        this.PROCESSING = "processing";
        this.FAILED = "failed";
        this.DONE = "done";
        Object.freeze(this);
    }
}

export const ProcessState = new ProcessStateEnum();

// Define PanelAudioModel
export class PanelAudioModel extends SupabaseModel {
    static TABLE_NAME = "panel_audio";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        panelId: { type: "uuid", required: true, dbColumn: "panel_id" },
        transcriptId: {
            type: "uuid",
            required: true,
            dbColumn: "transcript_id"
        },
        title: { type: "string", required: false, dbColumn: "title" },
        tags: { type: "array", required: false, dbColumn: "tags" },
        file: { type: "string", required: false, dbColumn: "file" },
        bucketId: {
            type: "string",
            required: true,
            dbColumn: "bucket_id",
            default: "public_panels"
        },
        processState: {
            type: ProcessState,
            required: false,
            dbColumn: "process_state"
        },
        processFailMessage: {
            type: "string",
            required: false,
            dbColumn: "process_fail_message"
        },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        isPublic: {
            type: "boolean",
            required: false,
            dbColumn: "is_public",
            default: false
        },
        disabled: {
            type: "boolean",
            required: false,
            dbColumn: "disabled",
            default: false
        },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}

// Define PanelDiscussionModel
export class PanelDiscussionModel extends SupabaseModel {
    static TABLE_NAME = "panel_discussion";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        title: { type: "string", required: false, dbColumn: "title" },
        tags: { type: "array", required: false, dbColumn: "tags" },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        isPublic: {
            type: "boolean",
            required: false,
            dbColumn: "is_public",
            default: false
        },
        disabled: {
            type: "boolean",
            required: false,
            dbColumn: "disabled",
            default: false
        },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}

// Define PanelTranscriptModel
export class PanelTranscriptModel extends SupabaseModel {
    static TABLE_NAME = "panel_transcript";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        panelId: { type: "uuid", required: true, dbColumn: "panel_id" },
        title: { type: "string", required: false, dbColumn: "title" },
        tags: { type: "array", required: false, dbColumn: "tags" },
        file: { type: "string", required: false, dbColumn: "file" },
        bucketId: {
            type: "string",
            required: true,
            dbColumn: "bucket_id",
            default: "public_panels"
        },
        type: { type: "string", required: false, dbColumn: "type" },
        transcript: { type: "json", required: false, dbColumn: "transcript" },
        processState: {
            type: ProcessState,
            required: false,
            dbColumn: "process_state"
        },
        processFailMessage: {
            type: "string",
            required: false,
            dbColumn: "process_fail_message"
        },
        generationCronjob: {
            type: "string",
            required: false,
            dbColumn: "generation_cronjob"
        },
        generationParent: {
            type: "uuid",
            required: false,
            dbColumn: "generation_parent"
        },
        metadata: { type: "json", required: false, dbColumn: "metadata" },
        isPublic: {
            type: "boolean",
            required: false,
            dbColumn: "is_public",
            default: false
        },
        disabled: {
            type: "boolean",
            required: false,
            dbColumn: "disabled",
            default: false
        },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}

// Define PanelTranscriptOrderModel
export class PanelTranscriptOrderModel extends SupabaseModel {
    static TABLE_NAME = "panel_transcript_order";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        panelId: { type: "uuid", required: true, dbColumn: "panel_id" },
        transcriptId: {
            type: "uuid",
            required: false,
            dbColumn: "transcript_id"
        },
        beforeId: { type: "uuid", required: false, dbColumn: "before_id" },
        afterId: { type: "uuid", required: false, dbColumn: "after_id" },
        data: { type: "json", required: false, dbColumn: "data" },
        isPublic: {
            type: "boolean",
            required: false,
            dbColumn: "is_public",
            default: false
        },
        disabled: {
            type: "boolean",
            required: false,
            dbColumn: "disabled",
            default: false
        },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}

// Define PanelTranscriptSourceReferenceModel
export class PanelTranscriptSourceReferenceModel extends SupabaseModel {
    static TABLE_NAME = "panel_transcript_source_reference";
    static TABLE_FIELDS = {
        id: { type: "uuid", required: false, dbColumn: "id" },
        transcriptId: {
            type: "uuid",
            required: true,
            dbColumn: "transcript_id"
        },
        sourceId: { type: "uuid", required: true, dbColumn: "source_id" },
        type: { type: "string", required: false, dbColumn: "type" },
        data: { type: "json", required: false, dbColumn: "data" },
        isPublic: {
            type: "boolean",
            required: false,
            dbColumn: "is_public",
            default: false
        },
        disabled: {
            type: "boolean",
            required: false,
            dbColumn: "disabled",
            default: false
        },
        disabledAt: { type: "date", required: false, dbColumn: "disabled_at" },
        createdAt: { type: "date", required: false, dbColumn: "created_at" },
        updatedAt: { type: "date", required: false, dbColumn: "updated_at" },
        ownerId: { type: "uuid", required: false, dbColumn: "owner_id" },
        organizationId: {
            type: "uuid",
            required: false,
            dbColumn: "organization_id"
        }
    };
}
