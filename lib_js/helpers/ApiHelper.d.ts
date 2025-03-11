// helpers/ApiHelperInterfaces.ts

export interface ApiConfig {
    host: string;
    port: number;
    authToken: string;
    refreshToken: string;
}

export interface FetchWithAuthParams {
    apiConfig: ApiConfig;
    endpoint: string;
    method: string;
    body: Record<string, unknown>;
}

export function fetchWithAuth(
    params: FetchWithAuthParams
): Promise<FetchWithAuthResponse>;
