import React, { useEffect } from "react";
import ReactGA from "react-ga4";

const GA_MEASUREMENT_ID = "G-5HQD9T8EHK";
const DEBUG_MODE = true;

const DebugGA: React.FC = () => {
    useEffect(() => {
        console.group("GA4 Debug Information");
        console.log("GA Measurement ID:", GA_MEASUREMENT_ID);
        console.log("GA Initialized:", !!ReactGA.ga());
        console.log("Debug Mode:", DEBUG_MODE);
        console.log("Current Page:", window.location.pathname);
        console.groupEnd();
    }, []);

    return null;
};

export default DebugGA;
