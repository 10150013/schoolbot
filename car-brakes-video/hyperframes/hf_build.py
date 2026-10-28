#!/usr/bin/env python3
"""Build a HyperFrames project (1080x1920) from an episode script.
Usage: hf_build.py <episode.py> <project_dir>     (episode.py defines NAME, SCENES, VIS_NAMES)"""
import os, sys, json, math, re, importlib.util, shutil
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tiktok")); sys.path.insert(0, HERE)
import engine, soundfile as sf
from hf_vis_brakes import VIS, Tw

W, H = 1080, 1920
BAND_TOP = 168
BEAT = 0.5

def rgb(c): return "%d,%d,%d" % tuple(c[:3])
def hexc(c): return "#%02x%02x%02x" % tuple(c[:3])

def load_episode(path):
    spec = importlib.util.spec_from_file_location("ep", path); m = importlib.util.module_from_spec(spec); sys.modules["ep"] = m
    sys.path.insert(0, os.path.dirname(path)); spec.loader.exec_module(m); return m

SCENE_CSS = """
#root { position: absolute; inset: 0; font-family: 'Archivo Black', 'Inter', sans-serif; }
.badge { position: absolute; left: 0; width: 1080px; top: 176px; text-align: center; }
.badge span { display: inline-block; padding: 8px 32px; border-radius: 40px; background: @ACC@; color: #0f0820; font: 800 30px 'Inter', sans-serif; letter-spacing: .05em; }
.bar { position: absolute; left: 236px; top: 246px; width: 608px; height: 10px; display: flex; gap: 6px; }
.bar i { flex: 1; border-radius: 5px; background: #5a5082; overflow: hidden; position: relative; display: block; }
.bar b { position: absolute; left: 0; top: 0; bottom: 0; width: 100%; background: @ACC@; display: block; }
.title { position: absolute; left: 0; width: 1080px; top: 278px; text-align: center; line-height: 1.04; }
.title .l { display: block; font-size: @FS@px; color: #fff; paint-order: stroke fill; -webkit-text-stroke: 10px #0c061c; letter-spacing: .01em; }
.title .l2 { color: @ACC@; }
.title .w { display: inline-block; margin: 0 .15em; }
.vis { position: absolute; left: 94px; top: 455px; width: 891px; height: 660px; }
.vis svg { width: 891px; height: 660px; overflow: hidden; display: block; }
.lbl { position: absolute; left: 0; width: 1080px; top: 468px; text-align: center; }
.lbl span { display: inline-block; padding: 8px 30px; border-radius: 34px; background: #fff; color: #0f0820; font: 800 36px 'Inter', sans-serif; }
.stk { position: absolute; left: 0; width: 1080px; top: 1092px; text-align: center; }
.stk span { display: inline-block; padding: 12px 34px; border-radius: 28px; background: #ffe200; border: 6px solid #fff; color: #0f0820; font: 900 40px 'Inter', sans-serif; }
.cta-btn { position: absolute; left: 190px; top: 490px; width: 700px; height: 150px; border-radius: 75px; background: #fe2c55; border: 8px solid #fff; color: #fff; font-size: 84px; line-height: 134px; text-align: center; }
.cta-save { position: absolute; left: 0; width: 1080px; top: 676px; text-align: center; font-size: 50px; color: #fff; paint-order: stroke fill; -webkit-text-stroke: 8px #0c061c; }
.cta-next { position: absolute; left: 0; width: 1080px; top: 760px; text-align: center; }
.cta-next span { display: inline-block; padding: 10px 34px; border-radius: 40px; background: #ffe200; color: #0f0820; font: 800 40px 'Inter', sans-serif; }
.cta-em { position: absolute; top: 960px; font-size: 90px; line-height: 1; color: #fff; }
.cta-disc { position: absolute; left: 0; width: 1080px; top: 1040px; text-align: center; font: 800 30px/1.3 'Inter', sans-serif; color: #fff; }
"""

def build_scene(i, sc, vis_name, n_scenes, total_steps, vis_kw):
    D = round(sc["dur"], 3); P = f"s{i}-"; acc = hexc(sc["acc"]); first = i == 0; last = i == n_scenes - 1
    fn = VIS[vis_name]; v = fn(P, D, **vis_kw) if vis_kw else fn(P, D)
    tw = v["tw"]; step = sc.get("step")
    lines = sc["title"]; maxc = max(len(l) for l in lines)
    fs = min(84, int(860 / (maxc * .72)))
    def words(l, cls): return f'<span class="l {cls}">' + "".join(f'<span class="w">{w}</span>' for w in l.split()) + "</span>"
    title = f'<div id="{P}title" class="title">' + words(lines[0], "l1") + "".join(words(l, "l2") for l in lines[1:]) + "</div>"
    badge = f'<div id="{P}badge" class="badge"><span>{sc["badge"]}</span></div>'
    segs = []
    for k in range(total_steps):
        done = last or (step and k < step - 1); cur = bool(step and k == step - 1)
        segs.append(f'<i><b id="{P}seg{k}" style="width:{100 if done else (100 if cur else 0)}%"></b></i>')
    bar = f'<div class="bar">{"".join(segs)}</div>'
    labels = "".join(f'<div id="{P}lbl{j}" class="lbl"><span>{t}</span></div>' for j, (t, a, b) in enumerate(v["labels"]))
    stk = ""
    if "sticker" in sc:
        t, e, si = sc["sticker"]; stk = f'<div id="{P}stk" class="stk"><span>{e} {t}</span></div>'
    svg = f'<div id="{P}vis" class="vis"><svg viewBox="0 50 1080 800" xmlns="http://www.w3.org/2000/svg">{v["svg"]}</svg></div>' if v["svg"] else ""
    content = f'<div id="{P}content" class="clip" data-start="0" data-duration="{D}">{badge}{bar}{title}{svg}{v.get("html", "")}{labels}{stk}</div>'
    js = [f"const tl = gsap.timeline({{ paused: true }});"]
    # scene entry / exit: blur swap on one stage
    if not first:
        js.append(f'tl.fromTo("#{P}content", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: .18, ease: "power2.out" }}, 0);')
    js.append(f'tl.to("#{P}content", {{ opacity: 0, filter: "blur(8px)", duration: .15, ease: "power2.in" }}, {D - .15:.3f});')
    # title entrance varies by scene; the hook title is already on screen at frame 0
    mode = i % 3
    if not first:
        sel = f"#{P}title .w"
        if mode == 0:
            js.append(f'tl.fromTo("{sel}", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: .13, stagger: .067, ease: "power2.out" }}, .1);')
        elif mode == 1:
            js.append(f'tl.fromTo("#{P}title", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: .2, ease: "power2.out" }}, .1);')
        else:
            js.append(f'tl.fromTo("#{P}title .l1 .w", {{ opacity: 0, color: "#8b83b4" }}, {{ opacity: 1, color: "#ffffff", duration: .1, stagger: .09, ease: "none" }}, .1);')
            js.append(f'tl.fromTo("#{P}title .l2 .w", {{ opacity: 0, color: "#8b83b4" }}, {{ opacity: 1, color: "{acc}", duration: .1, stagger: .09, ease: "none" }}, .25);')
        js.append(f'tl.fromTo("#{P}badge", {{ opacity: 0 }}, {{ opacity: 1, duration: .12 }}, 0);')
        d = -1 if i % 2 else 1
        if v["svg"]:
            js.append(f'tl.fromTo("#{P}vis", {{ x: {d * 160}, scale: .92, opacity: 0, filter: "blur(10px)" }}, {{ x: 0, scale: 1, opacity: 1, filter: "blur(0px)", duration: .42, ease: "expo.out" }}, .08);')
    if step and 1 <= step <= total_steps:
        js.append(f'tl.fromTo("#{P}seg{step - 1}", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, transformOrigin: "0% 50%", duration: {D:.3f}, ease: "none" }}, 0);')
    for j, (t, a, b) in enumerate(v["labels"]):
        js.append(f'tl.fromTo("#{P}lbl{j}", {{ opacity: 0, y: 12 }}, {{ opacity: 1, y: 0, duration: .22, ease: "power3.out" }}, {a * D:.3f});')
        if b is not None: js.append(f'tl.to("#{P}lbl{j}", {{ opacity: 0, duration: .12 }}, {b * D:.3f});')
    if "sticker" in sc:
        st0 = sc["sents"][sc["sticker"][2]]["start"] - sc["start"]
        js.append(f'tl.fromTo("#{P}stk", {{ opacity: 0, scale: .5, rotation: -14, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, rotation: -4, duration: .45, ease: "back.out(1.8)" }}, {st0:.3f});')
    js += tw.l
    js.append(f'window.__timelines["s{i}"] = tl;')
    css = SCENE_CSS.replace("@ACC@", acc).replace("@FS@", str(fs))
    return (f'<template>\n<style>{css}</style>\n<div id="root" data-composition-id="s{i}" data-width="{W}" data-height="{H}">\n{content}\n</div>\n'
            f'<script>\n{chr(10).join(js)}\n</script>\n</template>\n')

CAP_TEMPLATE = """<template>
<style>
#root { position: absolute; inset: 0; }
.cg { position: absolute; left: 0; width: 960px; top: 1196px; height: 130px; display: flex; align-items: center; justify-content: center; visibility: hidden; opacity: 0; }
.cp { padding: 12px 34px 16px; border-radius: 30px; background: rgba(12,6,28,.88); border: 5px solid var(--acc); white-space: nowrap; display: flex; gap: 22px; }
.cw { font: 400 78px/1.1 'Archivo Black', sans-serif; color: rgba(255,255,255,.55); text-transform: uppercase; display: inline-block; }
</style>
<div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
  <div id="cap-stage" class="clip" data-start="0" data-duration="@T@"></div>
</div>
<script>
const GROUPS = @GROUPS@;
const stage = document.getElementById("cap-stage");
GROUPS.forEach(function (g, gi) {
  const el = document.createElement("div"); el.id = "cg" + gi; el.className = "cg"; el.style.setProperty("--acc", g.acc);
  const pill = document.createElement("div"); pill.className = "cp";
  g.words.forEach(function (w, wi) { const s = document.createElement("span"); s.id = "cw" + gi + "-" + wi; s.className = "cw"; s.textContent = w.t; pill.appendChild(s); });
  el.appendChild(pill); stage.appendChild(el);
});
const tl = gsap.timeline({ paused: true });
GROUPS.forEach(function (g, gi) {
  const sel = "#cg" + gi;
  tl.set(sel, { visibility: "visible" }, g.start);
  tl.fromTo(sel, { opacity: 0, scale: .88 }, { opacity: 1, scale: 1, duration: .12, ease: "power3.out" }, g.start);
  g.words.forEach(function (w, wi) {
    tl.to("#cw" + gi + "-" + wi, { color: g.acc, duration: .08, ease: "none" }, Math.max(g.start, w.s - .02));
  });
  tl.to(sel, { opacity: 0, duration: .1, ease: "power2.in" }, g.end - .1);
  tl.set(sel, { opacity: 0, visibility: "hidden" }, g.end);
});
window.__timelines["captions"] = tl;
</script>
</template>
"""

def caption_groups(TL):
    groups = []
    for sc in TL:
        for s in sc["sents"]:
            for ch in s["chunks"]:
                ws = [dict(t=s["words"][k].lower(), s=round(s["wtimes"][k][0], 3), e=round(s["wtimes"][k][1], 3)) for k in ch]
                groups.append(dict(words=ws, start=max(.1, ws[0]["s"]), end=ws[-1]["e"] + .22, acc=hexc(sc["acc"]), scene_end=sc["end"]))
    for a, b in zip(groups, groups[1:]): a["end"] = min(a["end"], b["start"] + .0 if b["start"] > a["start"] else a["end"])
    for g in groups: g["end"] = min(g["end"], g["scene_end"]); g.pop("scene_end")
    return groups

def build(ep, outdir, vis_names):
    engine.SCENES = ep.SCENES; engine.NO_DING = True
    total = engine.init(); TL = engine.TL
    os.makedirs(os.path.join(outdir, "compositions"), exist_ok=True); os.makedirs(os.path.join(outdir, "assets", "vendor"), exist_ok=True)
    shutil.copy(os.path.join(HERE, "vendor", "gsap.min.js"), os.path.join(outdir, "assets", "vendor", "gsap.min.js"))  # no CDN: the render browser may be offline
    # audio stems from the same voice/music/sfx used for the earlier cut
    engine.make_audio(TL, total); S = engine.STEMS
    def peak(x): return float(np.abs(x).max()) or 1.0
    voice = S["voice"] / peak(S["voice"]) * .85
    music = S["music"] * .8; sfx = S["sfx"] * .8
    sf.write(os.path.join(outdir, "assets", "voice.wav"), voice, engine.SR, subtype="PCM_16")
    sf.write(os.path.join(outdir, "assets", "music.wav"), music, engine.SR, subtype="PCM_16")
    sf.write(os.path.join(outdir, "assets", "sfx.wav"), sfx, engine.SR, subtype="PCM_16")
    n = len(TL); total_steps = engine.NSTEPS
    T = round(total, 3)
    hosts, glows, tl_js = [], [], []
    for i, sc in enumerate(TL):
        kw = {}
        if vis_names[i] == "cta": kw = dict(nxt=getattr(ep, "NEXT", None))
        html = build_scene(i, sc, vis_names[i], n, total_steps, kw)
        open(os.path.join(outdir, "compositions", f"s{i}.html"), "w").write(html)
        hosts.append(f'<div id="s{i}" data-composition-id="s{i}" data-composition-src="compositions/s{i}.html" data-start="{sc["start"]:.3f}" data-duration="{sc["dur"]:.3f}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>')
        a = rgb(sc["acc"])
        glows.append(f'<div id="glow{i}" class="glow" style="background:radial-gradient(circle at 50% 50%, rgba({a},.62) 0%, rgba({a},0) 62%)"></div>')
        st, en = sc["start"], sc["end"]
        if i == 0: tl_js.append(f'tl.set("#glow0", {{ opacity: 1 }}, 0);')
        else: tl_js.append(f'tl.fromTo("#glow{i}", {{ opacity: 0 }}, {{ opacity: 1, duration: .4, ease: "power2.inOut" }}, {st - .1:.3f});')
        if i < n - 1: tl_js.append(f'tl.to("#glow{i}", {{ opacity: 0, duration: .4, ease: "power2.inOut" }}, {en - .1:.3f});')
    groups = caption_groups(TL)
    open(os.path.join(outdir, "compositions", "captions.html"), "w").write(CAP_TEMPLATE.replace("@GROUPS@", json.dumps(groups)).replace("@T@", str(T)))
    hosts.append(f'<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{T}" data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}"></div>')
    beats = "\n".join(f'tl.fromTo("#glowwrap", {{ scale: 1.05 }}, {{ scale: 1, duration: .4, ease: "power2.out"{"" if k == 0 else ", immediateRender: false"} }}, {k * BEAT:.3f});' for k in range(int(T / BEAT) + 1))
    audio = (f'<audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{T}" data-track-index="10" data-volume="1"></audio>\n'
             f'<audio id="music" src="assets/music.wav" data-start="0" data-duration="{T}" data-track-index="11" data-volume="1"></audio>\n'
             f'<audio id="sfx" src="assets/sfx.wav" data-start="0" data-duration="{T}" data-track-index="12" data-volume="1"></audio>')
    index = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<script src="assets/vendor/gsap.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #0e0a24; }}
#bg {{ position: absolute; inset: 0; background: linear-gradient(180deg, #0e0a24 0%, #2c0e4a 100%); }}
#stripes {{ position: absolute; left: -2400px; top: -200px; width: 5200px; height: 2400px; background: repeating-linear-gradient(115deg, rgba(255,255,255,.035) 0 40px, rgba(255,255,255,0) 40px 80px); }}
#glowwrap {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; }}
.glow {{ position: absolute; left: -200px; top: 190px; width: 1480px; height: 1480px; border-radius: 50%; opacity: 0; }}
#vignette {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,.5) 100%); }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="{W}" data-height="{H}">
<div id="bg"></div>
<div id="stripes"></div>
<div id="glowwrap">{"".join(glows)}</div>
<div id="vignette"></div>
{chr(10).join(hosts)}
{audio}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
tl.to("#stripes", {{ x: {-T * 40:.0f}, duration: {T}, ease: "none" }}, 0);
{chr(10).join(tl_js)}
{beats}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
"""
    open(os.path.join(outdir, "index.html"), "w").write(index)
    print("built", outdir, "T=", T, "scenes", n)

if __name__ == "__main__":
    ep = load_episode(os.path.abspath(sys.argv[1])); out = os.path.abspath(sys.argv[2])
    build(ep, out, ep.VIS_NAMES)
