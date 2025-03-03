import { SupabaseModel } from "./SupabaseModelInterface";

export interface ViewUserPanelDiscussion
    extends SupabaseModel<ViewUserPanelDiscussion> {
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

export interface ViewUserPanelTranscript
    extends SupabaseModel<ViewUserPanelTranscript> {
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

export interface ViewUserPanelAudio extends SupabaseModel<ViewUserPanelAudio> {
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
