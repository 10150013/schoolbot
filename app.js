import { code128Svg } from "./code128.js";

const $ = id => document.getElementById(id);
const KEY = "fusion-member";
const DOUBLE_TAP_MS = 350, MAX_MOVE_PX = 25;

const store = {
  load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } },
  save(m) { try { localStorage.setItem(KEY, JSON.stringify(m)); } catch {} },
};
let member = store.load();
// Optional: open with ?code=ABC123&name=Jane to pre-fill (e.g. from a link in the member's welcome email)
const q = new URLSearchParams(location.search);
if (q.get("code")) { member = { code: q.get("code").toUpperCase(), name: q.get("name") || "" }; store.save(member); history.replaceState(null, "", location.pathname); }

function renderHome() {
  $("memberName").textContent = member.name || "";
  $("hint").textContent = member.code ? "Double-tap anywhere to show your check-in barcode" : "Set your member code to get started";
}

let wakeLock = null;
async function showBarcode() {
  if (!member.code) { openSetup(); return; }
  try { $("barcode").innerHTML = code128Svg(member.code); } catch (e) { alert("That code can't be turned into a barcode."); return; }
  $("codeText").textContent = member.code;
  $("overlay").hidden = false;
  try { wakeLock = await navigator.wakeLock?.request("screen"); } catch {}
}
function hideBarcode() { $("overlay").hidden = true; wakeLock?.release?.().catch(() => {}); wakeLock = null; }

// Double-tap detection (dblclick is unreliable on iOS, so use pointer events).
let last = null;
document.addEventListener("pointerup", e => {
  if ($("setup").open || e.target.closest("button")) return;
  const now = Date.now();
  if (last && now - last.t < DOUBLE_TAP_MS && Math.hypot(e.clientX - last.x, e.clientY - last.y) < MAX_MOVE_PX) {
    last = null;
    $("overlay").hidden ? showBarcode() : hideBarcode();
  } else last = { t: now, x: e.clientX, y: e.clientY };
});
document.addEventListener("dblclick", e => e.preventDefault());

function openSetup() {
  $("nameInput").value = member.name || ""; $("codeInput").value = member.code || ""; $("err").textContent = "";
  $("setup").showModal();
}
$("editBtn").onclick = openSetup;
$("cancelBtn").onclick = () => $("setup").close();
$("setupForm").addEventListener("submit", e => {
  const code = $("codeInput").value.trim().toUpperCase();
  try { code128Svg(code); } catch { e.preventDefault(); $("err").textContent = "Use letters, numbers and standard symbols only."; return; }
  member = { code, name: $("nameInput").value.trim() };
  store.save(member); renderHome();
});

renderHome();
if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
