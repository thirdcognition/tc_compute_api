export interface UserProfile {
    id?: string;
    authId?: string;
    email?: string;
    name?: string;
    profilePicture?: string;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    activeOrganizationId?: string;
    activeConversationId?: string;
}

export interface OrganizationRole {
    id?: string;
    name: string;
    description?: string;
    seniority: number;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

export interface OrganizationTeam {
    id?: string;
    name: string;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface OrganizationTeamMembers {
    authId: string;
    userId: string;
    teamId: string;
    roleId: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

export interface OrganizationUsers {
    authId?: string;
    userId?: string;
    organizationId?: string;
    metadata?: object;
    isAdmin?: boolean;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
}

export interface Organizations {
    id?: string;
    defaultAclGroupId?: string;
    name?: string;
    website?: string;
    logo?: string;
    metadata?: object;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
}
