/**
 * Represents an API error with detailed information.
 */
export declare class ApiError {
    name: string; // Name of the error (e.g., "ApiError")
    code: number; // HTTP status code
    message: string; // Status text or error message
    details?: unknown; // Optional additional details about the error
}

/**
 * Function signature for throwApiError.
 * Throws an ApiError based on the response object.
 */
export declare function throwApiError(response: {
    status: number;
    statusText: string;
    error?: unknown;
}): void;
