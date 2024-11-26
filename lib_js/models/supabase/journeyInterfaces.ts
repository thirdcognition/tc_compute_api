import { SupabaseClient } from "@supabase/supabase-js";
import { SupabaseModel } from "./SupabaseModelInterface";

export interface Journey extends SupabaseModel<Journey> {
    id?: string;
    templateId?: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    currentVersionId?: string;
    updatedBy?: string;

    copyFrom(
        supabase: SupabaseClient,
        journeyId: string,
        journeyVersionId?: string
    ): Promise<{
        newJourney: Journey;
        newVersion: JourneyVersion;
        journeyItems: JourneyItem[];
        journeyItemVersions: JourneyItemVersion[];
        journeyStructures: JourneyStructure[];
        journeyStructureVersions: JourneyStructureVersion[];
    }>;
}

export interface JourneyVersion extends SupabaseModel<JourneyVersion> {
    id?: string;
    journeyId: string;
    templateId?: string;
    name: string;
    description?: string;
    metadata?: object;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    versionOfId?: string;

    createNewVersion(
        supabase: SupabaseClient,
        journeyId: string,
        oldVersion?: JourneyVersion
    ): Promise<JourneyVersion>;
}

export interface JourneyItem extends SupabaseModel<JourneyItem> {
    id?: string;
    journeyId: string;
    templateItemId?: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    currentVersionId?: string;
    updatedBy?: string;

    copyItemsFromJourney(
        supabase: SupabaseClient,
        newJourneyId: string,
        oldJourneyId: string
    ): Promise<{
        journeyItems: JourneyItem[];
        journeyItemVersions: JourneyItemVersion[];
        itemMap: Map<string, string>;
    }>;
}

export interface JourneyItemVersion extends SupabaseModel<JourneyItemVersion> {
    id?: string;
    journeyId: string;
    templateItemId?: string;
    name: string;
    type?: string; // Assuming JourneyItemType is a string enum
    data?: object;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    versionOfId?: string;
}

export interface JourneyStructure extends SupabaseModel<JourneyStructure> {
    id?: string;
    journeyId: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    currentVersionId?: string;
    updatedBy?: string;

    copyStructuresFromJourney(
        supabase: SupabaseClient,
        newJourneyId: string,
        oldJourneyId: string,
        itemMap: Map<string, string>
    ): Promise<{
        journeyStructures: JourneyStructure[];
        journeyStructureVersions: JourneyStructureVersion[];
    }>;
}

export interface JourneyStructureVersion
    extends SupabaseModel<JourneyStructureVersion> {
    id?: string;
    journeyId: string;
    journeyItemId: string;
    journeyItemVersionId: string;
    parentId?: string;
    nextId?: string;
    previousId?: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
    versionOfId?: string;
}
