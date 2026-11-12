const CACHE = "stek-v39";
const CORE = ["./", "index.html", "manifest.json", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "icon-maskable.png", "logo-s.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE.map(u => new Request(u, { cache: "reload" })))).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== self.location.origin) return; // só guarda os arquivos do app, nunca respostas do servidor
  // Sempre pergunta ao servidor se há versão nova (ignora o cache do navegador); sem internet, usa a cópia guardada.
  e.respondWith(
    fetch(e.request, { cache: "no-cache" }).then(res => {
      if (res && (res.ok || res.type === "opaque")) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    }).catch(() => caches.match(e.request).then(r => r || caches.match("index.html")))
  );
});
// Avisos da Rotina (enviados pelo servidor alguns minutos antes de cada tarefa)
self.addEventListener("push", e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (x) { d = { title: "STEK", body: e.data ? e.data.text() : "" }; }
  e.waitUntil(self.registration.showNotification(d.title || "STEK", {
    body: d.body || "", tag: d.tag || "stek", renotify: true,
    icon: "icon-192.png?v=4", badge: "icon-192.png?v=4", data: { url: d.url || "./" }
  }));
});
self.addEventListener("notificationclick", e => {
  e.notification.close();
  const url = new URL((e.notification.data && e.notification.data.url) || "./", self.registration.scope);
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(list => {
    const c = list.find(x => x.url.startsWith(self.registration.scope));
    if (c) { c.postMessage({ type: "stek-go", hash: url.hash }); return c.focus(); }
    return self.clients.openWindow(url.href);
  }));
});
