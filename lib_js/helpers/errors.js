class ApiError extends Error {
    constructor(status, statusText, details) {
        super(statusText);
        this.name = this.constructor.name;
        this.code = status;
        this.details = details;
        Error.captureStackTrace(this, this.constructor);
    }
}

export function throwApiError(response) {
    throw new ApiError(response.status, response.statusText, response.error);
}
