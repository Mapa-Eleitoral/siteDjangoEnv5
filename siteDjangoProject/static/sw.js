// Service Worker básico para evitar 404
// Cache estratégia conservadora
const CACHE_NAME = 'mapa-eleitoral-v1';
const urlsToCache = [
  '/',
  '/static/favicon.ico'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  // Apenas para requests GET
  if (event.request.method !== 'GET') return;
  
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});