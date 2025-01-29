self.addEventListener("install", (event) => {
    self.skipWaiting(); // Activate the new service worker immediately
    event.waitUntil(
        caches.open("app-cache").then((cache) => {
            return cache.addAll([
                "/", // Add the root and other necessary assets
                "/index.html",
                "/manifest.json",
                "/static/js/bundle.js",
                "/static/css/main.css"
            ]);
        })
    );
});

self.addEventListener("activate", (event) => {
    self.clients.claim(); // Take control of all open pages
});

self.addEventListener("fetch", (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});
