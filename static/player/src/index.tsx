import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App.tsx";

// Detect if the app is loaded in an iframe and add the iframe-mode class to the body
if (window.self !== window.top) {
    document.body.classList.add("iframe-mode");
}

// if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
//     document.documentElement.classList.add("dark");
// } else {
//     document.documentElement.classList.remove("dark");
// }

// window
//     .matchMedia("(prefers-color-scheme: dark)")
//     .addEventListener("change", (event) => {
//         if (event.matches) {
//             document.documentElement.classList.add("dark");
//         } else {
//             document.documentElement.classList.remove("dark");
//         }
//     });

const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement
);

root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
