import { SupabaseModel } from "./SupabaseModelInterface";

export interface ViewUserPanelDiscussionModel
    extends SupabaseModel<ViewUserPanelDiscussionModel> {
    userDataId?: string;
    panelDiscussionId?: string;
    authId?: string;
    title?: string;
    tags?: string[];
    item?: string;
    userDataData?: object;
    panelDiscussionMetadata?: object;
    userDataCreatedAt?: Date;
    userDataUpdatedAt?: Date;
}

export interface ViewUserPanelTranscriptModel
    extends SupabaseModel<ViewUserPanelTranscriptModel> {
    userDataId?: string;
    panelTranscriptId?: string;
    authId?: string;
    item?: string;
    title?: string;
    lang?: string;
    transcript?: object;
    file?: string;
    bucketId?: string;
    type?: string;
    userDataData?: object;
    panelTranscriptMetadata?: object;
    userDataCreatedAt?: Date;
    userDataUpdatedAt?: Date;
}

export interface ViewUserPanelAudioModel
    extends SupabaseModel<ViewUserPanelAudioModel> {
    userDataId?: string;
    panelAudioId?: string;
    authId?: string;
    item?: string;
    title?: string;
    lang?: string;
    file?: string;
    bucketId?: string;
    userDataData?: object;
    panelAudioMetadata?: object;
    userDataCreatedAt?: Date;
    userDataUpdatedAt?: Date;
}
