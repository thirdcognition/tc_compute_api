// helpers/ApiHelperInterfaces.ts

export declare class ApiConfig {
    host: string;
    port: number;
    authToken: string;
    refreshToken: string;
}

export type FetchWithAuthParams = {
    apiConfig: ApiConfig;
    endpoint: string;
    method: string;
    body: Record<string, unknown>;
};

export type FetchWithAuthResponse = {
    status: string;
    data: {
        token: string;
        user: string;
        expiresAt: string;
    };
};

export declare function fetchWithAuth(
    params: FetchWithAuthParams
): Promise<FetchWithAuthResponse>;
