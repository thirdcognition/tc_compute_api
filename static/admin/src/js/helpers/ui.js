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

export const formatUpdateCycle = (seconds) => {
    if (seconds === 0) return "Not set";
    const days = Math.floor(seconds / (24 * 3600));
    const hours = (seconds % (24 * 3600)) / 3600;
    return `${days}d ${hours}h`;
};

export const getWordCountDescription = (wordCount, maxWordCount) => {
    const percentage = (wordCount / maxWordCount) * 100;
    if (percentage <= 10) return `shortest (${wordCount} words)`;
    if (percentage <= 20) return `shorter (${wordCount} words)`;
    if (percentage <= 30) return `short (${wordCount} words)`;
    if (percentage <= 40) return `medium - (${wordCount} words)`;
    if (percentage <= 60) return `medium (${wordCount} words)`;
    if (percentage <= 70) return `medium + (${wordCount} words)`;
    if (percentage <= 80) return `long (${wordCount} words)`;
    if (percentage <= 90) return `longer (${wordCount} words)`;
    return `longest (${wordCount} words)`;
};
