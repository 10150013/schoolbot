"""Scene visuals for episodes 2-8 (filters, oil, intake, plugs, battery, wipers)."""
import json, math
from hf_shapes import *
from hf_vis_brakes import Tw, VIS, YEL, LIME, RED, INK, v_hook

CX = 540
ORG = "#ff8c00"; DARK = (62, 66, 82); RIMC = (110, 116, 134); STEELC = (170, 176, 190); OILC = "#ffaa00"; WHITE = "#fff"

def rrect_t(cx, cy, w, h, a_deg, fill, **kw):
    return f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w}" height="{h}" transform="rotate({a_deg} {cx} {cy})" {A(fill=fill, **kw)}/>'

def pop(w, sel, ox, oy, t, d=.4, ease="back.out(1.6)"):
    w.fromto(sel, {"scale": 0, "opacity": 0, "svgOrigin": f"{ox} {oy}"}, {"scale": 1, "opacity": 1, "svgOrigin": f"{ox} {oy}", "duration": d, "ease": ease}, t)

def fade(w, sel, t, d=.2, a=0, b=1):
    w.fromto(sel, {"opacity": a}, {"opacity": b, "duration": d, "ease": "none"}, t)

# ------------------------------------------------------------------ air filter
def filt(cx, cy, w, h, dirt=0.0, leaves=False, **kw):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    base, dirty = (245, 245, 238), (112, 88, 62)
    c = tuple(int(base[i] + (dirty[i] - base[i]) * dirt) for i in range(3)); dc = tuple(int(v * .78) for v in c)
    s = rr(x0, y0, x1, y1, 14, fill=(34, 34, 42)) + rr(x0 + 12, y0 + 12, x1 - 12, y1 - 12, 6, fill=c)
    n = max(3, int((w - 24) / 16))
    for i in range(n + 1):
        xx = x0 + 12 + i * (w - 24) / n; s += line(round(xx, 1), y0 + 12, round(xx, 1), y1 - 12, dc, 3)
    for i in range(int(45 * dirt)):
        s += ell(x0 + 18 + (i * 137) % max(1, int(w - 36)), y0 + 18 + (i * 71) % max(1, int(h - 36)), 3 + i % 4, fill=(62, 46, 30))
    if leaves:
        for i, (lx, ly) in enumerate([(.2, .3), (.55, .6), (.8, .25)]):
            s += rrect_t(x0 + w * lx, y0 + h * ly, 46, 20, round(math.degrees(.6 + i)), (90, 140, 50))
    return g(s, **kw)

X0, X1, YT, YB = 190, 890, 400, 700

def airbox(P, lid=0.0, clips=0.0, animate=False):
    """lid/clips are static open amounts (0 closed, 1 open); animate=True puts ids on the movable parts."""
    s = rr(X0, YT, X1, YB, 24, fill=DARK, stroke=RIMC, sw=4) + rr(X0 + 30, YT + 30, X1 - 30, YB - 30, 12, fill=(26, 28, 38))
    lid_svg = poly([(X0, YT - 70), (X1, YT - 70), (X1, YT), (X0, YT)], (82, 88, 106), (130, 136, 154), 4)
    s += g(lid_svg, id=f"{P}lid") if animate else g(lid_svg, transform=f"rotate({-lid * 54.4:.1f} {X0} {YT})")
    for k, (cx_, sd) in enumerate(((X0 + 90, -1), (X1 - 90, 1))):
        c = poly([(cx_ - 22, YT - 20), (cx_ + 22, YT - 20), (cx_ + 22, YT + 60), (cx_ - 22, YT + 60)], YEL, (150, 130, 0), 3)
        s += g(c, id=f"{P}clip{k}") if animate else g(c, transform=f"rotate({sd * clips * 74.5:.1f} {cx_} {YT + 60})")
    return s

def v_air_open(P, D):
    u = lambda x: x * D; w = Tw()
    svg = airbox(P, animate=True)
    svg += g(filt(540, 560, 560, 200), id=f"{P}f")
    for k, sd in enumerate((-1, 1)):
        cx_ = X0 + 90 if sd < 0 else X1 - 90
        w.to(f"#{P}clip{k}", {"rotation": sd * 74.5, "svgOrigin": f"{cx_} {YT + 60}", "duration": u(.3), "ease": "power2.out"}, u(.10))
    w.to(f"#{P}lid", {"rotation": -54.4, "svgOrigin": f"{X0} {YT}", "duration": u(.35), "ease": "power2.inOut"}, u(.45))
    fade(w, f"#{P}f", u(.5), .25)
    return dict(svg=svg, tw=w, labels=[("2 CLIPS OR A FEW SCREWS", .05, None)])

def v_air_pull(P, D):
    u = lambda x: x * D; w = Tw()
    svg = airbox(P, 1, 1) + g(filt(540, 560, 560, 200, dirt=.85), id=f"{P}f") + arrow(900, 560, 900, 330, YEL, id=f"{P}ar")
    w.to(f"#{P}f", {"y": -370, "duration": u(.5), "ease": "power2.inOut"}, u(.10))
    fade(w, f"#{P}ar", u(.15), .2)
    return dict(svg=svg, tw=w, labels=[("PULL STRAIGHT UP", .08, None)])

def v_air_light(P, D):
    u = lambda x: x * D; w = Tw()
    fx, fy, fw, fh = 700, 480, 440, 400
    svg = ell(160, 170, 78, fill=(255, 236, 120)) + ell(160, 170, 110, stroke=(255, 236, 120), sw=6, opacity=.5)
    for i in range(6):
        ty = fy - fh / 2 + 30 + i * (fh - 60) / 5
        svg += line(220, 210, fx - fw / 2 - 6, round(ty, 1), (255, 236, 120), 6, id=f"{P}r{i}")
    svg += filt(fx, fy, fw, fh, dirt=1.0) + g(f'<circle cx="{fx}" cy="{fy}" r="70" fill="#fe2c55" stroke="#fff" stroke-width="6"/>' + line(fx - 28, fy - 28, fx + 28, fy + 28, WHITE, 14) + line(fx - 28, fy + 28, fx + 28, fy - 28, WHITE, 14), id=f"{P}x")
    for i in range(6): fade(w, f"#{P}r{i}", u(.05) + i * .06, .2)
    pop(w, f"#{P}x", fx, fy, u(.45))
    return dict(svg=svg, tw=w, labels=[("NO LIGHT? REPLACE IT", .5, None)])

def v_air_new(P, D):
    u = lambda x: x * D; w = Tw()
    svg = airbox(P, 1, 1)
    svg += g("".join(ell(240 + (i * 83) % 600, 520 + (i * 47) % 120, 5, fill=(150, 120, 90)) for i in range(9)) + rr(200, 470, 300, 630, 30, fill=WHITE, id=f"{P}cloth"), id=f"{P}dust")
    svg += g(filt(540, 560, 560, 200, dirt=0), id=f"{P}f")
    w.to(f"#{P}cloth", {"x": 560, "duration": u(.35), "ease": "power1.inOut"}, u(.05))
    w.to(f"#{P}dust", {"opacity": 0, "duration": .2}, u(.4))
    w.fromto(f"#{P}f", {"y": -440, "opacity": 0}, {"y": 0, "opacity": 1, "duration": u(.4), "ease": "power3.out"}, u(.45))
    return dict(svg=svg, tw=w, labels=[("SAME SHAPE, SAME SIDE UP", .5, None)])

def v_air_close(P, D):
    u = lambda x: x * D; w = Tw()
    svg = airbox(P, animate=True) + g(filt(540, 560, 560, 200), id=f"{P}f") + tick(540, 220, id=f"{P}t")
    # airbox(animate) is drawn closed; start it open and close it
    w.fromto(f"#{P}lid", {"rotation": -54.4, "svgOrigin": f"{X0} {YT}"}, {"rotation": 0, "svgOrigin": f"{X0} {YT}", "duration": u(.4), "ease": "power2.inOut"}, u(.10))
    for k, sd in enumerate((-1, 1)):
        cx_ = X0 + 90 if sd < 0 else X1 - 90
        w.fromto(f"#{P}clip{k}", {"rotation": sd * 74.5, "svgOrigin": f"{cx_} {YT + 60}"}, {"rotation": 0, "svgOrigin": f"{cx_} {YT + 60}", "duration": u(.3), "ease": "power2.in"}, u(.5))
    w.to(f"#{P}f", {"opacity": 0, "duration": .15}, u(.42))
    pop(w, f"#{P}t", 540, 220, u(.78))
    return dict(svg=svg, tw=w, labels=[])

# ------------------------------------------------------------------ cabin filter
def dash():
    return rr(60, 100, 1020, 660, 50, fill=(48, 44, 72), stroke=(96, 90, 130), sw=4) + rr(120, 135, 440, 185, 14, fill=(30, 28, 48)) + rr(640, 135, 960, 185, 14, fill=(30, 28, 48))

def glovebox(P, filt_svg="", cover=True):
    s = rr(180, 240, 900, 540, 24, fill=(14, 14, 20))
    inner = rr(330, 290, 750, 430, 10, fill=(34, 38, 52), stroke=RIMC, sw=3) + filt_svg + (rr(330, 435, 750, 480, 8, fill=(96, 102, 120), stroke=RIMC, sw=3) if cover else "")
    s += g(inner, id=f"{P}in", opacity=0)
    s += rr(180, 240, 900, 540, 24, fill=(86, 92, 112), stroke=(130, 136, 156), sw=4, id=f"{P}door") + rr(470, 280, 610, 302, 10, fill=(60, 64, 80), id=f"{P}handle")
    return s

def door(w, P, t, d, o0, o1, ease="power2.inOut"):
    def yy(o): return 240 + (560 - 240) * o, (540 + (690 - 540) * o) - (240 + (560 - 240) * o)
    y0, h0 = yy(o0); y1, h1 = yy(o1)
    w.fromto(f"#{P}door", {"attr": {"y": y0, "height": h0}}, {"attr": {"y": y1, "height": h1}, "duration": d, "ease": ease}, t)

def v_glove1(P, D):
    u = lambda x: x * D; w = Tw()
    items = "".join(g(rrect_t(x, 400, 120, 22, round(math.degrees(a)), c), id=f"{P}it{i}") for i, (x, a, c) in enumerate([(380, .5, YEL), (540, -.4, "#ff3c96"), (700, 1.0, "#00ebff")]))
    svg = dash() + glovebox(P) + items
    door(w, P, u(.2), u(.4), 0, .35)
    fade(w, f"#{P}in", u(.3), .2)
    for i in range(3):
        w.fromto(f"#{P}it{i}", {"opacity": 0}, {"opacity": 1, "duration": .05}, u(.35) + i * .08)
        w.to(f"#{P}it{i}", {"y": 440, "duration": u(.5), "ease": "power2.in"}, u(.35) + i * .08)
    return dict(svg=svg, tw=w, labels=[("EMPTY IT FIRST", .05, None)])

def v_glove2(P, D):
    u = lambda x: x * D; w = Tw()
    svg = dash() + glovebox(P, filt(540, 360, 380, 110, dirt=.8, leaves=True))
    svg += arrow(70, 390, 170, 390, YEL, id=f"{P}al") + arrow(1010, 390, 910, 390, YEL, id=f"{P}ar")
    door(w, P, u(.45), u(.4), 0, 1)
    fade(w, f"#{P}in", u(.5), .2); w.to(f"#{P}handle", {"opacity": 0, "duration": .15}, u(.45))
    w.to(f"#{P}al", {"x": 14, "duration": .3, "ease": "sine.inOut", "repeat": max(1, int(u(.4) / .3)), "yoyo": True}, 0)
    w.to(f"#{P}ar", {"x": -14, "duration": .3, "ease": "sine.inOut", "repeat": max(1, int(u(.4) / .3)), "yoyo": True}, 0)
    w.to(f"#{P}al", {"opacity": 0, "duration": .15}, u(.45)); w.to(f"#{P}ar", {"opacity": 0, "duration": .15}, u(.45))
    return dict(svg=svg, tw=w, labels=[("SQUEEZE THE SIDES", .05, None)])

def v_glove3(P, D):
    u = lambda x: x * D; w = Tw()
    svg = dash() + rr(180, 240, 900, 540, 24, fill=(14, 14, 20)) + rr(330, 290, 750, 430, 10, fill=(34, 38, 52), stroke=RIMC, sw=3) + rr(330, 435, 750, 480, 8, fill=(96, 102, 120), stroke=RIMC, sw=3)
    svg += g(filt(540, 360, 380, 110, dirt=.9, leaves=True), id=f"{P}f") + rr(180, 560, 900, 690, 24, fill=(86, 92, 112), stroke=(130, 136, 156), sw=4)
    w.to(f"#{P}f", {"y": 420, "duration": u(.5), "ease": "power2.inOut"}, u(.25))
    return dict(svg=svg, tw=w, labels=[("COVER OFF, FILTER OUT", .05, None)])

def v_glove4(P, D):
    u = lambda x: x * D; w = Tw()
    svg = filt(300, 430, 340, 260, dirt=0) + filt(780, 430, 340, 260, dirt=0) + arrow(300, 330, 300, 520, (40, 150, 90), 22) + arrow(780, 520, 780, 330, RED, 22)
    svg += tick(300, 210, id=f"{P}ok") + g(f'<circle cx="780" cy="210" r="70" fill="#fe2c55" stroke="#fff" stroke-width="6"/>' + line(752, 182, 808, 238, WHITE, 14) + line(752, 238, 808, 182, WHITE, 14), id=f"{P}no")
    pop(w, f"#{P}ok", 300, 210, u(.35)); pop(w, f"#{P}no", 780, 210, u(.4))
    return dict(svg=svg, tw=w, labels=[("AIR FLOWS THE WAY THE ARROW POINTS", .05, None)])

def v_glove5(P, D):
    u = lambda x: x * D; w = Tw()
    svg = dash() + rr(180, 240, 900, 540, 24, fill=(14, 14, 20))
    svg += g(rr(330, 290, 750, 430, 10, fill=(34, 38, 52), stroke=RIMC, sw=3) + rr(330, 435, 750, 480, 8, fill=(96, 102, 120), stroke=RIMC, sw=3), id=f"{P}in")
    svg += g(filt(540, 360, 380, 110, dirt=0), id=f"{P}f")
    svg += rr(180, 560, 900, 690, 24, fill=(86, 92, 112), stroke=(130, 136, 156), sw=4, id=f"{P}door") + tick(540, 770, id=f"{P}t")
    w.fromto(f"#{P}f", {"y": 440}, {"y": 0, "duration": u(.35), "ease": "power3.out"}, u(.05))
    door(w, P, u(.45), u(.25), 1, 0, "power2.inOut")
    w.to(f"#{P}in", {"opacity": 0, "duration": .1}, u(.68)); w.to(f"#{P}f", {"opacity": 0, "duration": .1}, u(.68))
    pop(w, f"#{P}t", 540, 770, u(.75))
    return dict(svg=svg, tw=w, labels=[])

def v_hook_vent(P, D):
    u = lambda x: x * D; w = Tw()
    svg = rr(220, 440, 860, 640, 30, fill=(30, 28, 48), stroke=RIMC, sw=5) + "".join(line(250, 470 + i * 38, 830, 470 + i * 38, (90, 96, 120), 8) for i in range(5))
    for j in range(5):
        pts = [(300 + j * 120 + 26 * math.sin(k * .9 + j), 420 - k * 46) for k in range(7)]
        svg += pline(pts, (120, 200, 80), 12, id=f"{P}wv{j}")
        w.fromto(f"#{P}wv{j}", {"y": 0, "opacity": .9}, {"y": -40, "opacity": .3, "duration": .6, "ease": "sine.inOut", "repeat": 7, "yoyo": True}, j * .09)
    svg += emoji(540, 190, "🤢", 190, id=f"{P}em", fill=WHITE)
    w.to(f"#{P}em", {"y": -12, "duration": .5, "ease": "sine.inOut", "repeat": 7, "yoyo": True}, 0)
    return dict(svg=svg, tw=w, labels=[])

# ------------------------------------------------------------------ oil
def drop(cx, cy, r, col=OILC, **kw):
    return g(poly([(cx, cy - r * 1.9), (cx + r * .95, cy - r * .25), (cx - r * .95, cy - r * .25)], col) + ell(cx, cy, r, fill=col) + ell(cx - r * .35, cy - r * .2, r * .22, fill=(255, 235, 170)), **kw)

def oil_filter(x, y, **kw):
    return g(rr(x - 85, y, x + 85, y + 230, 26, fill=(235, 112, 28), stroke=(255, 170, 90), sw=3) + rr(x - 92, y, x + 92, y + 28, 10, fill=(150, 60, 15)) + rr(x - 45, y + 70, x - 5, y + 190, 6, fill=(250, 245, 235)) + rr(x - 92, y + 205, x + 92, y + 235, 10, fill=(120, 50, 12)), **kw)

def v_hook_oil(P, D):
    u = lambda x: x * D; w = Tw()
    spots = [(-330, -150), (330, -120), (340, 110), (-320, 140)]
    svg = drop(540, 380, 150, id=f"{P}dr") + text(540, 640, "6 STEPS", 190, WHITE, stroke=INK, sw=10) + text(540, 800, "NO QUICK LUBE NEEDED", 46, "#cdd2e8", font="Inter", weight=800)
    for i, (dx, dy) in enumerate(spots):
        svg += g(poly(star_pts(540 + dx, 400 + dy, 26), YEL), id=f"{P}st{i}"); pop(w, f"#{P}st{i}", 540 + dx, 400 + dy, u(.1) + i * .06, .3, "back.out(2)")
    w.to(f"#{P}dr", {"y": -12, "duration": .6, "ease": "sine.inOut", "repeat": 7, "yoyo": True}, 0)
    return dict(svg=svg, tw=w, labels=[])

def v_car_lift(P, D):
    u = lambda x: x * D; w = Tw(); gy = 800
    car = rr(100, 440, 980, 650, 60, fill=(66, 72, 108), stroke=(110, 118, 160), sw=4) + rr(330, 320, 760, 450, 40, fill=(66, 72, 108), stroke=(110, 118, 160), sw=4)
    car += rr(370, 345, 540, 430, 14, fill=(140, 190, 225)) + rr(560, 345, 720, 430, 14, fill=(140, 190, 225))
    car += "".join(ell(wx, gy - 95, 95, fill=(22, 22, 26), stroke=(78, 80, 92), sw=5) + ell(wx, gy - 95, 50, fill=(190, 196, 208)) for wx in (280, 800))
    svg = line(30, gy, 1050, gy, (130, 136, 160), 8) + g(car, id=f"{P}car")
    for k, sx in enumerate((430, 680)):
        svg += f'<g id="{P}stand{k}">' + poly([(sx - 80, gy), (sx + 80, gy), (sx + 20, gy - 36), (sx - 20, gy - 36)], ORG) + rr(sx - 18, 610, sx + 18, gy - 36, 6, fill=(255, 170, 60)) + rr(sx - 50, 598, sx + 50, 616, 8, fill=(255, 200, 90)) + "</g>"
    svg += "".join(pline([(300 + i * 160 + 18 * math.sin(k + i), 320 - k * 24) for k in range(6)], (255, 120, 60), 8, id=f"{P}hw{i}") for i in range(3))
    w.to(f"#{P}car", {"y": -40, "duration": u(.3), "ease": "power2.inOut"}, u(.3))
    for k, sx in enumerate((430, 680)):
        w.fromto(f"#{P}stand{k}", {"scaleY": 0, "opacity": 0, "svgOrigin": f"{sx} {gy}"}, {"scaleY": 1, "opacity": 1, "svgOrigin": f"{sx} {gy}", "duration": u(.2), "ease": "back.out(1.3)"}, u(.5))
    for i in range(3):
        w.fromto(f"#{P}hw{i}", {"opacity": .9, "y": 0}, {"opacity": 0, "y": -30, "duration": u(.3), "ease": "none"}, u(.02) + i * .1)
    return dict(svg=svg, tw=w, labels=[("WARM IT UP A FEW MINUTES", .04, .3)])

def v_drain(P, D):
    u = lambda x: x * D; w = Tw()
    svg = poly([(220, 130), (860, 130), (800, 410), (280, 410)], DARK, RIMC, 4)
    svg += poly([(160, 690), (620, 690), (580, 810), (200, 810)], (50, 54, 70), RIMC, 4) + g(poly([(200, 810), (580, 810), (584, 706), (196, 706)], OILC), id=f"{P}oil")
    svg += line(360, 460, 360, 690, OILC, 14, id=f"{P}stream")
    svg += "".join(ell(360, 470, 9, fill=(255, 215, 110), id=f"{P}dp{i}") for i in range(4))
    svg += g(g(bolt(360, 410, 28, id=f"{P}bs"), id=f"{P}bm"))
    w.to(f"#{P}bm", {"y": 70, "duration": u(.25), "ease": "power2.out"}, u(.1)); w.to(f"#{P}bs", {"rotation": 515, "svgOrigin": "360 410", "duration": u(.25), "ease": "power2.out"}, u(.1))
    w.fromto(f"#{P}stream", {"attr": {"y2": 470}, "opacity": 0}, {"attr": {"y2": 690}, "opacity": 1, "duration": .35, "ease": "power1.in"}, u(.3))
    w.fromto(f"#{P}oil", {"scaleY": 0, "svgOrigin": "400 810"}, {"scaleY": 1, "svgOrigin": "400 810", "duration": u(.6), "ease": "none"}, u(.3))
    for i in range(4):
        w.fromto(f"#{P}dp{i}", {"y": 0, "opacity": 0}, {"y": 210, "opacity": 1, "duration": .5, "ease": "none", "repeat": int(u(.6) / .5), }, u(.32) + i * .12)
    return dict(svg=svg, tw=w, labels=[("HOT OIL! BE CAREFUL", .05, None)])

def v_ofilter(P, D):
    u = lambda x: x * D; w = Tw()
    svg = rr(120, 130, 960, 300, 24, fill=DARK, stroke=RIMC, sw=4) + oil_filter(700, 300, id=f"{P}old")
    svg += g(oil_filter(700, 300) + ell(700, 300, 92, 12, stroke=OILC, sw=6), id=f"{P}new")
    w.to(f"#{P}old", {"y": 360, "duration": u(.28), "ease": "power2.in"}, u(.12)); w.to(f"#{P}old", {"opacity": 0, "duration": .12}, u(.4))
    w.fromto(f"#{P}new", {"y": 360, "opacity": 0}, {"y": 360, "opacity": 1, "duration": .2}, u(.45))
    w.to(f"#{P}new", {"y": 0, "duration": u(.24), "ease": "power3.out"}, u(.66))
    return dict(svg=svg, tw=w, labels=[("SPIN OFF THE OLD FILTER", .06, .45), ("OIL THE NEW GASKET", .5, None)])

def v_plug_back(P, D):
    u = lambda x: x * D; w = Tw()
    svg = poly([(220, 130), (860, 130), (800, 410), (280, 410)], DARK, RIMC, 4)
    svg += g(g(bolt(360, 480, 28, id=f"{P}bs") + g(line(360, 480, 570, 300, (200, 205, 215), 22), id=f"{P}wr")), id=f"{P}bm") + tick(760, 600, id=f"{P}t")
    w.to(f"#{P}bm", {"y": -70, "duration": u(.35), "ease": "power2.out"}, u(.10)); w.to(f"#{P}bs", {"rotation": -515, "svgOrigin": "360 480", "duration": u(.35), "ease": "power2.out"}, u(.10))
    w.to(f"#{P}wr", {"rotation": 22, "svgOrigin": "360 480", "duration": .3, "ease": "sine.inOut", "repeat": 5, "yoyo": True}, u(.45))
    pop(w, f"#{P}t", 760, 600, u(.6))
    return dict(svg=svg, tw=w, labels=[("TIGHTEN TO SPEC", .05, .45), ("NOT GORILLA TIGHT", .5, None)])

def v_pour(P, D):
    u = lambda x: x * D; w = Tw()
    bottle = g(rr(615, 150, 745, 350, 14, fill=(40, 44, 58), stroke=(120, 126, 142), sw=4) + rr(615, 215, 745, 285, 4, fill=OILC) + rr(655, 115, 705, 150, 4, fill=(200, 205, 215)), id=f"{P}bt")
    svg = rr(230, 470, 850, 640, 24, fill=DARK, stroke=RIMC, sw=4) + ell(579, 470, 70, 16, fill=(30, 34, 46), stroke=STEELC, sw=5) + poly([(509, 400), (649, 400), (599, 470), (559, 470)], (200, 205, 215), (120, 126, 140), 3)
    svg += line(579, 372, 579, 440, OILC, 16, id=f"{P}stream") + bottle
    w.fromto(f"#{P}bt", {"rotation": -17, "svgOrigin": "680 250"}, {"rotation": -137.5, "svgOrigin": "680 250", "duration": u(.3), "ease": "power2.inOut"}, 0)
    w.fromto(f"#{P}stream", {"scaleY": 0, "svgOrigin": "579 372"}, {"scaleY": 1, "svgOrigin": "579 372", "duration": .25, "ease": "none"}, u(.3))
    return dict(svg=svg, tw=w, labels=[("OIL TYPE + AMOUNT: OWNER'S MANUAL", .1, None)])

def v_dipstick(P, D):
    u = lambda x: x * D; w = Tw()
    stick = rr(CX - 7, 560, CX + 7, 890, 6, fill=STEELC) + ell(CX, 540, 30, 24, stroke=YEL, sw=10) + rr(CX - 7, 790, CX + 7, 850, 4, fill=OILC) + line(CX - 34, 770, CX + 34, 770, WHITE, 5) + line(CX - 34, 870, CX + 34, 870, WHITE, 5)
    svg = g(rr(CX - 40, 560, CX + 40, 800, 16, fill=DARK, stroke=RIMC, sw=4) + g(stick, id=f"{P}st") + g(rr(CX - 60, 700, CX + 60, 780, 20, fill=WHITE), id=f"{P}cl", opacity=0), transform="translate(540 600) scale(1.25) translate(-540 -600)") + tick(840, 420, id=f"{P}t")
    w.to(f"#{P}st", {"y": -360, "duration": u(.2), "ease": "power2.out"}, u(.05)); w.to(f"#{P}st", {"y": 0, "duration": u(.15), "ease": "power2.in"}, u(.45))
    w.to(f"#{P}st", {"y": -360, "duration": u(.15), "ease": "power2.out"}, u(.6))
    w.fromto(f"#{P}cl", {"opacity": 0, "x": 0}, {"opacity": 1, "x": 120, "duration": u(.18), "ease": "none"}, u(.3)); w.to(f"#{P}cl", {"opacity": 0, "duration": .1}, u(.48))
    pop(w, f"#{P}t", 840, 420, u(.8))
    return dict(svg=svg, tw=w, labels=[("RECYCLE THE OLD OIL", .6, None)])

# ------------------------------------------------------------------ intake system
RUN = [290, 430, 650, 790]
MAIN = [(60, 160), (880, 160), (880, 330), (540, 330), (540, 470)]

def path_len(pts): return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))

def v_intake(hl, label=None, fire=False):
    def v(P, D):
        w = Tw(); dim = (70, 66, 96); IN, OUT = INK, "#9690b4"
        def col(i, c): return c if hl is None or hl == i else dim
        def ink(i): return IN if hl in (None, i) else OUT
        svg = pline(MAIN, (44, 48, 68), 56)
        svg += rr(40, 90, 300, 240, 24, fill=col(0, (0, 190, 215)), stroke=WHITE if hl == 0 else None, sw=6) + text(170, 165, "AIR FILTER", 36, ink(0), font="Inter", weight=800)
        svg += rr(360, 130, 560, 190, 8, fill=(60, 64, 84)) + rr(400, 100, 520, 220, 14, fill=col(1, "#b6ff00"), stroke=WHITE if hl == 1 else None, sw=6) + text(460, 160, "MAF", 40, ink(1), font="Inter", weight=800)
        svg += rr(660, 100, 840, 220, 18, fill=col(2, ORG), stroke=WHITE if hl == 2 else None, sw=6) + g(line(706, 182, 794, 138, INK, 10), id=f"{P}bf")
        svg += rr(230, 440, 850, 520, 24, fill=col(3, "#ff3c96"), stroke=WHITE if hl == 3 else None, sw=6) + text(540, 480, "INTAKE MANIFOLD", 36, ink(3), font="Inter", weight=800)
        for i, x in enumerate(RUN):
            svg += rr(x - 20, 520, x + 20, 650, 6, fill=col(3, (210, 60, 140)))
            svg += rr(x - 62, 650, x + 62, 810, 14, fill=col(4, (175, 100, 255)), stroke=WHITE if hl == 4 else None, sw=6, id=f"{P}cy{i}")
            svg += rr(x - 44, 700, x + 44, 740, 6, fill=(220, 222, 235), id=f"{P}pi{i}")
        for i, x in enumerate(RUN): svg += g(poly(star_pts(x, 640, 34), WHITE), id=f"{P}fl{i}", opacity=0)
        L0 = path_len(MAIN); speed = 260.0
        pts_all = []
        for j in range(16):
            rx = RUN[j % 4]; full = MAIN + [(540, 470), (rx, 480), (rx, 700)]
            # unique vertices only
            full = MAIN + [(rx, 480), (rx, 700)]
            Lt = path_len(full); d0 = (j * 70) % Lt
            svg += ell(0, 0, 9, fill=(200, 245, 255), id=f"{P}ap{j}", opacity=0)
            def at(d):
                for (x0, y0), (x1, y1) in zip(full, full[1:]):
                    l = math.hypot(x1 - x0, y1 - y0)
                    if d <= l: k = d / l if l else 0; return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
                    d -= l
                return full[-1]
            verts = [0.0]; acc = 0
            for a, b in zip(full, full[1:]): acc += math.hypot(b[0] - a[0], b[1] - a[1]); verts.append(acc)
            t = 0.0; d = d0; first = True
            while t < D - 1e-6:
                nxt = min([v for v in verts if v > d + 1e-6] or [Lt]); dt = (nxt - d) / speed
                dt = min(dt, D - t); d_end = d + dt * speed
                x0, y0 = at(d); x1, y1 = at(min(d_end, Lt))
                if first: w.fromto(f"#{P}ap{j}", {"x": x0, "y": y0, "opacity": 1}, {"x": x1, "y": y1, "opacity": 1, "duration": dt, "ease": "none"}, t); first = False
                else: w.to(f"#{P}ap{j}", {"x": x1, "y": y1, "duration": dt, "ease": "none"}, t)
                t += dt; d = d_end
                if d >= Lt - 1e-6:
                    d = 0.0; w.set(f"#{P}ap{j}", {"x": full[0][0], "y": full[0][1]}, t)
        if hl == 2: w.to(f"#{P}bf", {"rotation": 55, "svgOrigin": "750 160", "duration": .7, "ease": "sine.inOut", "repeat": max(1, int(D / .7)), "yoyo": True}, 0)
        for i in range(4):
            w.to(f"#{P}pi{i}", {"y": 22, "duration": .26, "ease": "sine.inOut", "repeat": int(D / .26), "yoyo": True}, i * .08)
        if fire:
            for k in range(int(D * 5)):
                i = k % 4; t0 = k * .2 + .15
                w.to(f"#{P}cy{i}", {"attr": {"fill": "#ffc828"}, "duration": .04}, t0); w.to(f"#{P}cy{i}", {"attr": {"fill": "#af64ff"}, "duration": .06}, t0 + .13)
                w.to(f"#{P}fl{i}", {"opacity": 1, "duration": .04}, t0); w.to(f"#{P}fl{i}", {"opacity": 0, "duration": .06}, t0 + .12)
        return dict(svg=svg, tw=w, labels=[(label, .05, None)] if label else [])
    return v

# ------------------------------------------------------------------ spark plugs
def plug(cx, y, s=1.0, **kw):
    o = rr(cx - 12 * s, y, cx + 12 * s, y + 40 * s, 4 * s, fill=(200, 204, 214)) + rr(cx - 34 * s, y + 40 * s, cx + 34 * s, y + 200 * s, 16 * s, fill=(246, 244, 236), stroke=(190, 186, 176), sw=3)
    o += "".join(line(cx - 34 * s, y + 80 * s + i * 28 * s, cx + 34 * s, y + 80 * s + i * 28 * s, (205, 200, 190), 3) for i in range(3))
    o += rr(cx - 46 * s, y + 200 * s, cx + 46 * s, y + 250 * s, 6 * s, fill=STEELC, stroke=(210, 215, 225), sw=3) + rr(cx - 34 * s, y + 250 * s, cx + 34 * s, y + 330 * s, 4 * s, fill=(176, 182, 196))
    o += "".join(line(cx - 34 * s, y + (256 + i * 11) * s, cx + 34 * s, y + (256 + i * 11) * s, (120, 126, 140), 3) for i in range(7))
    o += rr(cx - 8 * s, y + 330 * s, cx + 8 * s, y + 356 * s, 2, fill=(215, 220, 230)) + pline([(cx + 30 * s, y + 330 * s), (cx + 30 * s, y + 352 * s), (cx + 3 * s, y + 352 * s)], (150, 156, 170), 9 * s)
    return g(o, **kw)

def coil(x, y, **kw):
    return g(rr(x - 44, y, x + 44, y + 150, 14, fill=(62, 44, 110), stroke=(130, 110, 190), sw=3) + rr(x + 20, y + 30, x + 66, y + 70, 6, fill=(30, 28, 44)) + rr(x - 26, y + 150, x + 26, y + 200, 6, fill=(40, 40, 52)), **kw)

ENG = lambda y0, y1: rr(100, y0, 980, y1, 40, fill=(54, 58, 76), stroke=RIMC, sw=4)

def v_hook_plug(P, D):
    u = lambda x: x * D; w = Tw()
    svg = plug(540, 150, 1.5, id=f"{P}pl")
    for i in range(5):
        svg += g(poly(star_pts(0, 0, 24), YEL), id=f"{P}sp{i}")
        cx_, cy_ = 580, 690; pts = [{"x": cx_ + 90 * math.cos(i * 1.26 + k * .5), "y": cy_ + 60 * math.sin(i * 1.26 + k * .5), "duration": .12} for k in range(int(D / .12) + 2)]
        w.fromto(f"#{P}sp{i}", {"x": pts[0]["x"], "y": pts[0]["y"]}, {"keyframes": pts[1:], "ease": "none"}, 0)
    svg += text(540, 800, "MISFIRE? WORN PLUGS?", 46, "#cdd2e8", font="Inter", weight=800)
    w.to(f"#{P}pl", {"x": 4, "duration": .06, "ease": "none", "repeat": int(D / .06), "yoyo": True}, 0)
    return dict(svg=svg, tw=w, labels=[])

def v_plug_coil(P, D):
    u = lambda x: x * D; w = Tw()
    svg = ENG(330, 700) + ell(420, 560, 40, 12, fill=(14, 14, 20)) + "".join(coil(x, 380, id=f"{P}c{i}") for i, x in enumerate((220, 420, 620, 820)))
    w.to(f"#{P}c1", {"y": -220, "duration": u(.35), "ease": "power2.out"}, u(.25))
    return dict(svg=svg, tw=w, labels=[("ONE AT A TIME", .08, None)])

def v_plug_blow(P, D):
    u = lambda x: x * D; w = Tw()
    svg = ENG(520, 760) + ell(640, 620, 100, 28, fill=(12, 12, 18), stroke=STEELC, sw=6) + rr(100, 390, 300, 440, 12, fill=ORG) + rr(280, 405, 400, 425, 6, fill=STEELC)
    for i in range(9):
        svg += ell(0, 0, 4, fill=(190, 230, 255), id=f"{P}ai{i}")
        w.fromto(f"#{P}ai{i}", {"x": 420, "y": 430, "opacity": 1}, {"x": 700, "y": 580, "opacity": 1, "duration": .55, "ease": "none", "repeat": int(D / .55)}, i * .06)
    for i in range(8):
        svg += ell(0, 0, 5, fill=(150, 120, 90), id=f"{P}ds{i}")
        w.fromto(f"#{P}ds{i}", {"x": 640 + (i - 4) * 4, "y": 600, "opacity": 1}, {"x": 640 + (i - 4) * 22, "y": 400, "opacity": 0, "duration": .8, "ease": "none", "repeat": int(D / .8)}, i * .1)
    return dict(svg=svg, tw=w, labels=[("KEEP DIRT OUT OF THE HOLE", .08, None)])

def v_plug_socket(P, D):
    u = lambda x: x * D; w = Tw()
    svg = ENG(600, 780) + ell(CX, 640, 90, 24, fill=(12, 12, 18), stroke=STEELC, sw=6)
    svg += rr(CX - 20, 160, CX + 20, 398, 4, fill=STEELC, id=f"{P}ext")
    svg += g(plug(CX, 380, .9) + rr(CX - 58, 398, CX + 58, 638, 12, fill=(96, 102, 120), stroke=STEELC, sw=4), id=f"{P}un")
    svg += g(line(CX, 160, CX + 330, 160, (210, 214, 224), 20), id=f"{P}ra") + ell(CX, 160, 40, fill=(120, 126, 142), stroke=STEELC, sw=4)
    w.to(f"#{P}un", {"y": -220, "duration": u(.55), "ease": "power2.inOut"}, u(.3)); w.to(f"#{P}ext", {"attr": {"height": 18}, "duration": u(.55), "ease": "power2.inOut"}, u(.3))
    w.fromto(f"#{P}ra", {"rotation": -18, "svgOrigin": "540 160"}, {"rotation": 18, "svgOrigin": "540 160", "duration": .6, "ease": "sine.inOut", "repeat": max(1, int(D / .6)), "yoyo": True}, 0)
    return dict(svg=svg, tw=w, labels=[("SPARK PLUG SOCKET", .05, None)])

def v_plug_gap(P, D):
    u = lambda x: x * D; w = Tw(); ty = 110 + 330 * 1.55
    svg = plug(500, 110, 1.55) + g(rr(560, ty + 5, 880, ty + 19, 2, fill=(230, 232, 240), stroke=(140, 146, 160), sw=2), id=f"{P}gg") + arrow(CX + 220, ty + 120, CX + 50, ty + 30, YEL, 10, id=f"{P}ar")
    w.fromto(f"#{P}gg", {"x": 490}, {"x": 0, "duration": u(.35), "ease": "power3.out"}, u(.15))
    fade(w, f"#{P}ar", u(.3), .2)
    return dict(svg=svg, tw=w, labels=[("CHECK THE GAP", .05, .5), ("MATCH YOUR MANUAL'S SPEC", .55, None)])

def v_plug_in(P, D):
    u = lambda x: x * D; w = Tw()
    svg = ENG(560, 780) + ell(CX, 600, 90, 24, fill=(12, 12, 18), stroke=STEELC, sw=6) + g(plug(CX, 120, .9), id=f"{P}pl")
    svg += g(line(CX, 200, CX + 300, 200, (210, 214, 224), 20), id=f"{P}ra", opacity=0) + tick(850, 300, id=f"{P}t")
    w.to(f"#{P}pl", {"y": 210, "duration": u(.45), "ease": "power2.inOut"}, u(.10))
    fade(w, f"#{P}ra", u(.6), .1)
    w.fromto(f"#{P}ra", {"rotation": -14, "svgOrigin": "540 200"}, {"rotation": 14, "svgOrigin": "540 200", "duration": .3, "ease": "sine.inOut", "repeat": 3, "yoyo": True}, u(.6))
    pop(w, f"#{P}t", 850, 300, u(.85))
    return dict(svg=svg, tw=w, labels=[("FINGER-TIGHT FIRST", .05, .55), ("THEN SNUG TO SPEC", .6, None)])

def v_plug_coilback(P, D):
    u = lambda x: x * D; w = Tw()
    svg = ENG(330, 700)
    for i, x in enumerate((220, 420, 620, 820)):
        svg += coil(x, 380, id=f"{P}c{i}")
        svg += g(ell(x, 300, 32, fill=(40, 210, 110), stroke=WHITE, sw=4) + pline([(x - 14, 300), (x - 3, 312), (x + 17, 288)], WHITE, 7), id=f"{P}t{i}")
        w.fromto(f"#{P}c{i}", {"y": -220}, {"y": 0, "duration": u(.2), "ease": "power3.out"}, u(.1 + i * .18))
        pop(w, f"#{P}t{i}", x, 300, u(.32 + i * .18), .3)
    return dict(svg=svg, tw=w, labels=[("REPEAT FOR EVERY CYLINDER", .05, None)])

# ------------------------------------------------------------------ battery
def battery(x=330, y=400, w_=420, h=280, **kw):
    s = rr(x, y, x + w_, y + h, 22, fill=(32, 34, 44), stroke=(90, 94, 110), sw=4) + rr(x + 24, y + 70, x + w_ - 24, y + h - 26, 10, fill=(46, 50, 68)) + text(x + w_ / 2, y + h / 2 + 22, "12V", 70, (150, 156, 176))
    for px, c, sign in ((x + 80, (80, 84, 98), "-"), (x + w_ - 80, (230, 50, 60), "+")):
        s += rr(px - 30, y - 34, px + 30, y, 6, fill=c, stroke=(200, 205, 215), sw=3) + text(px, y + 36, sign, 52, WHITE)
    return g(s, **kw)

def clamp(px, py, color, sd=1, **kw):
    y = py - 46
    return g(pline([(px, y), (px + sd * 40, y - 90), (px + sd * 140, y - 130)], color, 22) + rr(px - 38, y - 10, px + 38, y + 46, 8, fill=color, stroke=(200, 205, 215), sw=3) + ell(px, y + 18, 9, fill=(200, 205, 215)), **kw)

BLK = (24, 24, 30); RDC = (220, 40, 50)

def v_hook_batt(P, D):
    u = lambda x: x * D; w = Tw()
    svg = text(540, 200, "CLICK CLICK", 110, WHITE, stroke=INK, sw=8) + battery(300, 330, 480, 320) + rr(340, 345, 740, 390, 10, fill=(20, 20, 28)) + rr(344, 349, 404, 386, 8, fill=RED, id=f"{P}bar") + text(540, 760, "DEAD BATTERY?", 64, YEL, stroke=INK, sw=6)
    for k in range(int(D * 3)):
        w.to(f"#{P}bar", {"attr": {"width": 20 if k % 2 else 60}, "duration": .01}, k / 3)
    return dict(svg=svg, tw=w, labels=[])

def v_batt_safe(P, D):
    u = lambda x: x * D; w = Tw()
    lens = "".join(ell(gx, 330, 95, 80, fill=(140, 190, 225), stroke=(30, 30, 38), sw=14, fill_opacity=.75) for gx in (430, 650))
    svg = g(lens + line(525, 330, 555, 330, (30, 30, 38), 12) + line(335, 330, 180, 300, (30, 30, 38), 12) + line(745, 330, 900, 300, (30, 30, 38), 12), id=f"{P}gg")
    svg += g(ell(CX, 640, 90, fill=(60, 64, 82), stroke=STEELC, sw=8) + rr(CX + 60, 620, CX + 250, 660, 10, fill=STEELC) + text(CX, 800, "ENGINE OFF, KEY OUT", 44, WHITE, stroke=INK, sw=6), id=f"{P}ky")
    pop(w, f"#{P}gg", 540, 330, u(.1), .45); pop(w, f"#{P}ky", 540, 640, u(.4), .45)
    return dict(svg=svg, tw=w, labels=[])

def v_batt_neg(P, D):
    u = lambda x: x * D; w = Tw()
    svg = battery() + clamp(410, 400, BLK, -1, id=f"{P}cn") + clamp(670, 400, RDC, 1) + g(line(410, 354, 509, 215, STEELC, 18), id=f"{P}wr")
    w.to(f"#{P}cn", {"y": -120, "duration": u(.4), "ease": "power2.out"}, u(.3))
    w.fromto(f"#{P}wr", {"rotation": -17, "svgOrigin": "410 354"}, {"rotation": 17, "svgOrigin": "410 354", "duration": .28, "ease": "sine.inOut", "repeat": max(1, int(u(.35) / .28)), "yoyo": True}, u(.05))
    w.to(f"#{P}wr", {"opacity": 0, "duration": .12}, u(.45))
    return dict(svg=svg, tw=w, labels=[("NEGATIVE (BLACK) FIRST", .05, None)])

def v_batt_pos(P, D):
    u = lambda x: x * D; w = Tw()
    svg = battery() + clamp(410, 400, BLK, -1, transform="translate(0 -120)") + clamp(670, 400, RDC, 1, id=f"{P}cp")
    w.to(f"#{P}cp", {"y": -120, "duration": u(.4), "ease": "power2.out"}, u(.3))
    return dict(svg=svg, tw=w, labels=[("THEN POSITIVE (RED)", .05, None)])

def v_batt_lift(P, D):
    u = lambda x: x * D; w = Tw()
    svg = rr(280, 700, 800, 740, 8, fill=DARK, stroke=RIMC, sw=3) + g(battery(330, 420), id=f"{P}bt")
    svg += g(rr(300, 380, 780, 410, 8, fill=STEELC) + rr(520, 350, 560, 410, 6, fill=(220, 225, 235)), id=f"{P}hd") + arrow(900, 560, 900, 330, YEL, id=f"{P}ar")
    w.to(f"#{P}hd", {"y": -160, "duration": u(.2), "ease": "power2.out"}, u(.3)); w.to(f"#{P}hd", {"opacity": 0, "duration": .1}, u(.52))
    w.to(f"#{P}bt", {"y": -260, "duration": u(.45), "ease": "power2.inOut"}, u(.35)); fade(w, f"#{P}ar", u(.4), .2)
    return dict(svg=svg, tw=w, labels=[("REMOVE THE HOLD-DOWN", .05, .45), ("HEAVY: LIFT WITH YOUR LEGS", .5, None)])

def v_batt_new(P, D):
    u = lambda x: x * D; w = Tw()
    svg = rr(280, 700, 800, 740, 8, fill=DARK, stroke=RIMC, sw=3) + g("".join(line(300 + i * 80, 690, 360 + i * 80, 650, (230, 240, 240), 5) for i in range(6)) + ell(540, 520, 60, fill=(120, 126, 142)) + g(line(480, 520, 600, 520, STEELC, 8), id=f"{P}br"), id=f"{P}cr")
    svg += g(battery(330, 420), id=f"{P}bt") + g(rr(300, 380, 780, 410, 8, fill=STEELC), id=f"{P}hd") + tick(900, 280, id=f"{P}t")
    w.to(f"#{P}br", {"rotation": 720, "svgOrigin": "540 520", "duration": u(.3), "ease": "none"}, u(.03)); w.to(f"#{P}cr", {"opacity": 0, "duration": .15}, u(.36))
    w.fromto(f"#{P}bt", {"y": -300, "opacity": 0}, {"y": 0, "opacity": 1, "duration": u(.35), "ease": "power2.out"}, u(.4))
    fade(w, f"#{P}hd", u(.8), .15); pop(w, f"#{P}t", 900, 280, u(.82))
    return dict(svg=svg, tw=w, labels=[("SCRUB OFF THE CRUD", .05, .38), ("STRAP IT DOWN", .45, None)])

def v_batt_back(P, D):
    u = lambda x: x * D; w = Tw()
    svg = battery() + clamp(670, 400, RDC, 1, id=f"{P}cp") + clamp(410, 400, BLK, -1, id=f"{P}cn")
    svg += g(ell(670, 190, 40, fill=RED, stroke=WHITE, sw=5) + text(670, 190, "1", 50, WHITE), id=f"{P}n1") + g(ell(410, 190, 40, fill=BLK, stroke=WHITE, sw=5) + text(410, 190, "2", 50, WHITE), id=f"{P}n2") + tick(540, 800, id=f"{P}t")
    w.fromto(f"#{P}cp", {"y": -120}, {"y": 0, "duration": u(.3), "ease": "power3.out"}, u(.1)); w.fromto(f"#{P}cn", {"y": -120}, {"y": 0, "duration": u(.3), "ease": "power3.out"}, u(.55))
    fade(w, f"#{P}n2", u(.5), .2); pop(w, f"#{P}t", 540, 800, u(.85))
    return dict(svg=svg, tw=w, labels=[])

# ------------------------------------------------------------------ wipers
PIV = (800, 770); TH0 = math.pi + .1; BX = PIV[0] + 470 * math.cos(TH0); BY = PIV[1] + 470 * math.sin(TH0)

def rot_pt(p, deg):
    a = math.radians(deg); dx, dy = p[0] - PIV[0], p[1] - PIV[1]
    return PIV[0] + dx * math.cos(a) - dy * math.sin(a), PIV[1] + dx * math.sin(a) + dy * math.cos(a)

def windshield():
    return poly([(140, 70), (940, 70), (1010, 730), (70, 730)], (140, 190, 225), (30, 30, 38), 14) + poly([(140, 70), (330, 70), (210, 730), (70, 730)], WHITE, opacity=.18) + rr(40, 735, 1040, 880, 30, fill=(30, 32, 44))

def wiper(P, rot=0.0, tab=False, animate_rot=False, blade_id=True):
    blade = g(rrect_t(round(BX, 1), round(BY, 1), 480, 22, round(math.degrees(TH0) - 180, 1), (14, 14, 20), stroke=STEELC, stroke_width=3), id=f"{P}bl")
    tabc = g(ell(round(BX, 1), round(BY, 1), 16, fill=RED if tab else (90, 94, 110)), id=f"{P}tb")
    inner = line(PIV[0], PIV[1], round(BX, 1), round(BY, 1), (40, 42, 54), 14) + ell(PIV[0], PIV[1], 22, fill=(70, 72, 90), stroke=STEELC, sw=4) + blade + tabc
    return g(inner, id=f"{P}wp") if animate_rot else g(inner, transform=f"rotate({rot} {PIV[0]} {PIV[1]})")

def v_hook_wiper(P, D):
    w = Tw()
    svg = windshield() + "".join(line(200 + i * 150, 600 - 40 * i, 330 + i * 150, 420 - 30 * i, WHITE, 10, opacity=.4) for i in range(5)) + wiper(P) + emoji(540, 330, "😵", 200, id=f"{P}em", fill=WHITE)
    w.to(f"#{P}em", {"y": -12, "duration": .5, "ease": "sine.inOut", "repeat": 7, "yoyo": True}, 0)
    return dict(svg=svg, tw=w, labels=[])

def v_wipe1(P, D):
    u = lambda x: x * D; w = Tw()
    svg = windshield() + wiper(P, animate_rot=True) + arrow(300, 640, 300, 420, YEL, id=f"{P}ar")
    w.to(f"#{P}wp", {"rotation": 43, "svgOrigin": f"{PIV[0]} {PIV[1]}", "duration": u(.4), "ease": "power2.inOut"}, u(.15)); fade(w, f"#{P}ar", u(.4), .2)
    return dict(svg=svg, tw=w, labels=[("LIFT THE ARM OFF THE GLASS", .05, None)])

def v_wipe2(P, D):
    u = lambda x: x * D; w = Tw(); bx, by = rot_pt((BX, BY), 34.4)
    svg = windshield() + wiper(P, 34.4, tab=True) + ell(round(bx, 1), round(by, 1), 50, stroke=YEL, sw=8, id=f"{P}rg") + arrow(round(bx - 220), round(by - 120), round(bx - 40), round(by - 20), YEL, 10)
    w.to(f"#{P}rg", {"scale": 1.25, "svgOrigin": f"{bx:.1f} {by:.1f}", "duration": .4, "ease": "sine.inOut", "repeat": 7, "yoyo": True}, 0)
    return dict(svg=svg, tw=w, labels=[("FIND THE TAB", .1, None)])

def v_wipe3(P, D):
    u = lambda x: x * D; w = Tw()
    svg = windshield() + wiper(P, 34.4, tab=True)
    w.to(f"#{P}bl", {"x": 517, "y": 52, "duration": u(.5), "ease": "power2.inOut"}, u(.35))
    return dict(svg=svg, tw=w, labels=[("PRESS THE TAB, SLIDE IT OFF", .05, None)])

def v_wipe4(P, D):
    u = lambda x: x * D; w = Tw()
    svg = windshield() + wiper(P, 34.4) + tick(820, 280, id=f"{P}t")
    w.fromto(f"#{P}bl", {"x": 517, "y": 52}, {"x": 0, "y": 0, "duration": u(.5), "ease": "power3.out"}, u(.1))
    pop(w, f"#{P}t", 820, 280, u(.65))
    return dict(svg=svg, tw=w, labels=[("CLICK!", .6, None)])

def v_wipe5(P, D):
    u = lambda x: x * D; w = Tw()
    svg = windshield() + "".join(ell(300 + (i * 97) % 500, 250 + (i * 53) % 350, 7, fill=(210, 235, 255), id=f"{P}dr{i}", opacity=0) for i in range(10)) + wiper(P, animate_rot=True)
    w.fromto(f"#{P}wp", {"rotation": 43, "svgOrigin": f"{PIV[0]} {PIV[1]}"}, {"rotation": 0, "svgOrigin": f"{PIV[0]} {PIV[1]}", "duration": u(.3), "ease": "power2.inOut"}, u(.05))
    for i in range(10):
        fade(w, f"#{P}dr{i}", u(.4) + i * .03, .15)
    t0 = u(.55)
    w.to(f"#{P}wp", {"rotation": 40, "svgOrigin": f"{PIV[0]} {PIV[1]}", "duration": u(.18), "ease": "sine.inOut"}, t0); w.to(f"#{P}wp", {"rotation": 0, "svgOrigin": f"{PIV[0]} {PIV[1]}", "duration": u(.18), "ease": "sine.inOut"}, t0 + u(.18))
    for i in range(10): w.to(f"#{P}dr{i}", {"opacity": 0, "duration": .15}, t0 + .1 + i * .04)
    return dict(svg=svg, tw=w, labels=[("TEST WITH WASHER FLUID", .4, None)])

VIS.update({
    "air_open": v_air_open, "air_pull": v_air_pull, "air_light": v_air_light, "air_new": v_air_new, "air_close": v_air_close,
    "hook_vent": v_hook_vent, "glove1": v_glove1, "glove2": v_glove2, "glove3": v_glove3, "glove4": v_glove4, "glove5": v_glove5,
    "hook_oil": v_hook_oil, "car_lift": v_car_lift, "drain": v_drain, "ofilter": v_ofilter, "plug_back": v_plug_back, "pour": v_pour, "dipstick": v_dipstick,
    "intake_all": v_intake(None), "intake0": v_intake(0, "CATCHES DIRT + BUGS"), "intake1": v_intake(1, "MEASURES THE AIR"), "intake2": v_intake(2, "THE AIR VALVE"),
    "intake3": v_intake(3, "SPLITS AIR TO EACH CYLINDER"), "intake4": v_intake(4, "FUEL + AIR + SPARK = POWER", fire=True),
    "hook_plug": v_hook_plug, "plug_coil": v_plug_coil, "plug_blow": v_plug_blow, "plug_socket": v_plug_socket, "plug_gap": v_plug_gap, "plug_in": v_plug_in, "plug_coilback": v_plug_coilback,
    "hook_batt": v_hook_batt, "batt_safe": v_batt_safe, "batt_neg": v_batt_neg, "batt_pos": v_batt_pos, "batt_lift": v_batt_lift, "batt_new": v_batt_new, "batt_back": v_batt_back,
    "hook_wiper": v_hook_wiper, "wipe1": v_wipe1, "wipe2": v_wipe2, "wipe3": v_wipe3, "wipe4": v_wipe4, "wipe5": v_wipe5,
})
