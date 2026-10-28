#!/usr/bin/env python3
"""Renders a 9:16 TikTok-style video: how to change car brake pads.

Usage:  make_tiktok.py [preview|full]
Needs:  numpy, Pillow, soundfile, kokoro-onnx, ffmpeg, and the Kokoro model files
        (kokoro-v1.0.int8.onnx + voices-v1.0.bin) in $KOKORO_DIR (default: ./build/models).
Voice, music and sound effects are all generated locally, so the audio is royalty-free.
"""
import os, sys, re, math, hashlib, subprocess
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)
MODEL_DIR = os.environ.get("KOKORO_DIR", os.path.join(BUILD, "models"))
OUT = os.path.join(HERE, "brakes_tiktok.mp4")

W, H, FPS = 1080, 1920, 30
VSR, SR = 24000, 44100
BEAT = 0.5  # 120 BPM
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

YELLOW, PINK, CYAN, LIME, ORANGE, PURPLE = (255, 226, 0), (255, 60, 150), (0, 235, 255), (182, 255, 0), (255, 140, 0), (175, 100, 255)
TTRED = (254, 44, 85)

# ----------------------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eob(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

_fonts = {}
def F(sz):
    sz = max(4, int(sz))
    if sz not in _fonts: _fonts[sz] = ImageFont.truetype(BOLD, sz)
    return _fonts[sz]

_emo = {}
def emoji(ch, size):
    k = (ch, int(size))
    if k not in _emo:
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), ch, font=ImageFont.truetype(EMOJI_FONT, 109), embedded_color=True)
        im = im.crop(im.getbbox())
        r = size / max(im.size)
        _emo[k] = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    return _emo[k]

class Cv:
    """RGBA canvas drawn at 2x and reduced for clean anti-aliased vector shapes."""
    def __init__(s, w, h, S=2):
        s.S, s.w, s.h = S, w, h
        s.im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def ell(s, cx, cy, rx, ry=None, fill=None, outline=None, width=0):
        ry = rx if ry is None else ry; S = s.S
        s.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill, outline=outline, width=int(width * S))
    def rr(s, x0, y0, x1, y1, r=0, fill=None, outline=None, width=0):
        S = s.S
        s.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], r * S, fill=fill, outline=outline, width=int(width * S))
    def poly(s, pts, fill=None, outline=None, width=0):
        S = s.S; p = [(x * S, y * S) for x, y in pts]
        s.d.polygon(p, fill=fill)
        if outline: s.d.line(p + [p[0]], fill=outline, width=int(width * S), joint="curve")
    def line(s, pts, fill, width):
        S = s.S; s.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(width * S), joint="curve")
        for x, y in (pts[0], pts[-1]): s.ell(x, y, width / 2, fill=fill)
    def text(s, x, y, txt, size, fill, stroke=0, sfill=(10, 6, 24)):
        S = s.S
        s.d.text((x * S, y * S), txt, font=F(size * S), fill=fill, anchor="mm", stroke_width=int(stroke * S), stroke_fill=sfill)
    def emoji(s, x, y, ch, size):
        e = emoji(ch, size * s.S)
        s.im.alpha_composite(e, (int(x * s.S - e.width / 2), int(y * s.S - e.height / 2)))
    def out(s): return s.im.reduce(s.S)

def arrow(cv, x0, y0, x1, y1, col, w=14):
    a = math.atan2(y1 - y0, x1 - x0); hl = w * 2.6
    bx, by = x1 - hl * 0.8 * math.cos(a), y1 - hl * 0.8 * math.sin(a)
    cv.line([(x0, y0), (bx, by)], col, w)
    cv.poly([(x1, y1), (x1 - hl * math.cos(a - .45), y1 - hl * math.sin(a - .45)), (x1 - hl * math.cos(a + .45), y1 - hl * math.sin(a + .45))], col)

def star(cv, x, y, r, col):
    pts = []
    for i in range(8):
        rr_ = r if i % 2 == 0 else r * .25; a = i * math.pi / 4 - math.pi / 2
        pts.append((x + rr_ * math.cos(a), y + rr_ * math.sin(a)))
    cv.poly(pts, col)

def bolt(cv, x, y, r, rot):
    cv.poly([(x + r * math.cos(rot + i * math.pi / 3), y + r * math.sin(rot + i * math.pi / 3)) for i in range(6)], (205, 210, 220), (120, 125, 138), 3)
    cv.ell(x, y, r * .42, fill=(120, 125, 138))

# ----------------------------------------------------------------------------- brake drawings
def wheel(cv, cx, cy, R, rot=0.0, nut=YELLOW):
    cv.ell(cx, cy, R, fill=(22, 22, 26), outline=(78, 80, 92), width=5)
    cv.ell(cx, cy, R * .84, outline=(44, 46, 56), width=4)
    cv.ell(cx, cy, R * .70, fill=(208, 213, 223))
    cv.ell(cx, cy, R * .64, fill=(30, 32, 40))
    for i in range(5):
        a = rot + i * 2 * math.pi / 5; nx, ny = -math.sin(a), math.cos(a)
        r0, r1, w0, w1 = R * .1, R * .64, R * .075, R * .12
        p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a)); p1 = (cx + r1 * math.cos(a), cy + r1 * math.sin(a))
        cv.poly([(p0[0] + nx * w0, p0[1] + ny * w0), (p1[0] + nx * w1, p1[1] + ny * w1), (p1[0] - nx * w1, p1[1] - ny * w1), (p0[0] - nx * w0, p0[1] - ny * w0)], (190, 196, 210))
    cv.ell(cx, cy, R * .2, fill=(222, 227, 236), outline=(150, 156, 170), width=3)
    for i in range(5):
        a = rot + i * 2 * math.pi / 5 + math.pi / 5
        cv.ell(cx + R * .12 * math.cos(a), cy + R * .12 * math.sin(a), R * .035, fill=nut)

def rotor(cv, cx, cy, R, rot=0.0):
    cv.ell(cx, cy, R, fill=(130, 136, 150), outline=(215, 220, 232), width=4)
    cv.ell(cx, cy, R * .93, outline=(98, 103, 117), width=3)
    cv.ell(cx, cy, R * .62, fill=(112, 118, 132), outline=(86, 90, 104), width=3)
    for i in range(14):
        a = rot + i * 2 * math.pi / 14
        cv.ell(cx + R * .78 * math.cos(a), cy + R * .78 * math.sin(a), R * .045, fill=(48, 52, 64))
    cv.ell(cx, cy, R * .40, fill=(88, 92, 106))
    for i in range(5):
        a = rot + i * 2 * math.pi / 5
        cv.ell(cx + R * .27 * math.cos(a), cy + R * .27 * math.sin(a), R * .045, fill=(40, 42, 52))
    cv.ell(cx, cy, R * .12, fill=(36, 38, 46))

def caliper(cv, cx, cy, R, ox=0, oy=0):
    x0, x1, y0, y1 = cx + R * .40 + ox, cx + R * 1.0 + ox, cy - R * .62 + oy, cy + R * .62 + oy
    cv.rr(x0, y0, x1, y1, 34, fill=(228, 40, 62), outline=(255, 130, 140), width=4)
    cv.rr(x0 + 18, y0 + 18, x0 + 44, y1 - 18, 12, fill=(255, 110, 120))
    cv.text((x0 + x1) / 2 + 8, cy + oy, "BRAKE", 34, (255, 235, 238))

# ----------------------------------------------------------------------------- scene visuals (canvas 1080x900)
CX, CY = 540, 450

def v_hook(cv, u, t):
    cv.text(CX, 200, "$400", 330, (255, 255, 255), stroke=10)
    cv.text(CX, 380, "TYPICAL SHOP QUOTE", 44, (205, 210, 232))
    p = eo(seg(u, .22, .36))
    if p > 0:
        cv.line([(160, 330), (160 + p * 760, 330 - p * 220)], TTRED, 26)
    s = eob(seg(u, .40, .55))
    if s > .02:
        cv.text(CX, 640, "$60", 330 * s, LIME, stroke=10)
        cv.text(CX, 820, "PADS COST ABOUT THAT", 44 * s, (205, 210, 232))
        for i, (dx, dy) in enumerate([(-330, -120), (320, -150), (350, 90), (-300, 120)]):
            star(cv, CX + dx, 640 + dy, 26 * s * (0.8 + 0.2 * math.sin(t * 9 + i)), YELLOW)
    cv.emoji(150 + 10 * math.sin(t * 4), 70, "💸", 110)
    cv.emoji(930, 70 + 10 * math.sin(t * 4 + 1), "🔧", 110)

def v_lift(cv, u, t):
    lift = eo(seg(u, .42, .62)) * 50
    gy, R = 800, 280
    cv.line([(30, gy), (1050, gy)], (130, 136, 160), 8)
    cv.rr(40, 120 - lift, 1040, 470 - lift, 60, fill=(66, 72, 108), outline=(110, 118, 160), width=4)
    cv.ell(CX, gy - R - lift, R + 26, fill=(26, 20, 52))
    wheel(cv, CX, gy - R - lift, R, rot=-eo(seg(u, .05, .35)) * 0.5)
    if u < .4:
        cv.rr(340, 40, 740, 120, 40, fill=(255, 255, 255))
        cv.text(CX, 80, "LOOSEN 1/2 TURN", 38, (20, 12, 40))
    st = eob(seg(u, .55, .72))
    if st > .02:
        top = 470 - lift + 20
        k = st
        cv.poly([(120 - 90 * k, gy), (120 + 90 * k, gy), (120 + 22, gy - 40 * k), (120 - 22, gy - 40 * k)], ORANGE)
        cv.rr(120 - 20, top + (gy - top) * (1 - k), 120 + 20, gy - 40 * k, 6, fill=(255, 170, 60))
        cv.rr(120 - 55, top + (gy - top) * (1 - k) - 14, 120 + 55, top + (gy - top) * (1 - k) + 6, 8, fill=(255, 200, 90))

def v_wheeloff(cv, u, t):
    rotor(cv, CX, CY, 300, rot=t * 1.6); caliper(cv, CX, CY, 300)
    off = eo(seg(u, .08, .6)) * 900
    if off < 880:
        wheel(cv, CX + off, CY + 40 * seg(u, .08, .6) ** 2, 300, rot=off / 300)
    s = eob(seg(u, .55, .75))
    if s > .3:
        cv.rr(250, 70, 830, 150, 40, fill=(255, 255, 255))
        cv.text(CX, 110, "ROTOR + CALIPER", 40 * s, (20, 12, 40))

def v_caliper(cv, u, t):
    rotor(cv, CX, CY + 40, 300, rot=t * 0.6)
    bo = eo(seg(u, .10, .36)) * 120
    co = eo(seg(u, .42, .78))
    ox, oy = co * 150, co * 230
    bx = CX + 300 * .72 + ox
    if co > 0:
        pts = [(bx + 60, CY + 40 - 300 * .62 + oy), (bx + 90, 200), (780, 90), (780, 40)]
        cv.line(pts, ORANGE, 9)
        cv.ell(780, 40, 18, outline=ORANGE, width=8)
    caliper(cv, CX, CY + 40, 300, ox, oy)
    if co == 0:
        for sy in (-.45, .45):
            bolt(cv, CX + 300 * .72 + bo, CY + 40 + 300 * sy, 24, bo * .12)
    else:
        for sy in (-.45, .45):
            bolt(cv, CX + 300 * .72 + 120 + 40 * co, CY + 40 + 300 * sy + 120 * co, 24, 14)

def edge_rotor(cv, wear_left=0):
    cv.rr(505, 160, 575, 840, 8, fill=(150, 156, 170), outline=(220, 225, 236), width=4)
    for y in range(200, 820, 36): cv.line([(512, y), (568, y)], (110, 116, 130), 3)

def pad(cv, x_face, y0, y1, side, thick):
    """side=-1: pad left of the rotor (friction on its right). side=+1: right of rotor."""
    if side < 0:
        cv.rr(x_face - thick - 28, y0, x_face - thick, y1, 6, fill=(170, 176, 190))
        cv.rr(x_face - thick, y0 + 6, x_face, y1 - 6, 6, fill=(120, 74, 40))
    else:
        cv.rr(x_face + thick, y0, x_face + thick + 28, y1, 6, fill=(170, 176, 190))
        cv.rr(x_face, y0 + 6, x_face + thick, y1 - 6, 6, fill=(120, 74, 40))

def v_pads(cv, u, t):
    edge_rotor(cv)
    off = eo(seg(u, .22, .72)) * 330
    pad(cv, 500 - off, 210, 560, -1, 14); pad(cv, 580 + off, 210, 560, +1, 14)
    if off > 20:
        arrow(cv, 330, 385, 150, 385, YELLOW); arrow(cv, 750, 385, 930, 385, YELLOW)
    s = eob(seg(u, .5, .7))
    if s > .02:
        if s > .3:
            cv.rr(280, 610, 800, 670, 30, fill=(255, 255, 255))
            cv.text(CX, 640, "WORN OUT = THIN", 38, (20, 12, 40))

def v_piston(cv, u, t):
    p = eo(seg(u, .12, .85))
    xf = 540 + p * 100
    cv.rr(600, 280, 900, 720, 30, fill=(228, 40, 62), outline=(255, 130, 140), width=4)
    cv.rr(600, 360, 790, 640, 8, fill=(18, 16, 26))
    cv.rr(xf, 380, 790, 620, 8, fill=(196, 202, 214), outline=(120, 126, 140), width=3)
    for i in range(3): cv.line([(xf + 22 + i * 26, 392), (xf + 22 + i * 26, 608)], (140, 146, 160), 3)
    cv.rr(xf - 36, 350, xf, 650, 6, fill=(120, 74, 40))
    cv.rr(150, 230, 975, 268, 10, fill=(170, 176, 190)); cv.rr(150, 230, 192, 720, 10, fill=(170, 176, 190)); cv.rr(905, 230, 945, 720, 10, fill=(170, 176, 190))
    cv.rr(112, 480, xf - 36, 520, 6, fill=(220, 225, 236))
    a = p * 16
    hl = 120 * abs(math.cos(a))
    cv.line([(100, 500 - hl), (100, 500 + hl)], (255, 255, 255), 16)
    cv.ell(100, 500 - hl, 14, fill=YELLOW); cv.ell(100, 500 + hl, 14, fill=YELLOW)
    cv.text(CX, 810, "SQUEEZE SLOWLY", 52, (255, 255, 255), stroke=6)

def v_install(cv, u, t):
    edge_rotor(cv)
    e1 = eo(seg(u, .06, .34)); e2 = eo(seg(u, .36, .62)); e3 = eo(seg(u, .64, .8))
    off = (1 - e1) * 330
    pad(cv, 500 - off, 190, 520, -1, 46); pad(cv, 580 + off, 190, 520, +1, 46)
    if e2 > 0:
        oy = -(1 - e2) * 420
        cv.rr(402, 120 + oy, 678, 190 + oy, 18, fill=(228, 40, 62), outline=(255, 130, 140), width=4)
        cv.rr(402, 120 + oy, 452, 560 + oy, 18, fill=(228, 40, 62), outline=(255, 130, 140), width=4)
        cv.rr(628, 120 + oy, 678, 560 + oy, 18, fill=(228, 40, 62), outline=(255, 130, 140), width=4)
    if e3 > 0:
        for bx in (500, 580):
            cv.rr(bx - 14, 40 - (1 - e3) * 200, bx + 14, 130 - (1 - e3) * 200 + 20, 6, fill=(215, 220, 230))
    s = eob(seg(u, .82, .95))
    if s > .02:
        cv.ell(CX, 700, 70 * s, fill=(40, 210, 110), outline=(255, 255, 255), width=6)
        cv.line([(CX - 30 * s, 700), (CX - 6 * s, 700 + 26 * s), (CX + 36 * s, 700 - 28 * s)], (255, 255, 255), 14 * s)
        cv.text(CX, 810, "TORQUE TO SPEC", 50 * s, (255, 255, 255), stroke=6)

def v_finish(cv, u, t):
    spin = eo(seg(u, .05, .35)) * (u * 22 + 4)
    wheel(cv, CX, 330, 235, rot=spin * 3)
    if u > .15:
        for i, y in enumerate((230, 330, 430)):
            x = 200 - (t * 600 + i * 70) % 80
            cv.line([(x - 120, y), (x, y)], (255, 255, 255, 120), 8)
    press = 0.5 - 0.5 * math.cos(2 * math.pi * 1.5 * max(0, t - 1.3)) if u > .35 else 0
    py = 700 + press * 46
    cv.line([(CX + 90, py), (CX + 150, 600)], (120, 126, 142), 18)
    cv.rr(CX - 160, py, CX + 160, py + 90, 24, fill=(54, 56, 70), outline=(150, 156, 172), width=4)
    for i in range(6): cv.line([(CX - 130 + i * 52, py + 18), (CX - 130 + i * 52, py + 72)], LIME, 7)
    cv.text(CX, 850, "PUMP UNTIL FIRM", 48, (255, 255, 255), stroke=6)

def v_cta(cv, u, t):
    k = 1 + 0.06 * math.sin(t * 8)
    cv.rr(CX - 330 * k, 150 - 90 * k, CX + 330 * k, 150 + 90 * k, 90, fill=TTRED, outline=(255, 255, 255), width=8)
    cv.text(CX, 150, "FOLLOW  +", 100 * k, (255, 255, 255))
    cv.text(CX, 330, "SAVE THIS FOR LATER", 54, (255, 255, 255), stroke=6)
    for i in range(7):
        y = 760 - (t * 140 + i * 110) % 330
        cv.emoji(150 + i * 130 + 20 * math.sin(t * 3 + i), y, ["❤️", "🔔", "🔧", "🚗"][i % 4], 96)
    cv.text(CX, 790, "ALWAYS USE JACK STANDS", 34, (255, 255, 255, 220))
    cv.text(CX, 835, "& CHECK YOUR MANUAL FOR TORQUE SPECS", 34, (255, 255, 255, 220))

SCENES = [
 dict(badge="7 EASY STEPS", title=["STOP OVERPAYING", "FOR BRAKES"], acc=YELLOW, vis=v_hook, say=[
    "Stop paying a mechanic four hundred dollars.",
    "You can change your brakes in seven steps."]),
 dict(badge="STEP 1 / 7", title=["LOOSEN", "& LIFT"], acc=PINK, vis=v_lift, say=[
    "Step one. Loosen the lug nuts, then jack the car up.",
    "And always use jack stands."], sticker=("USE JACK STANDS", "⚠", 1)),
 dict(badge="STEP 2 / 7", title=["WHEEL", "OFF"], acc=CYAN, vis=v_wheeloff, say=[
    "Step two. Pull the wheel off.",
    "Now you can see the rotor and caliper."]),
 dict(badge="STEP 3 / 7", title=["UNBOLT THE", "CALIPER"], acc=LIME, vis=v_caliper, say=[
    "Step three. Remove the two caliper bolts and slide it off.",
    "Hang it up. Never let it dangle by the brake hose."], sticker=("NEVER BY THE HOSE", "❌", 1)),
 dict(badge="STEP 4 / 7", title=["OLD PADS", "OUT"], acc=ORANGE, vis=v_pads, say=[
    "Step four. Slide the old pads out.",
    "If the rotor is grooved, replace it too."]),
 dict(badge="STEP 5 / 7", title=["PUSH THE", "PISTON IN"], acc=PURPLE, vis=v_piston, say=[
    "Step five. Squeeze the piston back with a C clamp, nice and slow."]),
 dict(badge="STEP 6 / 7", title=["NEW PADS", "GO IN"], acc=YELLOW, vis=v_install, say=[
    "Step six. New pads in, caliper back on, bolts torqued to spec."]),
 dict(badge="STEP 7 / 7", title=["WHEEL ON", "& TEST"], acc=LIME, vis=v_finish, say=[
    "Step seven. Wheel back on, then pump the pedal until it feels firm.",
    "Bed them in with a few easy stops."]),
 dict(badge="DONE!", title=["FOLLOW FOR", "MORE CAR HACKS"], acc=PINK, vis=v_cta, say=[
    "That's it! Follow for more car hacks.",
    "Save this for your next brake job."]),
]

# ----------------------------------------------------------------------------- voice + timeline
_kokoro = None
def voice(text):
    import soundfile as sf
    p = os.path.join(BUILD, "v_" + hashlib.md5(text.encode()).hexdigest()[:12] + ".wav")
    if not os.path.exists(p):
        global _kokoro
        if _kokoro is None:
            from kokoro_onnx import Kokoro
            _kokoro = Kokoro(os.path.join(MODEL_DIR, "kokoro-v1.0.int8.onnx"), os.path.join(MODEL_DIR, "voices-v1.0.bin"))
        s, sr = _kokoro.create(text, voice="af_heart", speed=1.18, lang="en-us")
        assert sr == VSR
        sf.write(p, s, sr)
    s, _ = sf.read(p, dtype="float32")
    idx = np.where(np.abs(s) > 0.012)[0]
    return s[max(0, idx[0] - 200): idx[-1] + 400] if len(idx) else s

def syl(w):
    w = re.sub(r"[^a-z]", "", w.lower()); n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and n > 1 and not w.endswith("le"): n -= 1
    return max(1, n)

def chunks(words):
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and (len(cur) >= 3 or sum(len(words[x]) for x in cur) + len(w) > 12):
            out.append(cur); cur = []
        cur.append(i)
        if re.search(r"[.,?!]$", w): out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def build_timeline():
    t = 0.0; tl = []
    for si, sc in enumerate(SCENES):
        start = t; cur = start + (0.08 if si == 0 else 0.28); sents = []
        for s in sc["say"]:
            wav = voice(s); dur = len(wav) / VSR
            words = s.split()
            wt = [syl(w) + 0.4 + (0.7 if re.search(r"[.,?!]$", w) else 0) for w in words]
            cum = np.concatenate([[0], np.cumsum(wt)]) / sum(wt)
            ws = [(cur + cum[i] * dur, cur + cum[i + 1] * dur) for i in range(len(words))]
            sents.append(dict(text=s, start=cur, dur=dur, wav=wav, words=[w.upper() for w in words], wtimes=ws, chunks=chunks(words)))
            cur += dur + 0.14
        end = cur + 0.12
        tl.append(dict(sc, i=si, start=start, end=end, dur=end - start, sents=sents))
        t = end
    return tl, t

# ----------------------------------------------------------------------------- audio
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))

def resample(x, sr_in, sr_out):
    X = np.fft.rfft(x); m = int(round(len(x) * sr_out / sr_in))
    Y = np.zeros(m // 2 + 1, dtype=complex); k = min(len(X), len(Y)); Y[:k] = X[:k]
    return (np.fft.irfft(Y, m) * m / len(x)).astype(np.float32)

def make_audio(tl, total):
    n = int((total + 0.6) * SR); rng = np.random.default_rng(7)
    L = np.zeros(n, np.float32); R = np.zeros(n, np.float32)
    BPm = np.zeros(n, np.float32)  # bass + pad (pumped)
    def add(arr, t0, gl=1.0, gr=1.0, buf=None):
        i = int(t0 * SR)
        if i >= n: return
        j = min(n, i + len(arr)); a = arr[:j - i]
        if buf is not None: buf[i:j] += a
        else: L[i:j] += a * gl; R[i:j] += a * gr
    tk = np.arange(int(.4 * SR)) / SR
    kick = np.sin(2 * np.pi * (45 * tk + 4 * (1 - np.exp(-30 * tk)))) * np.exp(-tk / .14) * np.minimum(1, tk * 800) * .95
    tc = np.arange(int(.25 * SR)) / SR
    clap = bp(rng.standard_normal(len(tc)), 900, 6000) * (np.exp(-tc / .05) + .8 * np.exp(-np.clip(tc - .012, 0, None) / .05) * (tc > .012)) * .35
    th = np.arange(int(.06 * SR)) / SR
    hat = bp(rng.standard_normal(len(th)), 7000, 16000) * np.exp(-th / .012) * .16
    chords = [(110.0, [440, 523.25, 659.25]), (87.31, [349.23, 440, 523.25]), (130.81, [523.25, 659.25, 783.99]), (98.0, [392, 493.88, 587.33])]
    ta = np.arange(int(.3 * SR)) / SR
    tb = np.arange(int(.24 * SR)) / SR
    for b in range(int(total / BEAT) + 4):
        t0 = b * BEAT; add(kick, t0, buf=None)
        if b % 2 == 1: add(clap, t0)
        add(hat, t0 + BEAT / 2, .8, 1.0); add(hat * .45, t0 + BEAT / 4, 1.0, .7); add(hat * .45, t0 + 3 * BEAT / 4, .7, 1.0)
    pat = [0, 1, 2, 1, 0, 2, 1, 2]
    for bar in range(int(total / (4 * BEAT)) + 2):
        root, tones = chords[bar % 4]; tb0 = bar * 4 * BEAT
        for k in [0, 3, 6, 8, 11, 14]:
            bass = (np.sin(2 * np.pi * root * tb) + .5 * np.sin(4 * np.pi * root * tb) + .25 * np.sin(6 * np.pi * root * tb)) * np.exp(-tb / .13) * np.minimum(1, tb * 400) * .55
            add(bass, tb0 + k * BEAT / 4, buf=BPm)
        padlen = np.arange(int(4 * BEAT * SR)) / SR
        padw = sum(np.sin(2 * np.pi * f * .5 * padlen) for f in tones) / 3 * np.minimum(1, padlen * 8) * np.minimum(1, (4 * BEAT - padlen) * 8) * .10
        add(padw, tb0, buf=BPm)
        for k in range(16):
            f = tones[pat[k % 8]]
            pl = (np.sin(2 * np.pi * f * ta) + .3 * np.sin(4 * np.pi * f * ta)) * np.exp(-ta / .09) * np.minimum(1, ta * 600) * .13
            add(pl, tb0 + k * BEAT / 4, 1.0, .55); add(pl * .4, tb0 + k * BEAT / 4 + .375, .25, .6)
    tg = np.arange(n) / SR
    pump = 1 - .55 * np.exp(-(tg % BEAT) / .12)
    L += BPm * pump; R += BPm * pump
    music = np.stack([L, R], 1)
    # voice track
    v = np.zeros(n, np.float32)
    for sc in tl:
        for s in sc["sents"]:
            w = resample(s["wav"], VSR, SR); w = w / max(1e-6, np.abs(w).max()) * .85
            i = int(s["start"] * SR); v[i:i + len(w)] += w[:n - i]
    # sidechain duck
    hop = int(SR * .01); m = len(v) // hop
    e = np.sqrt((v[:m * hop].reshape(m, hop) ** 2).mean(1)); gate = (e > .02).astype(np.float32)
    d = np.zeros(m, np.float32); cur = 0.0
    for i in range(m):
        cur += (gate[i] - cur) * (.5 if gate[i] > cur else .05); d[i] = cur
    duck = np.interp(np.arange(len(v)) / hop, np.arange(m) + .5, d).astype(np.float32)
    music *= (1 - .6 * duck)[:, None] * .75
    # sfx
    sfx = np.zeros((n, 2), np.float32)
    def sadd(arr, t0, g=1.0):
        i = int(t0 * SR); j = min(n, i + len(arr))
        if i < n: sfx[i:j] += (arr[:j - i] * g)[:, None]
    tw = np.arange(int(.5 * SR)) / SR
    whoosh = bp(rng.standard_normal(len(tw)), 400, 7000) * np.sin(np.pi * np.clip(tw / .5, 0, 1) ** .7) * .28
    tp = np.arange(int(.15 * SR)) / SR
    pop = np.sin(2 * np.pi * (500 * tp + 1500 * tp ** 2)) * np.exp(-tp / .05) * .35
    td = np.arange(int(.8 * SR)) / SR
    ding = (np.sin(2 * np.pi * 1318.5 * td) + .5 * np.sin(2 * np.pi * 1975 * td)) * np.exp(-td / .25) * .22
    tbm = np.arange(int(.9 * SR)) / SR
    boom = (np.sin(2 * np.pi * 55 * tbm) * np.exp(-tbm / .35) + bp(rng.standard_normal(len(tbm)), 60, 600) * np.exp(-tbm / .08)) * .6
    sadd(boom, 0)
    for sc in tl:
        if sc["i"] > 0: sadd(whoosh, sc["start"] - .12)
        if "sticker" in sc: sadd(pop, sc["sents"][sc["sticker"][2]]["start"])
    if not NO_DING: sadd(ding, tl[-1]["sents"][0]["start"] + .9)
    global STEMS
    STEMS = dict(music=music, voice=v, sfx=sfx)
    mix = music + np.stack([v, v], 1) + sfx
    mix = np.tanh(mix * 1.15) / np.tanh(1.15)
    mix = mix / np.abs(mix).max() * .89
    import soundfile as sf
    p = os.path.join(BUILD, "mix.wav"); sf.write(p, mix, SR, subtype="PCM_16")
    return p

# ----------------------------------------------------------------------------- frame rendering
BW, BH = 540, 960
YY, XX = np.mgrid[0:BH, 0:BW].astype(np.float32)
_top, _bot = np.array([14, 10, 36], np.float32), np.array([46, 14, 74], np.float32)
BASE = _top + (_bot - _top) * (YY[..., None] / BH)
VIG = np.clip(1 - .5 * (((XX - BW / 2) / (BW / 2)) ** 2 + ((YY - BH / 2) / (BH / 2)) ** 2) / 2, 0, 1)[..., None]
GLOW = np.exp(-((XX - 270) ** 2 + (YY - 460) ** 2) / (2 * 190 ** 2))[..., None]

def background(t, acc):
    stripes = ((((XX + YY * .6) - t * 45) % 80) < 40).astype(np.float32)[..., None] * 5
    pulse = .25 + .15 * (1 - (t % BEAT) / BEAT) ** 2
    img = (BASE + stripes + GLOW * np.array(acc, np.float32) * pulse) * VIG
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)

def make_title(lines, acc):
    size = 108
    while max(F(size).getlength(l) for l in lines) > 940: size -= 4
    lh = int(size * 1.06)
    im = Image.new("RGBA", (1040, lh * len(lines) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        y = 20 + lh * i + lh // 2
        d.text((525, y + 7), l, font=F(size), fill=(0, 0, 0, 150), anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0, 150))
        d.text((520, y), l, font=F(size), fill=(255, 255, 255) if i == 0 else acc, anchor="mm", stroke_width=8, stroke_fill=(12, 6, 28))
    return im

def make_sticker(text, emo):
    f = F(52); tw = int(f.getlength(text)); w = tw + 190
    im = Image.new("RGBA", (w + 20, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 10, w + 10, 140], 32, fill=(255, 255, 255))
    d.rounded_rectangle([20, 20, w, 130], 26, fill=(255, 226, 0))
    d.text((120 + tw / 2 + 10, 76), text, font=f, fill=(20, 12, 40), anchor="mm")
    im.alpha_composite(emoji(emo, 80), (36, 36))
    return im

def pasteC(img, im, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

def caption_state(sc, t):
    prev = None
    for s in sc["sents"]:
        if t >= s["start"]:
            prev = s
    if prev is None: return None
    ws = prev["wtimes"]
    ai = max([i for i in range(len(ws)) if t >= ws[i][0]] or [0])
    for ch in prev["chunks"]:
        if ai in ch: return [prev["words"][i] for i in ch], ch.index(ai), ws[ch[0]][0]

def caption_img(words, act, acc):
    f = F(94); sp = 26; widths = [f.getlength(w) for w in words]
    lines, cur, cw = [], [], 0
    for i, w in enumerate(widths):
        if cur and cw + sp + w > 900: lines.append(cur); cur, cw = [], 0
        cur.append(i); cw += (sp if len(cur) > 1 else 0) + w
    lines.append(cur)
    lh = 124; im = Image.new("RGBA", (1000, lh * len(lines) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, ln in enumerate(lines):
        tw = sum(widths[i] for i in ln) + sp * (len(ln) - 1); x = 500 - tw / 2; y = 10 + lh * li + lh / 2
        for i in ln:
            if i == act:
                d.rounded_rectangle([x - 16, y - 66, x + widths[i] + 16, y + 58], 30, fill=acc)
                d.text((x + widths[i] / 2, y), words[i], font=f, fill=(15, 8, 30), anchor="mm")
            else:
                d.text((x + widths[i] / 2, y), words[i], font=f, fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=(10, 6, 24))
            x += widths[i] + sp
    return im

TL = None; TITLES = {}; STICKERS = {}; NSTEPS = 1; STEMS = {}; NO_DING = False
def scene_at(t):
    for sc in TL:
        if t < sc["end"]: return sc
    return TL[-1]

def render_frame(fi):
    t = fi / FPS; sc = scene_at(t); ti = t - sc["start"]; u = clamp(ti / sc["dur"]); acc = sc["acc"]
    img = background(t, acc)
    first = sc["i"] == 0
    # visual
    cv = Cv(1080, 900); sc["vis"](cv, u, ti); vis = cv.out()
    punch = 1 + .03 * (1 - (t % BEAT) / BEAT) ** 3
    intro = 1.0 if first else .55 + .45 * eob(ti / .38)
    pasteC(img, vis, 540, 920, punch * intro, 1.0 if first else clamp(ti / .12))
    # step tracker + badge
    d = ImageDraw.Draw(img)
    bw = int(F(40).getlength(sc["badge"])) + 70
    d.rounded_rectangle([540 - bw / 2, 140, 540 + bw / 2, 204], 32, fill=acc)
    d.text((540, 172), sc["badge"], font=F(40), fill=(15, 8, 30), anchor="mm")
    n = NSTEPS; sw = 616 / n; stp = sc.get("step"); last = sc["i"] == len(TL) - 1
    for k in range(n):
        a0 = 540 - 308 + k * sw + 3; a1 = a0 + sw - 6
        if last or (stp and k < stp - 1): d.rounded_rectangle([a0, 226, a1, 236], 5, fill=acc)
        elif stp and k == stp - 1:
            d.rounded_rectangle([a0, 226, a1, 236], 5, fill=(90, 80, 130))
            d.rounded_rectangle([a0, 226, a0 + (a1 - a0) * u, 236], 5, fill=acc)
        else: d.rounded_rectangle([a0, 226, a1, 236], 5, fill=(90, 80, 130))
    # title
    s = eob(ti / .42) if not first else 1.0
    shake = (6 * math.sin(ti * 70) * (1 - ti / .5) if first and ti < .5 else 0)
    pasteC(img, TITLES[sc["i"]], 540 + shake, 360, .6 + .4 * s if not first else 1.0, clamp(ti / .1) if not first else 1.0)
    # sticker
    if "sticker" in sc:
        st0 = sc["sents"][sc["sticker"][2]]["start"] - sc["start"]
        if ti >= st0:
            k = ti - st0; im = STICKERS[sc["i"]].rotate(-5 + 3 * math.sin(k * 7) * math.exp(-k * 1.2), expand=True, resample=Image.BICUBIC)
            pasteC(img, im, 540, 1285, eob(k / .3))
    # captions
    cs = caption_state(sc, t)
    if cs:
        words, act, cstart = cs
        ci = caption_img(words, act, acc)
        pasteC(img, ci, 500, 1445, .85 + .15 * eob((t - cstart) / .12), 1.0)
    # cut flash
    if not first and ti < .13:
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), .55 * (1 - ti / .13))
    return img.tobytes()

def init():
    global TL, TITLES, STICKERS, NSTEPS
    TL, total = build_timeline()
    NSTEPS = 1
    for sc in TL:
        m = re.search(r"(\d+)\s*/\s*(\d+)", sc["badge"])
        if m: sc["step"] = int(m.group(1)); NSTEPS = max(NSTEPS, int(m.group(2)))
    for sc in TL:
        TITLES[sc["i"]] = make_title(sc["title"], sc["acc"])
        if "sticker" in sc: STICKERS[sc["i"]] = make_sticker(*sc["sticker"][:2])
    return total

