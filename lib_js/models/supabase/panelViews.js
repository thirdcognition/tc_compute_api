import { SupabaseModel } from "./supabaseModel.js";

// Define ViewUserPanelDiscussionModel
export class ViewUserPanelDiscussionModel extends SupabaseModel {
    static TABLE_NAME = "view_user_panel_discussion";
    static TABLE_FIELDS = {
        userDataId: { type: "uuid", required: false, dbColumn: "user_data_id" },
        panelDiscussionId: {
            type: "uuid",
            required: false,
            dbColumn: "panel_discussion_id"
        },
        authId: { type: "uuid", required: false, dbColumn: "auth_id" },
        title: { type: "string", required: false, dbColumn: "title" },
        tags: { type: "array", required: false, dbColumn: "tags" },
        item: { type: "string", required: false, dbColumn: "item" },
        userDataData: {
            type: "json",
            required: false,
            dbColumn: "user_data_data"
        },
        panelDiscussionMetadata: {
            type: "json",
            required: false,
            dbColumn: "panel_discussion_metadata"
        },
        userDataCreatedAt: {
            type: "date",
            required: false,
            dbColumn: "user_data_created_at"
        },
        userDataUpdatedAt: {
            type: "date",
            required: false,
            dbColumn: "user_data_updated_at"
        }
    };
}

// Define ViewUserPanelTranscriptModel
export class ViewUserPanelTranscriptModel extends SupabaseModel {
    static TABLE_NAME = "view_user_panel_transcript";
    static TABLE_FIELDS = {
        userDataId: { type: "uuid", required: false, dbColumn: "user_data_id" },
        panelTranscriptId: {
            type: "uuid",
            required: false,
            dbColumn: "panel_transcript_id"
        },
        authId: { type: "uuid", required: false, dbColumn: "auth_id" },
        item: { type: "string", required: false, dbColumn: "item" },
        title: { type: "string", required: false, dbColumn: "title" },
        lang: { type: "string", required: false, dbColumn: "lang" },
        transcript: { type: "json", required: false, dbColumn: "transcript" },
        file: { type: "string", required: false, dbColumn: "file" },
        bucketId: { type: "string", required: false, dbColumn: "bucket_id" },
        type: { type: "string", required: false, dbColumn: "type" },
        userDataData: {
            type: "json",
            required: false,
            dbColumn: "user_data_data"
        },
        panelTranscriptMetadata: {
            type: "json",
            required: false,
            dbColumn: "panel_transcript_metadata"
        },
        userDataCreatedAt: {
            type: "date",
            required: false,
            dbColumn: "user_data_created_at"
        },
        userDataUpdatedAt: {
            type: "date",
            required: false,
            dbColumn: "user_data_updated_at"
        }
    };
}

// Define ViewUserPanelAudioModel
export class ViewUserPanelAudioModel extends SupabaseModel {
    static TABLE_NAME = "view_user_panel_audio";
    static TABLE_FIELDS = {
        userDataId: { type: "uuid", required: false, dbColumn: "user_data_id" },
        panelAudioId: {
            type: "uuid",
            required: false,
            dbColumn: "panel_audio_id"
        },
        authId: { type: "uuid", required: false, dbColumn: "auth_id" },
        item: { type: "string", required: false, dbColumn: "item" },
        title: { type: "string", required: false, dbColumn: "title" },
        lang: { type: "string", required: false, dbColumn: "lang" },
        file: { type: "string", required: false, dbColumn: "file" },
        bucketId: { type: "string", required: false, dbColumn: "bucket_id" },
        userDataData: {
            type: "json",
            required: false,
            dbColumn: "user_data_data"
        },
        panelAudioMetadata: {
            type: "json",
            required: false,
            dbColumn: "panel_audio_metadata"
        },
        userDataCreatedAt: {
            type: "date",
            required: false,
            dbColumn: "user_data_created_at"
        },
        userDataUpdatedAt: {
            type: "date",
            required: false,
            dbColumn: "user_data_updated_at"
        }
    };
}
