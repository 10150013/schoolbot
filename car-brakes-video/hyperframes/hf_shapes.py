"""SVG building blocks for the HyperFrames episodes (viewBox 0 50 1080 800)."""
import math

def col(c):
    return c if isinstance(c, str) else "#%02x%02x%02x" % tuple(c[:3])

def A(**kw):
    out = []
    for k, v in kw.items():
        if v is None: continue
        k = k.rstrip("_").replace("_", "-")
        out.append(f'{k}="{col(v) if k in ("fill", "stroke") else v}"')
    return " ".join(out)

def ell(cx, cy, rx, ry=None, fill="none", stroke=None, sw=None, **kw):
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{(rx if ry is None else ry):.1f}" {A(fill=fill, stroke=stroke, stroke_width=sw, **kw)}/>'

def rr(x0, y0, x1, y1, r=0, fill="none", stroke=None, sw=None, **kw):
    return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="{r}" {A(fill=fill, stroke=stroke, stroke_width=sw, **kw)}/>'

def poly(pts, fill="none", stroke=None, sw=None, **kw):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{p}" {A(fill=fill, stroke=stroke, stroke_width=sw, stroke_linejoin="round", **kw)}/>'

def line(x0, y0, x1, y1, stroke, sw, **kw):
    return f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" {A(stroke=stroke, stroke_width=sw, stroke_linecap="round", **kw)}/>'

def pline(pts, stroke, sw, **kw):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{p}" {A(fill="none", stroke=stroke, stroke_width=sw, stroke_linecap="round", stroke_linejoin="round", **kw)}/>'

def text(x, y, s, size, fill, stroke=None, sw=None, font="Archivo Black", weight=None, **kw):
    ex = dict(stroke=stroke, stroke_width=sw, paint_order="stroke" if stroke else None, stroke_linejoin="round" if stroke else None)
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-family="\'{font}\', sans-serif" {A(font_weight=weight, fill=fill, **ex, **kw)} '
            f'text-anchor="middle" dominant-baseline="central">{s}</text>')

def emoji(x, y, ch, size, **kw):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="middle" dominant-baseline="central" {A(**kw)}>{ch}</text>'

def g(inner, **kw):
    return f"<g {A(**kw)}>{inner}</g>"

def star_pts(cx, cy, r):
    pts = []
    for i in range(8):
        rr_ = r if i % 2 == 0 else r * .25; a = i * math.pi / 4 - math.pi / 2
        pts.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)))
    return pts

def bolt(cx, cy, r, **kw):
    pts = [(cx + r * math.cos(i * math.pi / 3), cy + r * math.sin(i * math.pi / 3)) for i in range(6)]
    return g(poly(pts, (205, 210, 220), (120, 125, 138), 3) + ell(cx, cy, r * .42, fill=(120, 125, 138)), **kw)

def wheel(cx, cy, R, nut="#ffe200", **kw):
    s = ell(cx, cy, R, fill=(22, 22, 26), stroke=(78, 80, 92), sw=5) + ell(cx, cy, R * .84, stroke=(44, 46, 56), sw=4)
    s += ell(cx, cy, R * .70, fill=(208, 213, 223)) + ell(cx, cy, R * .64, fill=(30, 32, 40))
    for i in range(5):
        a = i * 2 * math.pi / 5; nx, ny = -math.sin(a), math.cos(a)
        r0, r1, w0, w1 = R * .1, R * .64, R * .075, R * .12
        p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a)); p1 = (cx + r1 * math.cos(a), cy + r1 * math.sin(a))
        s += poly([(p0[0] + nx * w0, p0[1] + ny * w0), (p1[0] + nx * w1, p1[1] + ny * w1), (p1[0] - nx * w1, p1[1] - ny * w1), (p0[0] - nx * w0, p0[1] - ny * w0)], (190, 196, 210))
    s += ell(cx, cy, R * .2, fill=(222, 227, 236), stroke=(150, 156, 170), sw=3)
    for i in range(5):
        a = i * 2 * math.pi / 5 + math.pi / 5
        s += ell(cx + R * .12 * math.cos(a), cy + R * .12 * math.sin(a), R * .035, fill=nut)
    return g(s, **kw)

def rotor(cx, cy, R, **kw):
    s = ell(cx, cy, R, fill=(130, 136, 150), stroke=(215, 220, 232), sw=4) + ell(cx, cy, R * .93, stroke=(98, 103, 117), sw=3)
    s += ell(cx, cy, R * .62, fill=(112, 118, 132), stroke=(86, 90, 104), sw=3)
    for i in range(14):
        a = i * 2 * math.pi / 14
        s += ell(cx + R * .78 * math.cos(a), cy + R * .78 * math.sin(a), R * .045, fill=(48, 52, 64))
    s += ell(cx, cy, R * .40, fill=(88, 92, 106))
    for i in range(5):
        a = i * 2 * math.pi / 5
        s += ell(cx + R * .27 * math.cos(a), cy + R * .27 * math.sin(a), R * .045, fill=(40, 42, 52))
    s += ell(cx, cy, R * .12, fill=(36, 38, 46))
    return g(s, **kw)

def caliper(cx, cy, R, **kw):
    x0, x1, y0, y1 = cx + R * .40, cx + R * 1.0, cy - R * .62, cy + R * .62
    s = rr(x0, y0, x1, y1, 34, fill=(228, 40, 62), stroke=(255, 130, 140), sw=4)
    s += rr(x0 + 18, y0 + 18, x0 + 44, y1 - 18, 12, fill=(255, 110, 120))
    s += text((x0 + x1) / 2 + 8, cy, "BRAKE", 34, (255, 235, 238))
    return g(s, **kw)

def edge_rotor(**kw):
    s = rr(505, 160, 575, 840, 8, fill=(150, 156, 170), stroke=(220, 225, 236), sw=4)
    for y in range(200, 820, 36): s += line(512, y, 568, y, (110, 116, 130), 3)
    return g(s, **kw)

def pad_left(xf, y0, y1, thick, **kw):
    return g(rr(xf - thick - 28, y0, xf - thick, y1, 6, fill=(170, 176, 190)) + rr(xf - thick, y0 + 6, xf, y1 - 6, 6, fill=(120, 74, 40)), **kw)

def pad_right(xf, y0, y1, thick, **kw):
    return g(rr(xf + thick, y0, xf + thick + 28, y1, 6, fill=(170, 176, 190)) + rr(xf, y0 + 6, xf + thick, y1 - 6, 6, fill=(120, 74, 40)), **kw)

def arrow(x0, y0, x1, y1, color, w=14, **kw):
    a = math.atan2(y1 - y0, x1 - x0); hl = w * 2.6
    bx, by = x1 - hl * .8 * math.cos(a), y1 - hl * .8 * math.sin(a)
    head = poly([(x1, y1), (x1 - hl * math.cos(a - .45), y1 - hl * math.sin(a - .45)), (x1 - hl * math.cos(a + .45), y1 - hl * math.sin(a + .45))], color)
    return g(line(x0, y0, bx, by, color, w) + head, **kw)

def tick(cx, cy, **kw):
    return g(ell(cx, cy, 70, fill=(40, 210, 110), stroke="#fff", sw=6) + pline([(cx - 30, cy), (cx - 6, cy + 26), (cx + 36, cy - 28)], "#fff", 14), **kw)

def stand(x, gy, top, **kw):
    return g(poly([(x - 90, gy), (x + 90, gy), (x + 22, gy - 36), (x - 22, gy - 36)], "#ff8c00") + rr(x - 18, top, x + 18, gy - 36, 6, fill=(255, 170, 60)) + rr(x - 55, top - 12, x + 55, top + 6, 8, fill=(255, 200, 90)), **kw)
