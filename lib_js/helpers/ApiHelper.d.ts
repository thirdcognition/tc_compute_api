// helpers/ApiHelperInterfaces.ts

declare class ApiConfig {
    host: string;
    port: number;
    authToken: string;
    refreshToken: string;
}

declare class FetchWithAuthParams {
    apiConfig: ApiConfig;
    endpoint: string;
    method: string;
    body: Record<string, unknown>;
}

declare function fetchWithAuth(
    params: FetchWithAuthParams
): Promise<FetchWithAuthResponse>;
