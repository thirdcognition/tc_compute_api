export interface Journey {
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
}

export interface JourneyVersion {
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
}

export interface JourneyItem {
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
}

export interface JourneyItemVersion {
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

export interface JourneyStructure {
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
}

export interface JourneyStructureVersion {
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
