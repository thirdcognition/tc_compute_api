export const processStateIcon = (state) => {
    switch (state) {
        case "none":
            return "○"; // UML symbol for none
        case "waiting":
            return "⏳"; // UML symbol for waiting
        case "processing":
            return "⚙️"; // UML symbol for processing
        case "failed":
            return "❌"; // UML symbol for failed
        case "done":
            return "✔️"; // UML symbol for done
        default:
            return "";
    }
};

export const getStatusBarStyle = (taskStatus) => {
    switch ((taskStatus || "").toLowerCase()) {
        case "success":
            return "bg-green-500";
        case "failure":
            return "bg-red-500";
        case "idle":
            return "bg-gray-300";
        case "processing":
            return "bg-blue-500"; // Add style for processing
        default:
            return "bg-yellow-500";
    }
};

export const getStatusSymbol = (taskStatus) => {
    switch ((taskStatus ?? "failure").toLowerCase()) {
        case "success":
            return "✔️";
        case "failure":
            return "❌";
        case "idle":
            return "";
        case "processing":
            return "⚙️"; // Add symbol for processing
        default:
            return "";
    }
};
