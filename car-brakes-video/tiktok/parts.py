"""Reusable vector drawings and scene factories for the car-DIY episodes (canvas 1080x900)."""
import math
from engine import *

INK = (20, 12, 40)
GLASS = (140, 190, 225)
STEEL = (170, 176, 190)
DARK = (62, 66, 82)
RIM = (110, 116, 134)
OIL = (255, 170, 0)

def lerp(a, b, k): return a + (b - a) * k

def kf(u, keys):
    """Eased piecewise value: keys = [(u0, v0), (u1, v1), ...]."""
    if u <= keys[0][0]: return keys[0][1]
    for (u0, v0), (u1, v1) in zip(keys, keys[1:]):
        if u <= u1: return v0 + (v1 - v0) * eo(seg(u, u0, u1))
    return keys[-1][1]

def rotpts(pts, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]

def rrot(cv, cx, cy, w, h, a, fill, outline=None, ow=3):
    cv.poly(rotpts([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], cx, cy, a), fill, outline, ow)

def pill(cv, text, y, size=38, fill=(255, 255, 255), col=INK):
    w = F(size).getlength(text) + 80
    cv.rr(CX - w / 2, y - size * .9, CX + w / 2, y + size * .9, size * .9, fill=fill)
    cv.text(CX, y, text, size, col)

def tag(cv, u, a, text, y=80, size=38, fill=(255, 255, 255), col=INK):
    if eob(seg(u, a, a + .12)) > .3: pill(cv, text, y, size, fill, col)

def tick(cv, x, y, s=1.0):
    if s <= .02: return
    cv.ell(x, y, 70 * s, fill=(40, 210, 110), outline=(255, 255, 255), width=6)
    cv.line([(x - 30 * s, y), (x - 6 * s, y + 26 * s), (x + 36 * s, y - 28 * s)], (255, 255, 255), 14 * s)

def cross(cv, x, y, s=1.0):
    if s <= .02: return
    cv.ell(x, y, 70 * s, fill=TTRED, outline=(255, 255, 255), width=6)
    cv.line([(x - 28 * s, y - 28 * s), (x + 28 * s, y + 28 * s)], (255, 255, 255), 14 * s)
    cv.line([(x - 28 * s, y + 28 * s), (x + 28 * s, y - 28 * s)], (255, 255, 255), 14 * s)

def drop(cv, x, y, r, col=OIL):
    cv.poly([(x, y - r * 1.9), (x + r * .95, y - r * .25), (x - r * .95, y - r * .25)], col)
    cv.ell(x, y, r, fill=col)
    cv.ell(x - r * .35, y - r * .2, r * .22, fill=(255, 235, 170))

def stand(cv, x, gy, top, k=1.0):
    cv.poly([(x - 80 * k, gy), (x + 80 * k, gy), (x + 20, gy - 36 * k), (x - 20, gy - 36 * k)], ORANGE)
    cv.rr(x - 18, top, x + 18, gy - 36 * k, 6, fill=(255, 170, 60))
    cv.rr(x - 50, top - 12, x + 50, top + 6, 8, fill=(255, 200, 90))

def stars(cv, s, t, cx, cy, spread=330):
    for i, (dx, dy) in enumerate([(-spread, -120), (spread - 10, -150), (spread + 20, 90), (-spread + 30, 120)]):
        star(cv, cx + dx, cy + dy, 26 * s * (0.8 + 0.2 * math.sin(t * 9 + i)), YELLOW)

# ------------------------------------------------------------------ hooks / cta
def hook_price(old, new, lab_old, lab_new, e1="💸", e2="🔧"):
    def v(cv, u, t):
        cv.text(CX, 200, old, 330, (255, 255, 255), stroke=10)
        cv.text(CX, 380, lab_old, 44, (205, 210, 232))
        p = eo(seg(u, .22, .36))
        if p > 0: cv.line([(160, 330), (160 + p * 760, 330 - p * 220)], TTRED, 26)
        s = eob(seg(u, .40, .55))
        if s > .02:
            cv.text(CX, 640, new, 330 * s, LIME, stroke=10); cv.text(CX, 820, lab_new, 44 * s, (205, 210, 232))
            stars(cv, s, t, CX, 640)
        cv.emoji(150 + 10 * math.sin(t * 4), 70, e1, 110); cv.emoji(930, 70 + 10 * math.sin(t * 4 + 1), e2, 110)
    return v

def make_cta(nxt):
    def v(cv, u, t):
        k = 1 + 0.06 * math.sin(t * 8)
        cv.rr(CX - 330 * k, 130 - 90 * k, CX + 330 * k, 130 + 90 * k, 90, fill=TTRED, outline=(255, 255, 255), width=8)
        cv.text(CX, 130, "FOLLOW  +", 100 * k, (255, 255, 255))
        cv.text(CX, 300, "SAVE THIS FOR LATER", 54, (255, 255, 255), stroke=6)
        w = F(46).getlength("NEXT: " + nxt) + 70
        cv.rr(CX - w / 2, 365, CX + w / 2, 445, 40, fill=YELLOW); cv.text(CX, 405, "NEXT: " + nxt, 46, INK)
        for i in range(7):
            y = 780 - (t * 140 + i * 110) % 300
            cv.emoji(150 + i * 130 + 20 * math.sin(t * 3 + i), y, ["❤️", "🔔", "🔧", "🚗"][i % 4], 96)
        cv.text(CX, 800, "ALWAYS USE JACK STANDS", 34, (255, 255, 255, 220))
        cv.text(CX, 845, "& CHECK YOUR MANUAL FOR SPECS", 34, (255, 255, 255, 220))
    return v

# ------------------------------------------------------------------ filters (engine air, cabin)
def filt(cv, x, y, w, h, dirt=0.0, leaves=False):
    x0, y0, x1, y1 = x - w / 2, y - h / 2, x + w / 2, y + h / 2
    base, dirty = (245, 245, 238), (112, 88, 62)
    col = tuple(int(lerp(base[i], dirty[i], dirt)) for i in range(3))
    cv.rr(x0, y0, x1, y1, 14, fill=(34, 34, 42))
    cv.rr(x0 + 12, y0 + 12, x1 - 12, y1 - 12, 6, fill=col)
    n = max(3, int((w - 24) / 16))
    for i in range(n + 1):
        xx = x0 + 12 + i * (w - 24) / n
        cv.line([(xx, y0 + 12), (xx, y1 - 12)], tuple(int(c * .78) for c in col), 3)
    for i in range(int(45 * dirt)):
        px = x0 + 18 + (i * 137) % max(1, int(w - 36)); py = y0 + 18 + (i * 71) % max(1, int(h - 36))
        cv.ell(px, py, 3 + i % 4, fill=(62, 46, 30))
    if leaves:
        for i, (lx, ly) in enumerate([(.2, .3), (.55, .6), (.8, .25)]):
            rrot(cv, x0 + w * lx, y0 + h * ly, 46, 20, .6 + i, (90, 140, 50))

def airbox(cv, lid=0.0, clips=0.0, x0=190, x1=890, yt=400, yb=700):
    cv.rr(x0, yt, x1, yb, 24, fill=DARK, outline=RIM, width=4)
    cv.rr(x0 + 30, yt + 30, x1 - 30, yb - 30, 12, fill=(26, 28, 38))
    cv.poly(rotpts([(x0, yt - 70), (x1, yt - 70), (x1, yt), (x0, yt)], x0, yt, -lid * .95), (82, 88, 106), (130, 136, 154), 4)
    for cx_, sd in ((x0 + 90, -1), (x1 - 90, 1)):
        cv.poly(rotpts([(cx_ - 22, yt - 20), (cx_ + 22, yt - 20), (cx_ + 22, yt + 60), (cx_ - 22, yt + 60)], cx_, yt + 60, sd * clips * 1.3), YELLOW, (150, 130, 0), 3)

def v_air_open(cv, u, t):
    clips = eo(seg(u, .1, .4)); lid = eo(seg(u, .45, .8))
    airbox(cv, lid, clips)
    if lid > .1: filt(cv, CX, 560, 560, 200)
    tag(cv, u, .05, "2 CLIPS OR A FEW SCREWS", y=130, size=36)

def v_air_pull(cv, u, t):
    y = kf(u, [(.1, 560), (.6, 190)])
    airbox(cv, 1.0, 1.0); filt(cv, CX, y, 560, 200, dirt=.85)
    if u > .15: arrow(cv, 900, 560, 900, 330, YELLOW)
    tag(cv, u, .1, "PULL STRAIGHT UP", y=90)

def v_air_light(cv, u, t):
    cv.ell(160, 170, 78, fill=(255, 236, 120)); cv.ell(160, 170, 110, outline=(255, 236, 120, 120), width=6)
    fx, fy, fw, fh = 700, 480, 440, 400
    filt(cv, fx, fy, fw, fh, dirt=1.0)
    for i in range(6):
        ty = fy - fh / 2 + 30 + i * (fh - 60) / 5
        cv.line([(220, 210), (fx - fw / 2 - 6, ty)], (255, 236, 120), 6)
    s = eob(seg(u, .45, .65))
    if s > .02: cross(cv, fx, fy, s)
    tag(cv, u, .5, "NO LIGHT? REPLACE IT", y=790, size=40)

def v_air_new(cv, u, t):
    airbox(cv, 1.0, 1.0)
    sw = eo(seg(u, .05, .4))
    if u < .45:
        for i in range(9): cv.ell(240 + (i * 83) % 600, 520 + (i * 47) % 120, 5, fill=(150, 120, 90))
        cv.rr(200 + sw * 560, 470, 300 + sw * 560, 630, 30, fill=(255, 255, 255))
    y = kf(u, [(.45, 120), (.85, 560)])
    if u >= .4: filt(cv, CX, y, 560, 200, dirt=0)
    tag(cv, u, .5, "SAME SHAPE, SAME SIDE UP", y=60, size=34)

def v_air_close(cv, u, t):
    lid = 1 - eo(seg(u, .1, .5)); clips = 1 - eo(seg(u, .5, .8))
    airbox(cv, lid, clips)
    if lid > .1: filt(cv, CX, 560, 560, 200)
    tick(cv, CX, 220, eob(seg(u, .75, .9)))

# ------------------------------------------------------------------ cabin filter
def dash(cv):
    cv.rr(60, 100, 1020, 660, 50, fill=(48, 44, 72), outline=(96, 90, 130), width=4)
    cv.rr(120, 135, 440, 185, 14, fill=(30, 28, 48)); cv.rr(640, 135, 960, 185, 14, fill=(30, 28, 48))

def glovebox(cv, o, filter_in=True, filt_y=None, dirt=.8):
    cv.rr(180, 240, 900, 540, 24, fill=(14, 14, 20))
    if o > .02:
        cv.rr(330, 290, 750, 430, 10, fill=(34, 38, 52), outline=RIM, width=3)
        if filter_in: filt(cv, CX, 360 if filt_y is None else filt_y, 380, 110, dirt=dirt, leaves=dirt > .5)
        cv.rr(330, 435, 750, 480, 8, fill=(96, 102, 120), outline=RIM, width=3)
    y0, y1 = lerp(240, 560, o), lerp(540, 690, o)
    cv.rr(180, y0, 900, y1, 24, fill=(86, 92, 112), outline=(130, 136, 156), width=4)
    if o < .3: cv.rr(470, y0 + 40, 610, y0 + 62, 10, fill=(60, 64, 80))

def v_glove1(cv, u, t):
    dash(cv); o = eo(seg(u, .2, .6)) * .35
    glovebox(cv, o, False)
    for i, (x, a) in enumerate([(380, .5), (540, -.4), (700, 1.0)]):
        k = seg(u, .35 + i * .08, .9)
        if k > 0: rrot(cv, x, 400 + k * 440, 120, 22, a + k * 3, [YELLOW, PINK, CYAN][i])
    tag(cv, u, .05, "EMPTY IT FIRST", y=80)

def v_glove2(cv, u, t):
    dash(cv); o = eo(seg(u, .45, .85))
    glovebox(cv, o, True)
    p = 12 * math.sin(t * 9)
    if o < .3:
        arrow(cv, 70 - p, 390, 170 - p, 390, YELLOW); arrow(cv, 1010 + p, 390, 910 + p, 390, YELLOW)
    tag(cv, u, .05, "SQUEEZE THE SIDES", y=80)

def v_glove3(cv, u, t):
    dash(cv); glovebox(cv, 1.0, False)
    y = kf(u, [(.25, 360), (.75, 780)])
    filt(cv, CX, y, 380, 110, dirt=.9, leaves=True)
    tag(cv, u, .05, "COVER OFF, FILTER OUT", y=80)

def v_glove4(cv, u, t):
    for x, ok in ((300, True), (780, False)):
        filt(cv, x, 430, 340, 260, dirt=0)
        ay0, ay1 = (330, 520) if ok else (520, 330)
        arrow(cv, x, ay0, x, ay1, TTRED if not ok else (40, 150, 90), 22)
    s = eob(seg(u, .35, .55))
    tick(cv, 300, 210, s); cross(cv, 780, 210, s)

def v_glove5(cv, u, t):
    dash(cv); o = 1 - eo(seg(u, .45, .7))
    glovebox(cv, o, False)
    y = kf(u, [(.05, 800), (.4, 360)])
    if o > .02: filt(cv, CX, y, 380, 110, dirt=0)
    s = eob(seg(u, .75, .9))
    tick(cv, CX, 790, s)
    if u > .7:
        for i in range(3):
            xs = 300 + i * 240
            cv.line([(xs + 14 * math.sin(t * 6 + k * .8), 700 + k * 14) for k in range(6)], (170, 235, 255), 8) if False else None

def v_hook_vent(cv, u, t):
    cv.rr(220, 440, 860, 640, 30, fill=(30, 28, 48), outline=RIM, width=5)
    for i in range(5): cv.line([(250, 470 + i * 38), (830, 470 + i * 38)], (90, 96, 120), 8)
    for j in range(5):
        pts = [(300 + j * 120 + 26 * math.sin(t * 5 + k * .9 + j), 420 - k * 46 - (t * 60 + j * 40) % 40) for k in range(7)]
        cv.line(pts, (120, 200, 80), 12)
    cv.emoji(540, 120 + 8 * math.sin(t * 5), "🤢", 190)

# ------------------------------------------------------------------ oil change
def oil_filter(cv, x, y, rot=0.0):
    cv.rr(x - 85, y, x + 85, y + 230, 26, fill=(235, 112, 28), outline=(255, 170, 90), width=3)
    cv.rr(x - 92, y, x + 92, y + 28, 10, fill=(150, 60, 15))
    cv.rr(x - 85 + 40 + 30 * math.sin(rot), y + 70, x - 85 + 80 + 30 * math.sin(rot), y + 190, 6, fill=(250, 245, 235))
    cv.rr(x - 92, y + 205, x + 92, y + 235, 10, fill=(120, 50, 12))

def v_hook_oil(cv, u, t):
    drop(cv, CX, 380 + 12 * math.sin(t * 4), 150)
    cv.text(CX, 640, "6 STEPS", 190, (255, 255, 255), stroke=10)
    cv.text(CX, 800, "NO QUICK LUBE NEEDED", 48, (205, 210, 232))
    s = eob(seg(u, .1, .3))
    stars(cv, s, t, CX, 400, 340) if s > .02 else None

def v_car_lift(cv, u, t):
    lift = kf(u, [(.3, 0), (.6, 40)]); gy = 800
    cv.line([(30, gy), (1050, gy)], (130, 136, 160), 8)
    cv.rr(100, 440 - lift, 980, 650 - lift, 60, fill=(66, 72, 108), outline=(110, 118, 160), width=4)
    cv.rr(330, 320 - lift, 760, 450 - lift, 40, fill=(66, 72, 108), outline=(110, 118, 160), width=4)
    cv.rr(370, 345 - lift, 540, 430 - lift, 14, fill=GLASS); cv.rr(560, 345 - lift, 720, 430 - lift, 14, fill=GLASS)
    for wx in (280, 800):
        cv.ell(wx, gy - 95 - lift, 95, fill=(22, 22, 26), outline=(78, 80, 92), width=5); cv.ell(wx, gy - 95 - lift, 50, fill=(190, 196, 208))
    st = eob(seg(u, .5, .7))
    if st > .02:
        for sx in (430, 680): stand(cv, sx, gy, 650 - lift, st)
    if u < .3:
        for i in range(3):
            pts = [(300 + i * 160 + 18 * math.sin(t * 6 + k + i), 320 - k * 24) for k in range(6)]
            cv.line(pts, (255, 120, 60), 8)
    tag(cv, u, .05, "WARM IT UP A FEW MINUTES", y=90, size=34)

def v_drain(cv, u, t):
    cv.poly([(220, 130), (860, 130), (800, 410), (280, 410)], DARK, RIM, 4)
    out = eo(seg(u, .1, .35)); by = 410 + out * 70
    flow = u > .3
    lvl = kf(u, [(.3, 0), (.9, 1)])
    cv.poly([(160, 690), (620, 690), (580, 810), (200, 810)], (50, 54, 70), RIM, 4)
    if lvl > 0: cv.poly([(200 + 12 * (1 - lvl), 810 - 100 * lvl), (580 - 12 * (1 - lvl), 810 - 100 * lvl), (580, 806), (200, 806)], OIL)
    if flow:
        cv.line([(360, by + 20), (360, 690)], OIL, 14)
        for i in range(4):
            yy = 470 + ((t * 420 + i * 55) % 220); cv.ell(360, yy, 9, fill=(255, 215, 110))
    bolt(cv, 360, by, 28, out * 9)
    tag(cv, u, .05, "HOT OIL! BE CAREFUL", y=640, size=38)

def v_ofilter(cv, u, t):
    cv.rr(120, 130, 960, 300, 24, fill=DARK, outline=RIM, width=4)
    out = eo(seg(u, .12, .4)); nw = eo(seg(u, .66, .9))
    if u < .45: oil_filter(cv, 700, 300 + out * 360, rot=out * 6)
    else:
        oil_filter(cv, 700, 660 - nw * 360, rot=nw * 6)
        if u < .66: drop(cv, 700, 500 - (u - .45) * 300, 20)
    cv.ell(700, 300, 90, ry=12, outline=OIL, width=6) if .45 <= u < .66 else None
    tag(cv, u, .5, "OIL THE NEW GASKET", y=90, size=38)
    tag(cv, u, .06, "SPIN OFF THE OLD FILTER", y=90, size=34) if u < .45 else None

def v_plug_back(cv, u, t):
    cv.poly([(220, 130), (860, 130), (800, 410), (280, 410)], DARK, RIM, 4)
    inn = eo(seg(u, .1, .45)); by = 480 - inn * 70
    bolt(cv, 360, by, 28, inn * 9)
    a = -.9 + .5 * math.sin(inn * 9) * 0.3
    cv.line([(360, by), (360 + 340 * math.cos(a - .5), by + 340 * math.sin(a - .5) * -1)], (200, 205, 215), 22)
    s = eob(seg(u, .6, .8)); tick(cv, 760, 600, s)
    tag(cv, u, .05, "TIGHTEN TO SPEC", y=700, size=40)
    tag(cv, u, .5, "NOT GORILLA TIGHT", y=800, size=36)

def v_pour(cv, u, t):
    cv.rr(230, 470, 850, 640, 24, fill=DARK, outline=RIM, width=4)
    cv.ell(579, 470, 70, ry=16, fill=(30, 34, 46), outline=STEEL, width=5)
    cv.poly([(509, 400), (649, 400), (599, 470), (559, 470)], (200, 205, 215), (120, 126, 140), 3)
    a = kf(u, [(0, -.3), (.3, -2.4)])
    c = (680, 250)
    rrot(cv, *c, 130, 200, a, (40, 44, 58), (120, 126, 142), 4)
    rrot(cv, c[0], c[1], 130, 70, a, OIL)
    for pts_, col in (([(-25, -135), (25, -135), (25, -100), (-25, -100)], (200, 205, 215)),):
        cv.poly(rotpts([(c[0] + x, c[1] + y) for x, y in pts_], *c, a), col)
    if a < -2.0:
        tip = rotpts([(c[0], c[1] - 138)], *c, a)[0]
        cv.line([(tip[0], tip[1]), (tip[0], 440)], OIL, 16)
    tag(cv, u, .1, "OIL TYPE + AMOUNT: OWNER'S MANUAL", y=790, size=30)

def v_dipstick(cv, u, t):
    cv.rr(CX - 40, 560, CX + 40, 800, 16, fill=DARK, outline=RIM, width=4)
    off = kf(u, [(.05, 0), (.25, 360), (.45, 360), (.6, 0), (.75, 360)])
    top, bot = 560 - off, 560 - off + 330
    cv.rr(CX - 7, top, CX + 7, bot, 6, fill=STEEL)
    cv.ell(CX, top - 20, 30, ry=24, outline=YELLOW, width=10)
    cv.rr(CX - 7, bot - 100, CX + 7, bot - 40, 4, fill=OIL)
    for yy in (bot - 120, bot - 20): cv.line([(CX - 34, yy), (CX + 34, yy)], (255, 255, 255), 5)
    if .3 < u < .48: cv.rr(CX - 60 + 120 * ((u - .3) / .18), top + 120, CX + 60 + 120 * ((u - .3) / .18), top + 200, 20, fill=(255, 255, 255))
    tick(cv, 800, 400, eob(seg(u, .8, .95)))
    tag(cv, u, .78, "RECYCLE THE OLD OIL", y=840, size=38)

# ------------------------------------------------------------------ intake system
RUN = [290, 430, 650, 790]
MAIN = [(60, 160), (880, 160), (880, 330), (540, 330), (540, 470)]

def pt_along(path, d):
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        l = math.hypot(x1 - x0, y1 - y0)
        if d <= l: k = d / l if l else 0; return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        d -= l
    return path[-1]

def intake(hl, label=None, fire=False):
    def v(cv, u, t):
        dim = (70, 66, 96)
        def col(i, c): return c if hl is None or hl == i else dim
        cv.line(MAIN, (44, 48, 68), 56)
        cv.rr(40, 90, 300, 240, 24, fill=col(0, (0, 190, 215)), outline=(255, 255, 255) if hl == 0 else None, width=6)
        cv.text(170, 165, "AIR FILTER", 30, INK if hl in (None, 0) else (150, 146, 180))
        cv.rr(360, 130, 560, 190, 8, fill=(60, 64, 84)); cv.rr(400, 100, 520, 220, 14, fill=col(1, LIME), outline=(255, 255, 255) if hl == 1 else None, width=6)
        cv.text(460, 160, "MAF", 34, INK if hl in (None, 1) else (150, 146, 180))
        cv.rr(660, 100, 840, 220, 18, fill=col(2, ORANGE), outline=(255, 255, 255) if hl == 2 else None, width=6)
        ang = .3 + (1.1 * (0.5 + 0.5 * math.sin(t * 2.6)) if hl == 2 else .5)
        cv.line([(750 - 44 * math.cos(ang), 160 - 44 * math.sin(ang)), (750 + 44 * math.cos(ang), 160 + 44 * math.sin(ang))], INK, 10)
        cv.rr(230, 440, 850, 520, 24, fill=col(3, PINK), outline=(255, 255, 255) if hl == 3 else None, width=6)
        cv.text(540, 480, "INTAKE MANIFOLD", 32, INK if hl in (None, 3) else (150, 146, 180))
        for i, x in enumerate(RUN):
            cv.rr(x - 20, 520, x + 20, 650, 6, fill=col(3, (210, 60, 140)))
            hot = fire and int(t * 5) % 4 == i
            cv.rr(x - 62, 650, x + 62, 810, 14, fill=(255, 200, 40) if hot else col(4, PURPLE), outline=(255, 255, 255) if hl == 4 else None, width=6)
            py = 700 + 20 * math.sin(t * 6 + i * 1.6)
            cv.rr(x - 44, py, x + 44, py + 40, 6, fill=(220, 222, 235) if not hot else (255, 255, 255))
            if hot: star(cv, x, 640, 34, (255, 255, 255))
        L0 = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(MAIN, MAIN[1:]))
        for j in range(16):
            d = (t * 260 + j * 70) % (L0 + 260)
            if d <= L0: x, y = pt_along(MAIN, d)
            else:
                rx = RUN[j % 4]; x, y = pt_along([(540, 470), (rx, 480), (rx, 700)], d - L0)
            cv.ell(x, y, 9, fill=(200, 245, 255))
        if label: pill(cv, label, 858, 36)
    return v

# ------------------------------------------------------------------ spark plugs
def plug(cv, x, y, s=1.0, rot=0.0):
    cv.rr(x - 12 * s, y, x + 12 * s, y + 40 * s, 4 * s, fill=(200, 204, 214))
    cv.rr(x - 34 * s, y + 40 * s, x + 34 * s, y + 200 * s, 16 * s, fill=(246, 244, 236), outline=(190, 186, 176), width=3)
    for i in range(3): cv.line([(x - 34 * s, y + 80 * s + i * 28 * s), (x + 34 * s, y + 80 * s + i * 28 * s)], (205, 200, 190), 3)
    cv.rr(x - 46 * s, y + 200 * s, x + 46 * s, y + 250 * s, 6 * s, fill=STEEL, outline=(210, 215, 225), width=3)
    cv.rr(x - 34 * s, y + 250 * s, x + 34 * s, y + 330 * s, 4 * s, fill=(176, 182, 196))
    for i in range(7): cv.line([(x - 34 * s, y + 256 * s + (i * 11 * s + rot * 30 * s) % (70 * s)), (x + 34 * s, y + 256 * s + (i * 11 * s + rot * 30 * s) % (70 * s))], (120, 126, 140), 3)
    cv.rr(x - 8 * s, y + 330 * s, x + 8 * s, y + 356 * s, 2, fill=(215, 220, 230))
    cv.line([(x + 30 * s, y + 330 * s), (x + 30 * s, y + 352 * s), (x + 3 * s, y + 352 * s)], (150, 156, 170), 9 * s)

def coil(cv, x, y, hot=False):
    cv.rr(x - 44, y, x + 44, y + 150, 14, fill=(62, 44, 110), outline=(130, 110, 190), width=3)
    cv.rr(x + 20, y + 30, x + 66, y + 70, 6, fill=(30, 28, 44))
    cv.rr(x - 26, y + 150, x + 26, y + 200, 6, fill=(40, 40, 52))

def engine_top(cv):
    cv.rr(100, 330, 980, 700, 40, fill=(54, 58, 76), outline=RIM, width=4)

def v_hook_plug(cv, u, t):
    plug(cv, CX, 150 + 6 * math.sin(t * 8), 1.5)
    for i in range(5):
        a = i * 1.3 + t * 10
        star(cv, CX + 40 + 90 * math.cos(a), 690 + 60 * math.sin(a), 22 + 8 * math.sin(t * 12 + i), YELLOW)
    cv.text(CX, 840, "MISFIRE? WORN PLUGS?", 44, (205, 210, 232))

def v_plug_coil(cv, u, t):
    engine_top(cv)
    lift = eo(seg(u, .25, .6)) * 220
    for i, x in enumerate((220, 420, 620, 820)):
        if i == 1: coil(cv, x, 380 - lift)
        else: coil(cv, x, 380)
    cv.ell(420, 560, 40, ry=12, fill=(14, 14, 20))
    tag(cv, u, .1, "ONE AT A TIME", y=130)

def v_plug_blow(cv, u, t):
    cv.rr(100, 520, 980, 760, 40, fill=(54, 58, 76), outline=RIM, width=4)
    cv.ell(CX + 100, 620, 100, ry=28, fill=(12, 12, 18), outline=STEEL, width=6)
    cv.rr(100, 390, 300, 440, 12, fill=ORANGE); cv.rr(280, 405, 400, 425, 6, STEEL)
    for i in range(9):
        k = ((t * 1.8 + i * .13) % 1)
        cv.ell(420 + k * 280, 430 + 150 * k, 4, fill=(190, 230, 255))
    for i in range(8):
        k = ((t * 1.2 + i * .17) % 1)
        cv.ell(CX + 100 + (i - 4) * 18 * k, 600 - 200 * k, 5, fill=(150, 120, 90))
    tag(cv, u, .1, "KEEP DIRT OUT OF THE HOLE", y=140, size=36)

def v_plug_socket(cv, u, t):
    cv.rr(100, 600, 980, 780, 40, fill=(54, 58, 76), outline=RIM, width=4)
    cv.ell(CX, 640, 90, ry=24, fill=(12, 12, 18), outline=STEEL, width=6)
    up = eo(seg(u, .3, .85)) * 220
    y = 380 - up
    plug(cv, CX, y, .9, u * 14)
    cv.rr(CX - 58, y + 18, CX + 58, y + 258, 12, fill=(96, 102, 120), outline=STEEL, width=4)
    cv.rr(CX - 20, 160, CX + 20, y + 18, 4, fill=STEEL)
    ang = .35 * math.sin(u * 22)
    cv.line([(CX, 160), (CX + 330 * math.cos(ang), 160 + 330 * math.sin(ang))], (210, 214, 224), 20)
    cv.ell(CX, 160, 40, fill=(120, 126, 142), outline=STEEL, width=4)
    tag(cv, u, .05, "SPARK PLUG SOCKET", y=70)

def v_plug_gap(cv, u, t):
    plug(cv, CX - 40, 110, 1.55)
    ty = 110 + 330 * 1.55
    gx = kf(u, [(.15, 1050), (.5, CX + 20)])
    rrot(cv, gx + 160, ty + 12, 320, 14, 0, (230, 232, 240), (140, 146, 160), 2)
    arrow(cv, CX + 220, ty + 120, CX + 50, ty + 30, YELLOW, 10)
    tag(cv, u, .05, "CHECK THE GAP", y=80)
    tag(cv, u, .55, "MATCH YOUR MANUAL'S SPEC", y=850, size=34)

def v_plug_in(cv, u, t):
    cv.rr(100, 560, 980, 780, 40, fill=(54, 58, 76), outline=RIM, width=4)
    cv.ell(CX, 600, 90, ry=24, fill=(12, 12, 18), outline=STEEL, width=6)
    y = kf(u, [(.1, 120), (.55, 330)])
    rot = u * 12
    plug(cv, CX, y, .9, rot)
    if u > .6:
        a = .4 * math.sin((u - .6) * 20)
        cv.line([(CX, 200), (CX + 300 * math.cos(a), 200 + 300 * math.sin(a))], (210, 214, 224), 20)
    tick(cv, 850, 300, eob(seg(u, .85, .97)))
    tag(cv, u, .05, "FINGER-TIGHT FIRST", y=70) if u < .55 else tag(cv, u, .6, "THEN SNUG TO SPEC", y=70)

def v_plug_coilback(cv, u, t):
    engine_top(cv)
    for i, x in enumerate((220, 420, 620, 820)):
        k = eo(seg(u, .1 + i * .18, .3 + i * .18))
        coil(cv, x, 380 - (1 - k) * 220)
        if k > .95: tick(cv, x, 300, .45)
    tag(cv, u, .05, "REPEAT FOR EVERY CYLINDER", y=130, size=34)

# ------------------------------------------------------------------ battery
def battery(cv, x=330, y=400, w=420, h=280):
    cv.rr(x, y, x + w, y + h, 22, fill=(32, 34, 44), outline=(90, 94, 110), width=4)
    cv.rr(x + 24, y + 70, x + w - 24, y + h - 26, 10, fill=(46, 50, 68))
    cv.text(x + w / 2, y + h / 2 + 22, "12V", 70, (150, 156, 176))
    for px, col, sign in ((x + 80, (80, 84, 98), "-"), (x + w - 80, (230, 50, 60), "+")):
        cv.rr(px - 30, y - 34, px + 30, y, 6, fill=col, outline=(200, 205, 215), width=3)
        cv.text(px, y + 36, sign, 52, (255, 255, 255))

def clamp_cable(cv, px, py, col, lift=0.0, sd=1, show=True):
    if not show: return
    y = py - 46 - lift
    cv.line([(px, y), (px + sd * 40, y - 90), (px + sd * 140, y - 130)], col, 22)
    cv.rr(px - 38, y - 10, px + 38, y + 46, 8, fill=col, outline=(200, 205, 215), width=3)
    cv.ell(px, y + 18, 9, fill=(200, 205, 215))

def v_hook_batt(cv, u, t):
    battery(cv, 300, 330, 480, 320)
    blink = int(t * 3) % 2 == 0
    cv.rr(340, 345, 740, 390, 10, fill=(20, 20, 28))
    cv.rr(344, 349, 344 + (60 if blink else 20), 386, 8, fill=TTRED)
    cv.text(CX, 200, "CLICK CLICK", 110, (255, 255, 255), stroke=8)
    cv.text(CX, 760, "DEAD BATTERY?", 64, YELLOW, stroke=6)

def v_batt_safe(cv, u, t):
    s = eob(seg(u, .1, .35))
    for gx in (430, 650):
        cv.ell(gx, 330, 95 * s, ry=80 * s, fill=(*GLASS, 190), outline=(30, 30, 38), width=14)
    cv.line([(525, 330), (555, 330)], (30, 30, 38), 12); cv.line([(335, 330), (180, 300)], (30, 30, 38), 12); cv.line([(745, 330), (900, 300)], (30, 30, 38), 12)
    k = eob(seg(u, .4, .65))
    if k > .02:
        cv.ell(CX, 640, 90 * k, fill=(60, 64, 82), outline=STEEL, width=8)
        cv.rr(CX + 60 * k, 620, CX + 250 * k, 660, 10, fill=STEEL)
        cv.text(CX, 800, "ENGINE OFF, KEY OUT", 44, (255, 255, 255), stroke=6)

def v_batt_neg(cv, u, t):
    lift = eo(seg(u, .3, .7)) * 120
    battery(cv)
    cv.rr(520, 340, 620, 380, 8, fill=(200, 205, 215)) if False else None
    clamp_cable(cv, 410, 400, (24, 24, 30), lift, -1)
    clamp_cable(cv, 670, 400, (220, 40, 50), 0, 1)
    if u < .45:
        a = u * 14
        cv.line([(410 + 160 * math.cos(-.9 + .3 * math.sin(a)), 340 + 160 * math.sin(-.9 + .3 * math.sin(a))), (410, 354)], STEEL, 18)
    tag(cv, u, .05, "NEGATIVE (BLACK) FIRST", y=110, size=38)

def v_batt_pos(cv, u, t):
    lift = eo(seg(u, .3, .7)) * 120
    battery(cv)
    clamp_cable(cv, 410, 400, (24, 24, 30), 120, -1)
    clamp_cable(cv, 670, 400, (220, 40, 50), lift, 1)
    tag(cv, u, .05, "THEN POSITIVE (RED)", y=110, size=38)

def v_batt_lift(cv, u, t):
    off = kf(u, [(.35, 0), (.8, 260)])
    cv.rr(280, 700, 800, 740, 8, fill=DARK, outline=RIM, width=3)
    battery(cv, 330, 420 - off)
    hy = 380 - off * .0
    if u < .4:
        cv.rr(300, 380, 780, 410, 8, fill=STEEL); cv.rr(520, 350, 560, 410, 6, fill=(220, 225, 235))
    else:
        cv.rr(300, 380 - (u - .4) * 800 if u < .6 else 220, 780, 410 - (u - .4) * 800 if u < .6 else 250, 8, fill=STEEL)
    if u > .4: arrow(cv, 900, 560, 900, 330, YELLOW)
    tag(cv, u, .05, "REMOVE THE HOLD-DOWN", y=90, size=36) if u < .4 else tag(cv, u, .5, "HEAVY: LIFT WITH YOUR LEGS", y=90, size=34)

def v_batt_new(cv, u, t):
    cv.rr(280, 700, 800, 740, 8, fill=DARK, outline=RIM, width=3)
    for i in range(6): cv.line([(300 + i * 80, 690), (360 + i * 80, 650)], (230, 240, 240), 5) if u < .35 else None
    k = eo(seg(u, .4, .75))
    battery(cv, 330, 420 - (1 - k) * 300)
    if u < .35:
        a = u * 40
        cv.ell(540, 520, 60, fill=(120, 126, 142)); cv.line([(540 + 60 * math.cos(a), 520 + 60 * math.sin(a)), (540 - 60 * math.cos(a), 520 - 60 * math.sin(a))], STEEL, 8)
    s = eob(seg(u, .8, .95))
    if s > .02: cv.rr(300, 380, 780, 410, 8, fill=STEEL); tick(cv, 900, 280, s)
    tag(cv, u, .05, "SCRUB OFF THE CRUD", y=90) if u < .38 else tag(cv, u, .45, "STRAP IT DOWN", y=90)

def v_batt_back(cv, u, t):
    battery(cv)
    a = 1 - eo(seg(u, .1, .4)); b = 1 - eo(seg(u, .55, .85))
    clamp_cable(cv, 670, 400, (220, 40, 50), a * 120, 1)
    clamp_cable(cv, 410, 400, (24, 24, 30), b * 120, -1)
    cv.ell(670, 190, 40, fill=(220, 40, 50), outline=(255, 255, 255), width=5); cv.text(670, 190, "1", 50, (255, 255, 255))
    if u > .5: cv.ell(410, 190, 40, fill=(24, 24, 30), outline=(255, 255, 255), width=5); cv.text(410, 190, "2", 50, (255, 255, 255))
    tick(cv, 540, 800, eob(seg(u, .85, .97)))

# ------------------------------------------------------------------ wipers
PIV = (800, 770)

def windshield(cv):
    cv.poly([(140, 70), (940, 70), (1010, 730), (70, 730)], (*GLASS, 235), (30, 30, 38), 14)
    cv.poly([(140, 70), (330, 70), (210, 730), (70, 730)], (255, 255, 255, 45))
    cv.rr(40, 735, 1040, 880, 30, fill=(30, 32, 44))

def wiper(cv, lift=0.0, slide=0.0, newblade=False, tabhl=False, blade=True):
    th = math.pi + .1 + lift * .75
    ca, sa = math.cos(th), math.sin(th)
    bx, by = PIV[0] + 470 * ca, PIV[1] + 470 * sa
    cv.line([PIV, (bx, by)], (40, 42, 54), 14)
    cv.ell(PIV[0], PIV[1], 22, fill=(70, 72, 90), outline=STEEL, width=4)
    if blade:
        ox, oy = slide * ca, slide * sa
        rrot(cv, bx + ox, by + oy, 480, 22, th, (14, 14, 20), STEEL, 3)
    cv.ell(bx, by, 16, fill=TTRED if tabhl else (90, 94, 110))
    return bx, by, th

def v_hook_wiper(cv, u, t):
    windshield(cv)
    for i in range(5):
        cv.line([(200 + i * 150, 600 - 40 * i), (330 + i * 150, 420 - 30 * i)], (255, 255, 255, 110), 10)
    wiper(cv, lift=0.0)
    cv.emoji(540, 330, "😵", 200)

def v_wipe1(cv, u, t):
    windshield(cv); k = eo(seg(u, .15, .55))
    wiper(cv, lift=k)
    if k > .5: arrow(cv, 300, 640, 300, 420, YELLOW)
    tag(cv, u, .05, "LIFT THE ARM OFF THE GLASS", y=150, size=34)

def v_wipe2(cv, u, t):
    windshield(cv)
    bx, by, th = wiper(cv, lift=.8, tabhl=True)
    r = 50 + 12 * math.sin(t * 8)
    cv.ell(bx, by, r, outline=YELLOW, width=8)
    arrow(cv, bx - 220, by - 120, bx - 40, by - 20, YELLOW, 10)
    tag(cv, u, .1, "FIND THE TAB", y=150)

def v_wipe3(cv, u, t):
    windshield(cv)
    sl = eo(seg(u, .35, .85)) * 520
    bx, by, th = wiper(cv, lift=.8, slide=-sl, tabhl=True)
    tag(cv, u, .05, "PRESS THE TAB, SLIDE IT OFF", y=150, size=34)

def v_wipe4(cv, u, t):
    windshield(cv)
    sl = (1 - eo(seg(u, .1, .6))) * 520
    wiper(cv, lift=.8, slide=-sl)
    tick(cv, 820, 280, eob(seg(u, .65, .85)))
    tag(cv, u, .6, "CLICK!", y=150, size=60)

def v_wipe5(cv, u, t):
    windshield(cv)
    lift = 1 - eo(seg(u, .05, .35))
    ph = (u - .35) / .65
    sweep = (.9 * (0.5 - 0.5 * math.cos(ph * 2 * math.pi * 2))) if ph > 0 else 0
    wiper(cv, lift=lift + sweep * .0, blade=True)
    if ph > 0:
        for i in range(10): cv.ell(300 + (i * 97) % 500, 250 + (i * 53) % 350, 7, fill=(210, 235, 255))
    tag(cv, u, .4, "TEST WITH WASHER FLUID", y=150, size=34)
