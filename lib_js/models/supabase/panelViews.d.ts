import { SupabaseModel } from "./supabaseModel";

export declare class ViewUserPanelDiscussionModel extends SupabaseModel<ViewUserPanelDiscussionModel> {
    userDataId?: string;
    panelDiscussionId?: string;
    authId?: string;
    title?: string;
    tags?: string[];
    item?: string;
    userDataData?: Record<string, unknown>;
    panelDiscussionMetadata?: Record<string, unknown>;
    userDataCreatedAt?: Date;
    userDataUpdatedAt?: Date;
}

export declare class ViewUserPanelTranscriptModel extends SupabaseModel<ViewUserPanelTranscriptModel> {
    userDataId?: string;
    panelTranscriptId?: string;
    authId?: string;
    item?: string;
    title?: string;
    lang?: string;
    transcript?: Record<string, unknown>;
    file?: string;
    bucketId?: string;
    type?: string;
    userDataData?: Record<string, unknown>;
    panelTranscriptMetadata?: Record<string, unknown>;
    userDataCreatedAt?: Date;
    userDataUpdatedAt?: Date;
}

export declare class ViewUserPanelAudioModel extends SupabaseModel<ViewUserPanelAudioModel> {
    userDataId?: string;
    panelAudioId?: string;
    authId?: string;
    item?: string;
    title?: string;
    lang?: string;
    file?: string;
    bucketId?: string;
    userDataData?: Record<string, unknown>;
    panelAudioMetadata?: Record<string, unknown>;
    userDataCreatedAt?: Date;
    userDataUpdatedAt?: Date;
}
