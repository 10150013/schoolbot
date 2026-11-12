import { code128Svg } from "./code128.js";

const $ = id => document.getElementById(id);
const KEY = "gym-cards-v2", OLD_KEY = "fusion-member";
const DOUBLE_TAP_MS = 350, MAX_MOVE_PX = 25;

// ---- storage ----
const read = k => { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } };
let state = read(KEY) || { cards: [], active: null };
if (!state.cards.length) { // migrate the single-card version
  const old = read(OLD_KEY);
  if (old?.code) { const c = { id: uid(), name: old.name || "Fusion Gyms", type: "code128", code: old.code }; state = { cards: [c], active: c.id }; }
}
const q = new URLSearchParams(location.search); // ?code=ABC&name=Gym still adds a typed card
if (q.get("code")) { const c = { id: uid(), name: q.get("name") || "Gym", type: "code128", code: q.get("code").toUpperCase() }; state.cards.push(c); state.active = c.id; history.replaceState(null, "", location.pathname); }
function uid() { return Math.random().toString(36).slice(2, 10); }
function save() {
  try { localStorage.setItem(KEY, JSON.stringify(state)); return true; }
  catch { alert("Not enough storage on this phone for that photo. Try a smaller crop."); return false; }
}
const active = () => state.cards.find(c => c.id === state.active) || state.cards[0];

// ---- home list ----
function renderHome() {
  $("hint").textContent = state.cards.length ? "Double-tap anywhere to show your selected card" : "Add your first card to get started";
  const ul = $("list"); ul.innerHTML = "";
  for (const c of state.cards) {
    const li = document.createElement("li");
    const sel = document.createElement("button");
    sel.className = "pick" + (c.id === active()?.id ? " on" : ""); sel.textContent = (c.id === active()?.id ? "● " : "○ ") + c.name;
    sel.onclick = () => { state.active = c.id; save(); renderHome(); };
    const ed = document.createElement("button"); ed.textContent = "Edit"; ed.onclick = () => openSetup(c);
    const del = document.createElement("button"); del.textContent = "Delete";
    del.onclick = () => { if (confirm(`Delete ${c.name}?`)) { state.cards = state.cards.filter(x => x.id !== c.id); if (state.active === c.id) state.active = state.cards[0]?.id ?? null; save(); renderHome(); } };
    li.append(sel, ed, del); ul.append(li);
  }
}

// ---- overlay ----
let wakeLock = null;
async function showCard() {
  const c = active(); if (!c) { openSetup(); return; }
  if (c.type === "image") { const img = new Image(); img.alt = c.name; img.src = c.img; $("barcode").replaceChildren(img); $("codeText").textContent = ""; }
  else { $("barcode").innerHTML = code128Svg(c.code); $("codeText").textContent = c.code; }
  $("overlay").hidden = false;
  try { wakeLock = await navigator.wakeLock?.request("screen"); } catch {}
}
function hideCard() { $("overlay").hidden = true; wakeLock?.release?.().catch(() => {}); wakeLock = null; }

let last = null;
document.addEventListener("pointerup", e => {
  if ($("setup").open || e.target.closest("button, input, select, label")) return;
  const now = Date.now();
  if (last && now - last.t < DOUBLE_TAP_MS && Math.hypot(e.clientX - last.x, e.clientY - last.y) < MAX_MOVE_PX) {
    last = null; $("overlay").hidden ? showCard() : hideCard();
  } else last = { t: now, x: e.clientX, y: e.clientY };
});
document.addEventListener("dblclick", e => e.preventDefault());

// ---- add / edit dialog ----
let editing = null, srcImg = null;
const crop = $("cropCanvas"), sl = ["cl", "ct", "cr", "cb"].map($);
function syncType() { const img = $("typeInput").value === "image"; $("imageBox").hidden = !img; $("codeBox").hidden = img; }
$("typeInput").onchange = syncType;
function drawCrop() {
  if (!srcImg) return;
  const [l, t, r, b] = sl.map(s => +s.value / 100);
  const sx = srcImg.width * l, sy = srcImg.height * t, sw = srcImg.width * (1 - l - r), sh = srcImg.height * (1 - t - b);
  const scale = Math.min(1, 1000 / Math.max(sw, sh));
  crop.width = Math.max(1, Math.round(sw * scale)); crop.height = Math.max(1, Math.round(sh * scale));
  const g = crop.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, crop.width, crop.height);
  g.drawImage(srcImg, sx, sy, sw, sh, 0, 0, crop.width, crop.height);
}
sl.forEach(s => s.oninput = drawCrop);
$("fileInput").onchange = e => {
  const f = e.target.files[0]; if (!f) return;
  const img = new Image(); const url = URL.createObjectURL(f);
  img.onload = () => { srcImg = img; sl.forEach(s => s.value = 0); crop.hidden = false; $("sliders").hidden = false; drawCrop(); URL.revokeObjectURL(url); };
  img.onerror = () => { $("err").textContent = "Could not open that photo."; };
  img.src = url;
};
function openSetup(card = null) {
  editing = card; srcImg = null; $("err").textContent = ""; $("fileInput").value = ""; crop.hidden = true; $("sliders").hidden = true;
  $("nameInput").value = card?.name ?? ""; $("typeInput").value = card?.type ?? "image"; $("codeInput").value = card?.code ?? "";
  syncType(); $("setup").showModal();
}
$("addBtn").onclick = () => openSetup();
$("cancelBtn").onclick = () => $("setup").close();
$("setupForm").addEventListener("submit", e => {
  const name = $("nameInput").value.trim(), type = $("typeInput").value;
  const card = editing ? { ...editing } : { id: uid() };
  Object.assign(card, { name, type });
  if (type === "code128") {
    const code = $("codeInput").value.trim().toUpperCase();
    try { if (!code) throw 0; code128Svg(code); } catch { e.preventDefault(); $("err").textContent = "Enter a code using letters, numbers and standard symbols."; return; }
    card.code = code; delete card.img;
  } else {
    if (srcImg) card.img = crop.toDataURL("image/png");
    if (!card.img) { e.preventDefault(); $("err").textContent = "Choose a photo first."; return; }
    delete card.code;
  }
  if (editing) state.cards = state.cards.map(c => c.id === card.id ? card : c); else state.cards.push(card);
  if (!state.active || !editing) state.active = card.id;
  if (!save()) e.preventDefault();
  renderHome();
});

renderHome();
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
