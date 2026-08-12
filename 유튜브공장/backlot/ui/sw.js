const CACHE_NAME = "ytf-shell-v1";
const APP_SHELL = [
  "/mobile",
  "/ui/mobile.css",
  "/ui/mobile.js",
  "/manifest.webmanifest",
  "/ui/icons/icon-192.png",
  "/ui/icons/icon-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/media/") || url.pathname.startsWith("/thumb/")) {
    event.respondWith(fetch(request, { cache: "no-store" }));
    return;
  }
  if (!APP_SHELL.includes(url.pathname)) return;
  event.respondWith(caches.match(request).then(cached => cached || fetch(request)));
});
