export interface ACLGroup {
    id?: string;
    name: string;
    description?: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface ACLGroupItems {
    aclGroupId: string;
    acl?: string; // Assuming ACL is a string enum
    itemId: string;
    itemType: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export interface ACLGroupUsers {
    authId: string;
    userId: string;
    aclGroupId: string;
    acl?: string; // Assuming UserACL is a string enum
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

export interface ACLGroupUsersWithItems {
    organizationId?: string;
    aclGroupId: string;
    itemId: string;
    itemType: string;
    itemAcl: string; // Assuming ACL is a string enum
    itemCreatedAt?: Date;
    itemDisabled: boolean;
    itemDisabledAt?: Date;
    authId: string;
    userAcl: string; // Assuming UserACL is a string enum
    userId: string;
    userCreatedAt?: Date;
    userDisabled: boolean;
    userDisabledAt?: Date;
}
