const CACHE = "stek-v85";
const CORE = ["./", "index.html", "manifest.json", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "icon-maskable.png", "logo-s.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE.map(u => new Request(u, { cache: "reload" })))).then(() => self.skipWaiting())); });
const CRON_CACHE = "stek-cron"; // pausas tocadas na notificação do cronômetro, aplicadas quando o app abre
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE && k !== CRON_CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
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
const ICON = "icon-192.png?v=4";
const pausasUrl = () => new URL("pausas", self.registration.scope).href;
function cronPausas() { return caches.open(CRON_CACHE).then(c => c.match(pausasUrl())).then(r => r ? r.json() : []).catch(() => []); }
function cronSalvar(list) { return caches.open(CRON_CACHE).then(c => c.put(pausasUrl(), new Response(JSON.stringify(list), { headers: { "Content-Type": "application/json" } }))); }
function hm(ms) { const d = new Date(ms); return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0"); }
function cronPausada(tag, title, at, url) {
  return self.registration.showNotification("⏸ " + title, { tag, body: "Pausado às " + hm(at) + ". O tempo já para de contar; toque para abrir o app.", silent: true, renotify: false, icon: ICON, badge: ICON, data: { url } });
}
// Avisos da Rotina (enviados pelo servidor alguns minutos antes de cada tarefa)
self.addEventListener("push", e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (x) { d = { title: "STEK", body: e.data ? e.data.text() : "" }; }
  // fim de sessão com tempo: substitui a notificação do cronômetro (a não ser que já tenha sido pausado pela notificação)
  const m = /^cron-end-([a-z]+)-(\d+)$/.exec(d.tag || "");
  if (m) {
    const tag = "stek-cron-" + m[1];
    e.waitUntil(cronPausas().then(list => {
      const p = list.find(x => x.mod === m[1] && String(x.start) === m[2]);
      if (p) return cronPausada(tag, p.title || "Cronômetro", p.at, d.url || "./");
      return self.registration.showNotification(d.title || "STEK", { body: d.body || "", tag, renotify: true, icon: ICON, badge: ICON, data: { url: d.url || "./" } });
    }));
    return;
  }
  e.waitUntil(self.registration.showNotification(d.title || "STEK", {
    body: d.body || "", tag: d.tag || "stek", renotify: true,
    icon: ICON, badge: ICON, data: { url: d.url || "./" }
  }));
});
self.addEventListener("notificationclick", e => {
  const d = e.notification.data || {};
  // Pausar no cronômetro: guarda a hora e avisa o app (se estiver aberto em segundo plano); sem abrir o app
  if (e.action === "pausar" && d.cron) {
    const at = Date.now();
    e.waitUntil(cronPausas().then(list => cronSalvar(list.filter(x => x.mod !== d.cron).concat({ mod: d.cron, at, start: d.start, title: d.title })))
      .then(() => cronPausada(e.notification.tag, d.title || "Cronômetro", at, d.url || "./"))
      .then(() => self.clients.matchAll({ type: "window", includeUncontrolled: true }))
      .then(list => list.forEach(c => c.postMessage({ type: "stek-cron" }))));
    return;
  }
  e.notification.close();
  const url = new URL((e.notification.data && e.notification.data.url) || "./", self.registration.scope);
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(list => {
    const c = list.find(x => x.url.startsWith(self.registration.scope));
    if (c) { c.postMessage({ type: "stek-go", hash: url.hash }); return c.focus(); }
    return self.clients.openWindow(url.href);
  }));
});
