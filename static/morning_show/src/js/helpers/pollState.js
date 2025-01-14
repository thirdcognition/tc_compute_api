import { fetchData } from "./fetch.js";

export const pollTaskStatus = async (
    id,
    type,
    onSuccess,
    onFailure,
    onError,
    onPolling
) => {
    try {
        onPolling(true);
        const result = await fetchData(`/system/task_status/${id}`);
        const status = (result.status ?? "failure").toLowerCase();

        if (status === "success") {
            onSuccess();
            onPolling(false);
        } else if (status === "failure") {
            onFailure();
            onPolling(false);
        } else {
            setTimeout(
                () =>
                    pollTaskStatus(
                        id,
                        type,
                        onSuccess,
                        onFailure,
                        onError,
                        onPolling
                    ),
                5000
            );
        }
    } catch (error) {
        console.error("Error polling task status:", error);
        onError();
        onPolling(false);
    }
};
