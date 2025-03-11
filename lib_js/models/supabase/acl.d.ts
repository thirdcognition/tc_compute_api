import { SupabaseModel } from "./supabaseModel";

export enum ACLEnum {
    PUBLIC = "public",
    GROUP = "group",
    PRIVATE = "private"
}

export enum UserACLEnum {
    ADM = "adm",
    RW = "rw",
    RO = "ro"
}

export declare class ACLGroupModel extends SupabaseModel<ACLGroupModel> {
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

export declare class ACLGroupItemsModel extends SupabaseModel<ACLGroupItemsModel> {
    aclGroupId: string;
    acl?: ACLEnum;
    itemId: string;
    itemType: string;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    ownerId?: string;
    organizationId?: string;
}

export declare class ACLGroupUsersModel extends SupabaseModel<ACLGroupUsersModel> {
    authId: string;
    userId: string;
    aclGroupId: string;
    acl?: UserACLEnum;
    disabled?: boolean;
    disabledAt?: Date;
    createdAt?: Date;
    updatedAt?: Date;
    organizationId?: string;
}

export declare class ACLGroupUsersWithItemsModel {
    organizationId?: string;
    aclGroupId: string;
    itemId: string;
    itemType: string;
    itemAcl: ACLEnum;
    itemCreatedAt?: Date;
    itemDisabled: boolean;
    itemDisabledAt?: Date;
    authId: string;
    userAcl: UserACLEnum;
    userId: string;
    userCreatedAt?: Date;
    userDisabled: boolean;
    userDisabledAt?: Date;
}
