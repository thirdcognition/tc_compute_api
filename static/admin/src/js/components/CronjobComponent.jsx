import React, { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";
import { formatCronjob } from "../helpers/ui.js";

function CronjobComponent({ value, onChange }) {
    const [frequency, setFrequency] = useState("");
    const [time, setTime] = useState(""); // For time of day
    const [times, setTimes] = useState([]); // For multiple times a day
    const [enableHourlyInterval, setEnableHourlyInterval] = useState(false); // Toggle for every N hours
    const [hourlyInterval, setHourlyInterval] = useState(""); // For every N hours
    const [enableDailyInterval, setEnableDailyInterval] = useState(false); // Toggle for every N days
    const [dailyInterval, setDailyInterval] = useState(""); // For every N days
    const [daysOfWeek, setDaysOfWeek] = useState([]);
    const [daysOfMonth, setDaysOfMonth] = useState([]);

    useEffect(() => {
        // Generate the cronjob string based on the selected options
        if (!frequency) {
            onChange(""); // Set to empty string if no frequency is selected
            return;
        }

        let cronString = "* * * * *"; // Default cronjob string
        if (frequency === "hourly") {
            if (times.length > 0) {
                const minutes = times.join(",");
                cronString = `${minutes || "0"} ${enableHourlyInterval && hourlyInterval ? `*/${hourlyInterval}` : "*"} * * *`;
            } else {
                cronString = `0 ${enableHourlyInterval && hourlyInterval ? `*/${hourlyInterval}` : "*"} * * *`;
            }
        } else if (frequency === "daily") {
            if (times.length > 0) {
                const hours = times.map((t) => t.split(":")[0]).join(",");
                const minutes = times.map((t) => t.split(":")[1]).join(",");
                cronString = `${minutes || "0"} ${hours || "*"} ${enableDailyInterval && dailyInterval ? `*/${dailyInterval}` : "*"} * *`;
            } else {
                cronString = `0 0 ${enableDailyInterval && dailyInterval ? `*/${dailyInterval}` : "*"} * *`;
            }
        } else if (frequency === "weekly") {
            const [hour, minute] = time.split(":");
            cronString = `${minute || "0"} ${hour || "0"} * * ${daysOfWeek.join(",") || "*"}`;
        } else if (frequency === "monthly") {
            const [hour, minute] = time.split(":");
            cronString = `${minute || "0"} ${hour || "0"} ${daysOfMonth.join(",") || "*"} * *`;
        }
        onChange(cronString);
    }, [
        frequency,
        time,
        times,
        enableHourlyInterval,
        hourlyInterval,
        enableDailyInterval,
        dailyInterval,
        daysOfWeek,
        daysOfMonth,
        onChange
    ]);

    const addTime = () => {
        if (time && !times.includes(time)) {
            setTimes([...times, time]);
            setTime("");
        }
    };

    const removeTime = (timeToRemove) => {
        setTimes(times.filter((t) => t !== timeToRemove));
    };

    const toggleSelection = (list, setList, value) => {
        if (list.includes(value)) {
            setList(list.filter((item) => item !== value));
        } else {
            setList([...list, value]);
        }
    };

    const clearSchedule = () => {
        setFrequency("");
        setTime("");
        setTimes([]);
        setEnableHourlyInterval(false);
        setHourlyInterval("");
        setEnableDailyInterval(false);
        setDailyInterval("");
        setDaysOfWeek([]);
        setDaysOfMonth([]);
        onChange(""); // Set cronjob to empty string
    };

    //  className="mb-4 bg-white border rounded shadow-md"

    return (
        <div className="mb-4">
            <div className="flex justify-between gap-4">
                <Form.Group controlId="frequency" className="flex-none">
                    <Form.Select
                        value={frequency}
                        onChange={(e) => {
                            setFrequency(e.target.value);
                            setTimes([]);
                            setEnableHourlyInterval(false);
                            setHourlyInterval("");
                            setEnableDailyInterval(false);
                            setDailyInterval("");
                            setDaysOfWeek([]);
                            setDaysOfMonth([]);
                        }}
                        className="border-gray-300 focus:ring focus:ring-blue-200"
                    >
                        <option value="">No Schedule</option>
                        <option value="hourly">Hourly</option>
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                    </Form.Select>
                </Form.Group>

                {frequency === "hourly" && (
                    <div className="flex-1">
                        <Form.Group
                            controlId="enableHourlyInterval"
                            className="mb-2"
                        >
                            <Form.Check
                                type="switch"
                                label="Set every N Hours"
                                checked={enableHourlyInterval}
                                onChange={(e) =>
                                    setEnableHourlyInterval(e.target.checked)
                                }
                            />
                        </Form.Group>
                        {enableHourlyInterval && (
                            <Form.Group
                                controlId="hourlyInterval"
                                className="mb-2"
                            >
                                <Form.Label className="font-semibold">
                                    Every N Hours
                                </Form.Label>
                                <Form.Control
                                    type="number"
                                    min="1"
                                    value={hourlyInterval}
                                    onChange={(e) =>
                                        setHourlyInterval(e.target.value)
                                    }
                                    className="border-gray-300 focus:ring focus:ring-blue-200"
                                />
                            </Form.Group>
                        )}
                        <Form.Group controlId="time" className="mb-2">
                            <Form.Label className="font-semibold">
                                Target minute to start at
                            </Form.Label>
                            <div className="flex items-center gap-2">
                                <Form.Control
                                    type="number"
                                    min="0"
                                    max="59"
                                    value={time}
                                    onChange={(e) => setTime(e.target.value)}
                                    className="border-gray-300 focus:ring focus:ring-blue-200"
                                />
                                <Button onClick={addTime} variant="primary">
                                    Add
                                </Button>
                            </div>
                        </Form.Group>
                        <div>
                            {times.map((t, index) => (
                                <div
                                    key={index}
                                    className="flex items-center gap-2"
                                >
                                    <span>{t}</span>
                                    <Button
                                        variant="danger"
                                        size="sm"
                                        onClick={() => removeTime(t)}
                                    >
                                        Remove
                                    </Button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {frequency === "daily" && (
                    <div className="flex-1">
                        <Form.Group
                            controlId="enableDailyInterval"
                            className="mb-2"
                        >
                            <Form.Check
                                type="switch"
                                label="Set every N Days"
                                checked={enableDailyInterval}
                                onChange={(e) =>
                                    setEnableDailyInterval(e.target.checked)
                                }
                            />
                        </Form.Group>
                        {enableDailyInterval && (
                            <Form.Group
                                controlId="dailyInterval"
                                className="mb-2"
                            >
                                <Form.Label className="font-semibold">
                                    Every N Days
                                </Form.Label>
                                <Form.Control
                                    type="number"
                                    min="1"
                                    value={dailyInterval}
                                    onChange={(e) =>
                                        setDailyInterval(e.target.value)
                                    }
                                    className="border-gray-300 focus:ring focus:ring-blue-200"
                                />
                            </Form.Group>
                        )}
                        <Form.Group controlId="time" className="mb-2">
                            <Form.Label className="font-semibold">
                                Target Time (UTC)
                            </Form.Label>
                            <div className="flex items-center gap-2">
                                <Form.Control
                                    type="time"
                                    value={time}
                                    onChange={(e) => setTime(e.target.value)}
                                    className="border-gray-300 focus:ring focus:ring-blue-200"
                                />
                                <Button onClick={addTime} variant="primary">
                                    Add
                                </Button>
                            </div>
                        </Form.Group>
                        <div>
                            {times.map((t, index) => (
                                <div
                                    key={index}
                                    className="flex items-center gap-2"
                                >
                                    <span>{t}</span>
                                    <Button
                                        variant="danger"
                                        size="sm"
                                        onClick={() => removeTime(t)}
                                    >
                                        Remove
                                    </Button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {frequency === "weekly" && (
                    <div className="flex-1">
                        <Form.Label className="font-semibold">
                            Select Days of the Week
                        </Form.Label>
                        <div className="flex flex-wrap gap-2 mt-2 whitespace-nowrap">
                            {[
                                "Sun",
                                "Mon",
                                "Tue",
                                "Wed",
                                "Thu",
                                "Fri",
                                "Sat"
                            ].map((day, index) => (
                                <Button
                                    key={index}
                                    variant={
                                        daysOfWeek.includes(index.toString())
                                            ? "primary"
                                            : "outline-secondary"
                                    }
                                    className="w-12 h-12 text-center whitespace-nowrap"
                                    onClick={() =>
                                        toggleSelection(
                                            daysOfWeek,
                                            setDaysOfWeek,
                                            index.toString()
                                        )
                                    }
                                >
                                    {day}
                                </Button>
                            ))}
                        </div>
                        <Form.Group controlId="time" className="mt-4">
                            <Form.Label className="font-semibold">
                                Time of Day (UTC)
                            </Form.Label>
                            <Form.Control
                                type="time"
                                value={time}
                                onChange={(e) => setTime(e.target.value)}
                                className="border-gray-300 focus:ring focus:ring-blue-200"
                            />
                        </Form.Group>
                    </div>
                )}

                {frequency === "monthly" && (
                    <div className="flex-1">
                        <Form.Label className="font-semibold">
                            Select Days of the Month
                        </Form.Label>
                        <div className="flex flex-wrap gap-2 mt-2">
                            {Array.from({ length: 31 }, (_, i) => i + 1).map(
                                (day) => (
                                    <Button
                                        key={day}
                                        variant={
                                            daysOfMonth.includes(day.toString())
                                                ? "primary"
                                                : "outline-secondary"
                                        }
                                        className="w-12 h-12 text-center"
                                        onClick={() =>
                                            toggleSelection(
                                                daysOfMonth,
                                                setDaysOfMonth,
                                                day.toString()
                                            )
                                        }
                                    >
                                        {day}
                                    </Button>
                                )
                            )}
                        </div>
                        <Form.Group controlId="time" className="mt-4">
                            <Form.Label className="font-semibold">
                                Time of Day
                            </Form.Label>
                            <Form.Control
                                type="time"
                                value={time}
                                onChange={(e) => setTime(e.target.value)}
                                className="border-gray-300 focus:ring focus:ring-blue-200"
                            />
                        </Form.Group>
                    </div>
                )}
            </div>

            <div className="flex items-end justify-between mt-4">
                <div>
                    <strong>Generated Cronjob:</strong>{" "}
                    {value || "No Schedule Set"}
                    <div className="text-gray-600">
                        <strong>Readable Format:</strong>{" "}
                        {value ? formatCronjob(value) : "No Schedule Set"}
                    </div>
                </div>

                {value && (
                    <Button variant="danger" onClick={clearSchedule}>
                        Reset
                    </Button>
                )}
            </div>
        </div>
    );
}

export default CronjobComponent;
