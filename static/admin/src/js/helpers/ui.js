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

export const formatCronjob = (cronjob_str) => {
    if (!cronjob_str || cronjob_str === "0") return "Not set";

    const fields = cronjob_str.split(" ");
    if (fields.length < 5 || fields.length > 6) {
        throw new Error("Invalid cron job format");
    }

    const [minute, hour, dayOfMonth, month, dayOfWeek] = fields;

    const daysOfWeekMap = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
    const monthsMap = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec"
    ];

    const formatTime = (hour, minute) => {
        const formattedHour = hour.padStart(2, "0");
        const formattedMinute = minute.padStart(2, "0");
        return `${formattedHour}:${formattedMinute}`;
    };

    const formatList = (list, map) => {
        return list
            .split(",")
            .map((item) => (map ? map[parseInt(item, 10)] : item))
            .join(", ");
    };

    const formatField = (field, map, wildcardDescription, unit) => {
        if (field === "*") return wildcardDescription;
        if (field.includes(",")) return formatList(field, map);
        if (field.includes("-")) {
            const [start, end] = field.split("-");
            return `from ${map ? map[parseInt(start, 10)] : start} to ${
                map ? map[parseInt(end, 10)] : end
            }`;
        }
        if (field.includes("/")) {
            const [base, step] = field.split("/");
            return `every ${step} ${unit} starting at ${
                map ? map[parseInt(base, 10)] : base
            }`;
        }
        return map ? map[parseInt(field, 10)] : field;
    };

    const time =
        hour === "*"
            ? `${minute}th minute of every hour`
            : hour.includes("/")
              ? `${minute}th minute every ${hour.split("/")[1]} hours`
              : formatTime(hour, minute);

    const dayOfWeekDesc = formatField(
        dayOfWeek,
        daysOfWeekMap,
        "every day",
        "days"
    );
    const dayOfMonthDesc = formatField(dayOfMonth, null, "every day", "days");
    const monthDesc = formatField(month, monthsMap, "every month", "months");

    if (dayOfMonth === "*" && month === "*" && dayOfWeek === "*") {
        return `${time} every day`;
    }

    if (dayOfMonth === "*" && month === "*") {
        return `${time} ${dayOfWeekDesc}`;
    }

    if (dayOfWeek === "*") {
        return `${time} on the ${dayOfMonthDesc} of ${monthDesc}`;
    }

    return `${time} on the ${dayOfMonthDesc} of ${monthDesc}, ${dayOfWeekDesc}`;
};

export const getWordCountDescription = (wordCount, maxWordCount) => {
    const percentage = (wordCount / maxWordCount) * 100;
    if (percentage <= 10)
        return `shortest (${wordCount} words, ~${Math.round(wordCount / 250)} min)`;
    if (percentage <= 20)
        return `shorter (${wordCount} words ~${Math.round(wordCount / 250)} min)`;
    if (percentage <= 30)
        return `short (${wordCount} words ~${Math.round(wordCount / 250)} min)`;
    if (percentage <= 40)
        return `medium - (${wordCount} words ~${Math.round(wordCount / 250)} min)`;
    if (percentage <= 60)
        return `medium (${wordCount} words ~${Math.round(wordCount / 250)} min)`;
    if (percentage <= 70)
        return `medium + (${wordCount} words ~${Math.round(wordCount / 250)} min)`;
    if (percentage <= 80)
        return `long (${wordCount} words ~${Math.round(wordCount / 250)} min)`;
    if (percentage <= 90)
        return `longer (${wordCount} words ~${Math.round(wordCount / 250)} min)`;
    return `longest (${wordCount} words ~${Math.round(wordCount / 250)} min)`;
};
