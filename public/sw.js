const CACHE = 'gestao-v2';
const STATIC = ['/index.html', '/manifest.json', '/icon.svg'];
const SKIP = ['gstatic.com', 'googleapis.com', 'firebase', 'jsdelivr.net', 'tailwindcss.com', 'firebaseio.com'];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC).catch(() => {})));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = e.request.url;
  if (SKIP.some(d => url.includes(d))) {
    e.respondWith(fetch(e.request).catch(() => new Response('', { status: 503 })));
    return;
  }
  e.respondWith(
    caches.match(e.request).then(cached =>
      cached || fetch(e.request).then(resp => {
        if (resp.ok) caches.open(CACHE).then(c => c.put(e.request, resp.clone()));
        return resp;
      })
    )
  );
});

self.addEventListener('push', e => {
  const d = e.data?.json() || { title: 'Gestão Familiar', body: '' };
  e.waitUntil(
    self.registration.showNotification(d.title, {
      body: d.body, icon: '/icon.svg', badge: '/icon.svg',
      tag: d.tag || 'default', data: d.url || '/'
    })
  );
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(clients.openWindow(e.notification.data || '/'));
});
