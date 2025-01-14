import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchPublicPanels } from "../helpers/fetch.ts";

interface Panel {
    id: string;
    name: string;
    date: string;
}

const PanelList: React.FC = () => {
    const [panels, setPanels] = useState<Panel[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        async function fetchPanels() {
            try {
                const fetchedPanels = await fetchPublicPanels();
                const formattedPanels = fetchedPanels.map((panel: any) => ({
                    id: panel.id,
                    name: panel.title || "Unnamed Show",
                    date: new Date(panel.created_at).toLocaleDateString()
                }));
                setPanels(formattedPanels);
            } catch (error) {
                console.error("Error fetching panels:", error);
            }
        }
        fetchPanels();
    }, []);

    return (
        <div className="w-full max-w-2xl bg-blue-50 dark:bg-gray-800 rounded-lg shadow-xl p-6 mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                Shows
            </h3>
            <div className="space-y-2">
                {panels.map((panel) => (
                    <div
                        key={panel.id}
                        className="p-2 rounded-md bg-white dark:bg-gray-800 cursor-pointer"
                        onClick={() => navigate(`/panel/${panel.id}`)}
                    >
                        <span className="text-sm font-medium text-center block text-gray-700 dark:text-gray-300">
                            {panel.name} - {panel.date}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PanelList;
