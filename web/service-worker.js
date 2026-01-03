// Civilization OS - Unified Service Worker (v2.0)
// Strategy: Network-First (App Files) | Cache-First (CDN/Assets) | Offline Queue (API)

const CACHE_NAME = 'civ-os-pwa-v2.1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/mesh.html',
    '/mesh_visualizer.js',
    '/app.js',
    '/style.css',
    '/ui_config.json',
    '/manifest.json',
    '/activity_feed.js',
    '/engagement.js',
    '/sound_engine.js',
    '/mobility_module.js',
    '/hardware_monitor.js',
    '/seh7_quests.json',
    '/seed_quests.json',
    '/truck_quests.json',
    '/fbcc_roles.json',
    '/icon-192.png',
    '/icon-512.png'
];

const CDN_ASSETS = [
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap',
    'https://d3js.org/d3.v7.min.js',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
    'https://cdn.jsdelivr.net/npm/marked/marked.min.js'
];

// IndexedDB for Offline Queue
const DB_NAME = 'CivOS_Offline';
const STORE_NAME = 'request_queue';

async function getDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, 1);
        request.onupgradeneeded = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
            }
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

// Install: Pre-cache CDN assets (since they rarely change)
self.addEventListener('install', event => {
    console.log('[SW] Installing Unified Service Worker...');
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(CDN_ASSETS))
    );
    self.skipWaiting();
});

// Activate: Clean old caches from legacy service workers
self.addEventListener('activate', event => {
    console.log('[SW] Activating and purging legacy caches...');
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.map(key => {
                    if (key !== CACHE_NAME) return caches.delete(key);
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch Logic
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // 1. API Requests Handler
    // 1. API Requests Handler
    if (url.pathname.startsWith('/api/')) {
        if (event.request.method === 'POST') {
            // Queue POST requests if offline
            event.respondWith(
                fetch(event.request.clone()).catch(async () => {
                    await queueRequest(event.request.clone());
                    return new Response(JSON.stringify({
                        status: 'queued',
                        message: 'System offline. Transaction queued for sync.'
                    }), { headers: { 'Content-Type': 'application/json' } });
                })
            );
        }
        // For GET requests to API, we RETURN (allow network pass-through)
        // This prevents the SW from breaking local dev calls or returning weird cached responses
        return;
    }

    // 2. CDN & Assets: Cache-First
    if (CDN_ASSETS.includes(event.request.url) || url.pathname.endsWith('.png') || url.pathname.endsWith('.jpg')) {
        event.respondWith(
            caches.match(event.request).then(cached => {
                return cached || fetch(event.request).then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                    }
                    return response;
                });
            })
        );
        return;
    }

    // 3. Local Web Files: Network-First (Ensure freshness)
    event.respondWith(
        fetch(event.request)
            .then(response => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
                }
                return response;
            })
            .catch(() => {
                return caches.match(event.request).then(matched => {
                    return matched || new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
                });
            })
    );
});

// Background Sync Logic
async function queueRequest(request) {
    const body = await request.text();
    const db = await getDB();
    const tx = db.transaction(STORE_NAME, 'readwrite');
    const entry = {
        url: request.url,
        method: request.method,
        body: body,
        headers: Object.fromEntries(request.headers.entries()),
        timestamp: Date.now()
    };
    return new Promise((resolve) => {
        tx.objectStore(STORE_NAME).add(entry);
        tx.oncomplete = () => {
            console.log('[SW] Request queued for sync');
            resolve();
        };
    });
}

self.addEventListener('sync', event => {
    if (event.tag === 'sync-queue') {
        event.waitUntil(processQueue());
    }
});

async function processQueue() {
    const db = await getDB();
    const tx = db.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    const requests = await new Promise(resolve => {
        const req = store.getAll();
        req.onsuccess = () => resolve(req.result);
    });

    for (const req of requests) {
        try {
            const response = await fetch(req.url, {
                method: req.method,
                body: req.body,
                headers: req.headers
            });
            if (response.ok) {
                const deleteTx = db.transaction(STORE_NAME, 'readwrite');
                deleteTx.objectStore(STORE_NAME).delete(req.id);
            }
        } catch (e) {
            console.warn('[SW] Sync failed for item, retrying later:', req.url);
        }
    }
}
