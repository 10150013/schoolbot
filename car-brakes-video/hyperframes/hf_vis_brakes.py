"""Scene visuals for the brake episode: each returns dict(svg, html, tw, labels)."""
import json, math
from hf_shapes import *

class Tw:
    def __init__(s): s.l = []
    def fromto(s, sel, frm, to, at): s.l.append(f'tl.fromTo({json.dumps(sel)}, {json.dumps(frm)}, {json.dumps(to)}, {at:.3f});')
    def to(s, sel, vars, at): s.l.append(f'tl.to({json.dumps(sel)}, {json.dumps(vars)}, {at:.3f});')
    def set(s, sel, vars, at): s.l.append(f'tl.set({json.dumps(sel)}, {json.dumps(vars)}, {at:.3f});')

YEL, LIME, RED, INK = "#ffe200", "#b6ff00", "#fe2c55", "#0c061c"

def v_hook(P, D, **kw):
    u = lambda x: x * D; w = Tw()
    spots = [(-330, -120), (320, -150), (350, 90), (-300, 120)]
    stars = "".join(g(poly(star_pts(540 + dx, 640 + dy, 26), YEL), id=f"{P}st{i}") for i, (dx, dy) in enumerate(spots))
    svg = (text(540, 210, kw.get("old", "$400"), 300, "#fff", stroke=INK, sw=10) + text(540, 400, kw.get("lab_old", "TYPICAL SHOP QUOTE"), 44, "#cdd2e8", font="Inter", weight=800)
           + line(160, 320, 160, 320, RED, 26, id=f"{P}strike", opacity=0)
           + g(text(540, 640, kw.get("new", "$60"), 300, LIME, stroke=INK, sw=10) + text(540, 820, kw.get("lab_new", "PADS COST ABOUT THAT"), 44, "#cdd2e8", font="Inter", weight=800) + stars, id=f"{P}new")
           + emoji(120, 400, kw.get("e1", "💸"), 100, id=f"{P}e1", fill="#fff") + emoji(960, 400, kw.get("e2", "🔧"), 100, id=f"{P}e2", fill="#fff"))
    w.fromto(f"#{P}strike", {"attr": {"x2": 160, "y2": 320}, "opacity": 0}, {"attr": {"x2": 920, "y2": 110}, "opacity": 1, "duration": u(.14), "ease": "power3.out"}, u(.22))
    w.fromto(f"#{P}new", {"opacity": 0, "scale": .2, "svgOrigin": "540 640"}, {"opacity": 1, "scale": 1, "svgOrigin": "540 640", "duration": .5, "ease": "back.out(1.4)"}, u(.40))
    for i, (dx, dy) in enumerate(spots):
        w.fromto(f"#{P}st{i}", {"scale": 0, "svgOrigin": f"{540 + dx} {640 + dy}"}, {"scale": 1, "svgOrigin": f"{540 + dx} {640 + dy}", "duration": .3, "ease": "back.out(2)"}, u(.5) + i * .06)
    w.to(f"#{P}e1", {"y": -10, "duration": .55, "ease": "sine.inOut", "repeat": 6, "yoyo": True}, 0)
    w.to(f"#{P}e2", {"y": -10, "duration": .55, "ease": "sine.inOut", "repeat": 6, "yoyo": True}, .27)
    return dict(svg=svg, tw=w, labels=[])

def v_lift(P, D):
    u = lambda x: x * D; w = Tw()
    car = rr(40, 120, 1040, 470, 60, fill=(66, 72, 108), stroke=(110, 118, 160), sw=4) + ell(540, 520, 306, fill=(26, 20, 52)) + wheel(540, 520, 280, id=f"{P}wheel")
    svg = line(30, 800, 1050, 800, (130, 136, 160), 8) + g(car, id=f"{P}car") + stand(120, 800, 440, id=f"{P}stand")
    w.to(f"#{P}wheel", {"rotation": -28.6, "svgOrigin": "540 520", "duration": u(.3), "ease": "power2.inOut"}, u(.05))
    w.to(f"#{P}car", {"y": -50, "duration": u(.2), "ease": "power2.inOut"}, u(.42))
    w.fromto(f"#{P}stand", {"scaleY": 0, "opacity": 0, "svgOrigin": "120 800"}, {"scaleY": 1, "opacity": 1, "svgOrigin": "120 800", "duration": u(.17), "ease": "back.out(1.3)"}, u(.55))
    return dict(svg=svg, tw=w, labels=[("LOOSEN ½ TURN", .05, .40)])

def v_wheeloff(P, D):
    u = lambda x: x * D; w = Tw()
    svg = rotor(540, 450, 300, id=f"{P}rotor") + caliper(540, 450, 300) + g(wheel(540, 450, 300, id=f"{P}wspin"), id=f"{P}wheel")
    w.to(f"#{P}rotor", {"rotation": 91.7 * D, "svgOrigin": "540 450", "duration": D, "ease": "none"}, 0)
    w.to(f"#{P}wheel", {"x": 900, "duration": u(.52), "ease": "power2.out"}, u(.08))
    w.to(f"#{P}wspin", {"rotation": 172, "svgOrigin": "540 450", "duration": u(.52), "ease": "power2.out"}, u(.08))
    w.to(f"#{P}wheel", {"y": 40, "duration": u(.52), "ease": "power2.in"}, u(.08))
    return dict(svg=svg, tw=w, labels=[("ROTOR + CALIPER", .55, None)])

def v_caliper(P, D):
    u = lambda x: x * D; w = Tw()
    cy = 490
    bolts = "".join(g(bolt(756, cy + dy, 24, id=f"{P}bs{i}"), id=f"{P}b{i}") for i, dy in enumerate((-135, 135)))
    svg = rotor(540, cy, 300, id=f"{P}rotor") + caliper(540, cy, 300, id=f"{P}cal")
    svg += line(790, 70, 750, 304, "#ff8c00", 9, id=f"{P}wire", opacity=0) + ell(790, 60, 18, stroke="#ff8c00", sw=8, id=f"{P}ring", opacity=0) + bolts
    w.to(f"#{P}rotor", {"rotation": 34 * D, "svgOrigin": f"540 {cy}", "duration": D, "ease": "none"}, 0)
    for i, dy in enumerate((-135, 135)):
        w.to(f"#{P}b{i}", {"x": 120, "duration": u(.26), "ease": "power2.out"}, u(.10))
        w.to(f"#{P}bs{i}", {"rotation": 825, "svgOrigin": f"756 {cy + dy}", "duration": u(.26), "ease": "power2.out"}, u(.10))
        w.to(f"#{P}b{i}", {"x": 160, "y": 120, "duration": u(.36), "ease": "power3.out"}, u(.42))
    w.to(f"#{P}cal", {"x": 150, "y": 230, "duration": u(.36), "ease": "power3.out"}, u(.42))
    w.to(f"#{P}wire", {"opacity": 1, "duration": .12}, u(.42)); w.to(f"#{P}ring", {"opacity": 1, "duration": .12}, u(.42))
    w.to(f"#{P}wire", {"attr": {"x2": 900, "y2": 534}, "duration": u(.36), "ease": "power3.out"}, u(.42))
    return dict(svg=svg, tw=w, labels=[])

def v_pads(P, D):
    u = lambda x: x * D; w = Tw()
    svg = edge_rotor() + pad_left(500, 210, 560, 14, id=f"{P}pl") + pad_right(580, 210, 560, 14, id=f"{P}pr")
    svg += arrow(330, 385, 150, 385, YEL, id=f"{P}al") + arrow(750, 385, 930, 385, YEL, id=f"{P}ar")
    w.to(f"#{P}pl", {"x": -330, "duration": u(.5), "ease": "power2.inOut"}, u(.22)); w.to(f"#{P}pr", {"x": 330, "duration": u(.5), "ease": "power2.inOut"}, u(.22))
    for k in ("al", "ar"): w.fromto(f"#{P}{k}", {"opacity": 0}, {"opacity": 1, "duration": .2}, u(.3))
    return dict(svg=svg, tw=w, labels=[("WORN OUT = THIN", .50, None)])

def v_piston(P, D):
    u = lambda x: x * D; w = Tw()
    ridges = "".join(line(540 + 22 + i * 26, 392, 540 + 22 + i * 26, 608, (140, 146, 160), 3) for i in range(3))
    pist = rr(540, 380, 790, 620, 8, fill=(196, 202, 214), stroke=(120, 126, 140), sw=3) + ridges + rr(504, 350, 540, 650, 6, fill=(120, 74, 40))
    svg = rr(600, 280, 900, 720, 30, fill=(228, 40, 62), stroke=(255, 130, 140), sw=4) + rr(600, 360, 790, 640, 8, fill=(18, 16, 26)) + g(pist, id=f"{P}pg")
    svg += rr(150, 230, 975, 268, 10, fill=(170, 176, 190)) + rr(150, 230, 192, 720, 10, fill=(170, 176, 190)) + rr(905, 230, 945, 720, 10, fill=(170, 176, 190))
    svg += rr(112, 480, 504, 520, 6, fill=(220, 225, 236), id=f"{P}rod")
    svg += g(line(100, 380, 100, 620, "#fff", 16) + ell(100, 380, 14, fill=YEL) + ell(100, 620, 14, fill=YEL), id=f"{P}hd")
    span = u(.73)
    w.to(f"#{P}pg", {"x": 100, "duration": span, "ease": "power1.inOut"}, u(.12))
    w.to(f"#{P}rod", {"attr": {"width": 492}, "duration": span, "ease": "power1.inOut"}, u(.12))
    w.to(f"#{P}hd", {"scaleY": .08, "svgOrigin": "100 500", "duration": span / 10, "ease": "sine.inOut", "repeat": 9, "yoyo": True}, u(.12))
    return dict(svg=svg, tw=w, labels=[("SQUEEZE SLOWLY", .10, None)])

def v_install(P, D):
    u = lambda x: x * D; w = Tw()
    cal = "".join((rr(402, 120, 678, 190, 18), rr(402, 120, 452, 560, 18), rr(628, 120, 678, 560, 18)))
    cal = g("".join(rr(*a, 18, fill=(228, 40, 62), stroke=(255, 130, 140), sw=4) for a in ((402, 120, 678, 190), (402, 120, 452, 560), (628, 120, 678, 560))), id=f"{P}cal")
    bolts = g("".join(rr(bx - 14, 40, bx + 14, 150, 6, fill=(215, 220, 230)) for bx in (500, 580)), id=f"{P}bolts")
    svg = edge_rotor() + pad_left(500, 190, 520, 46, id=f"{P}pl") + pad_right(580, 190, 520, 46, id=f"{P}pr") + cal + bolts + tick(540, 700, id=f"{P}tick")
    w.fromto(f"#{P}pl", {"x": -330}, {"x": 0, "duration": u(.28), "ease": "power3.out"}, u(.06)); w.fromto(f"#{P}pr", {"x": 330}, {"x": 0, "duration": u(.28), "ease": "power3.out"}, u(.06))
    w.fromto(f"#{P}cal", {"y": -420}, {"y": 0, "duration": u(.26), "ease": "power3.out"}, u(.36))
    w.fromto(f"#{P}bolts", {"y": -200}, {"y": 0, "duration": u(.16), "ease": "power2.out"}, u(.64))
    w.fromto(f"#{P}tick", {"scale": 0, "opacity": 0, "svgOrigin": "540 700"}, {"scale": 1, "opacity": 1, "svgOrigin": "540 700", "duration": .4, "ease": "back.out(1.6)"}, u(.82))
    return dict(svg=svg, tw=w, labels=[("TORQUE TO SPEC", .66, None)])

def v_finish(P, D):
    u = lambda x: x * D; w = Tw()
    ped = g(line(630, 700, 690, 600, (120, 126, 142), 18) + rr(380, 700, 700, 790, 24, fill=(54, 56, 70), stroke=(150, 156, 172), sw=4) + "".join(line(410 + i * 52, 718, 410 + i * 52, 772, LIME, 7) for i in range(6)), id=f"{P}ped")
    lines = "".join(line(80, y, 200, y, "#fff", 8, id=f"{P}sp{i}", opacity=0) for i, y in enumerate((230, 330, 430)))
    svg = wheel(540, 330, 235, id=f"{P}wheel") + lines + ped
    w.to(f"#{P}wheel", {"rotation": 4200, "svgOrigin": "540 330", "duration": D * .92, "ease": "power2.in"}, u(.05))
    for i in range(3):
        w.fromto(f"#{P}sp{i}", {"opacity": 0, "x": 0}, {"opacity": .5, "x": -70, "duration": .22, "ease": "none", "repeat": int(D / .22) - 4}, u(.2) + i * .05)
    t0 = max(1.3, u(.35)); n = max(1, int((D - t0) / .667))
    for k in range(n):
        w.to(f"#{P}ped", {"y": 46, "duration": .22, "ease": "power2.inOut"}, t0 + k * .667)
        w.to(f"#{P}ped", {"y": 0, "duration": .44, "ease": "power2.out"}, t0 + k * .667 + .22)
    return dict(svg=svg, tw=w, labels=[("PUMP UNTIL FIRM", .35, None)])

def v_cta(P, D, nxt=None, disclaimer=("ALWAYS USE JACK STANDS", "& CHECK YOUR MANUAL FOR SPECS")):
    u = lambda x: x * D; w = Tw()
    html = [f'<div id="{P}btn" class="cta-btn">FOLLOW +</div>', f'<div id="{P}save" class="cta-save">SAVE THIS FOR LATER</div>']
    if nxt: html.append(f'<div id="{P}nxt" class="cta-next"><span>NEXT: {nxt}</span></div>')
    emo = ["❤️", "🔔", "🔧", "🚗", "❤️", "🔔", "🔧"]
    for i, e in enumerate(emo):
        html.append(f'<div id="{P}em{i}" class="cta-em" style="left:{90 + i * 130}px">{e}</div>')
    html.append(f'<div id="{P}disc" class="cta-disc">{disclaimer[0]}<br>{disclaimer[1]}</div>')
    w.fromto(f"#{P}btn", {"scale": .6, "opacity": 0, "transformOrigin": "50% 50%"}, {"scale": 1, "opacity": 1, "transformOrigin": "50% 50%", "duration": .45, "ease": "back.out(1.5)"}, .1)
    w.fromto(f"#{P}save", {"opacity": 0, "filter": "blur(6px)"}, {"opacity": 1, "filter": "blur(0px)", "duration": .2}, .35)
    if nxt: w.fromto(f"#{P}nxt", {"opacity": 0, "filter": "blur(6px)"}, {"opacity": 1, "filter": "blur(0px)", "duration": .2}, .55)
    for i in range(len(emo)):
        st = .2 + i * .22
        w.fromto(f"#{P}em{i}", {"opacity": 0}, {"keyframes": {"0%": {"opacity": 0}, "15%": {"opacity": 1}, "85%": {"opacity": 1}, "100%": {"opacity": 0}}, "duration": 2.6, "ease": "none"}, st)
        w.to(f"#{P}em{i}", {"y": -150, "duration": 2.6, "ease": "none"}, st)
    w.fromto(f"#{P}disc", {"opacity": 0}, {"opacity": .85, "duration": .3}, .8)
    return dict(svg="", html="\n".join(html), tw=w, labels=[])

VIS = {"hook": v_hook, "lift": v_lift, "wheeloff": v_wheeloff, "caliper": v_caliper, "pads": v_pads,
       "piston": v_piston, "install": v_install, "finish": v_finish, "cta": v_cta}
EP01 = ["hook", "lift", "wheeloff", "caliper", "pads", "piston", "install", "finish", "cta"]
