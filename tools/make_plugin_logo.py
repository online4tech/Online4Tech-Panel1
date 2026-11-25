#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Glossy Online4Tech plugin logo (satellite dish + red signal + 'Online4Tech').

    python3 tools/make_plugin_logo.py

Writes the receiver icon (plugin.png, 120x60) and hi-res branding files (branding/).
Needs Pillow. Colours follow the panel logo: electric blue, signal red, silver, navy."""
import math
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugin", "usr", "lib", "enigma2", "python", "Plugins", "Extensions",
                      "Online4TechPanel")
FONT = os.path.join(PLUGIN, "fonts", "Tajawal-Bold.ttf")
S = 2                                   # supersampling
W, H = 1024 * S, 512 * S


def vgrad(w, h, top, bottom):
    g = Image.new("RGBA", (w, h))
    px = g.load()
    for y in range(h):
        t = y / float(max(1, h - 1))
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(4))
        for x in range(w):
            px[x, y] = c
    return g


def rmask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


def radial(w, h, cx, cy, r, inner, outer):
    g = Image.new("RGBA", (w, h))
    px = g.load()
    for y in range(h):
        for x in range(w):
            t = min(1.0, math.hypot(x - cx, y - cy) / float(r))
            px[x, y] = tuple(int(inner[i] + (outer[i] - inner[i]) * t) for i in range(4))
    return g


def glow(img, radius, strength=1.0):
    g = img.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = g.getchannel("A").point(lambda v: min(255, int(v * strength)))
        g.putalpha(a)
    return g


def tile():
    """Glossy rounded tile: electric-blue to deep-navy gradient, light streak, glass highlight, rim."""
    m = 16 * S
    w, h = W - 2 * m, H - 2 * m
    r = 118 * S
    body = vgrad(w, h, (50, 140, 255, 255), (6, 20, 78, 255))
    # soft cyan light from the lower left, deep navy corner top right
    body = Image.alpha_composite(body, radial(w, h, int(w * 0.18), int(h * 1.05), int(w * 0.75),
                                               (56, 189, 248, 120), (56, 189, 248, 0)))
    streak = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(streak).polygon([(int(w * 0.55), 0), (int(w * 0.78), 0), (int(w * 0.42), h),
                                    (int(w * 0.19), h)], fill=(120, 200, 255, 26))
    body = Image.alpha_composite(body, streak.filter(ImageFilter.GaussianBlur(14 * S)))
    # glass highlight over the upper half (curved bottom edge)
    hl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse((-int(w * 0.12), -int(h * 0.95), int(w * 1.12), int(h * 0.50)),
                               fill=(255, 255, 255, 70))
    hl_a = ImageChops.multiply(hl.getchannel("A"), vgrad(w, h, (0, 0, 0, 255), (0, 0, 0, 90)).getchannel("A"))
    hl.putalpha(hl_a)
    body = Image.alpha_composite(body, hl)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # drop shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((m, m + 10 * S, W - m, H - m + 10 * S), r, fill=(0, 0, 0, 150))
    out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(14 * S)))
    out.paste(body, (m, m), rmask(w, h, r))
    rim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(rim).rounded_rectangle((m, m, W - m, H - m), r, outline=(255, 255, 255, 215), width=5 * S)
    ImageDraw.Draw(rim).rounded_rectangle((m + 9 * S, m + 9 * S, W - m - 9 * S, H - m - 9 * S), r - 9 * S,
                                          outline=(150, 210, 255, 90), width=2 * S)
    return Image.alpha_composite(out, rim)


def ell(cx, cy, rx, ry, ang_deg, n=180):
    """Polygon of an ellipse centred (cx, cy), radii rx/ry, rotated clockwise by ang_deg (image coords)."""
    a = math.radians(ang_deg)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)))
    return pts


def paint(mask_pts, fill_img):
    """fill_img (RGBA, full canvas) clipped to a polygon."""
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(mask_pts, fill=255)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(fill_img, (0, 0), m)
    return out


def dish_scene():
    """Silver satellite dish facing the upper right, stand, feed arm and red signal waves."""
    k = S
    cx, cy = 205 * k, 292 * k                     # dish centre
    up = (math.cos(math.radians(-45)), math.sin(math.radians(-45)))     # facing direction
    scene = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(scene)
    # stand
    d.polygon([(cx - 16 * k, cy + 78 * k), (cx + 16 * k, cy + 78 * k), (cx + 30 * k, cy + 142 * k),
               (cx - 30 * k, cy + 142 * k)], fill=(205, 222, 248, 255))
    d.ellipse((cx - 92 * k, cy + 126 * k, cx + 92 * k, cy + 168 * k), fill=(238, 245, 255, 255),
              outline=(110, 150, 215, 255), width=2 * k)
    d.ellipse((cx - 62 * k, cy + 134 * k, cx + 62 * k, cy + 158 * k), fill=(140, 172, 226, 255))
    # soft shadow under the bowl
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon(ell(cx + 10 * k, cy + 14 * k, 142 * k, 102 * k, 45), fill=(0, 10, 60, 150))
    scene = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * k)), scene)
    # bowl: outer rim, then the concave face (lit from the upper left)
    rim = vgrad(W, H, (255, 255, 255, 255), (150, 175, 220, 255))
    scene = Image.alpha_composite(scene, paint(ell(cx, cy, 142 * k, 102 * k, 45), rim))
    fx, fy = cx + up[0] * 9 * k, cy + up[1] * 9 * k
    face = radial(W, H, int(fx - 40 * k), int(fy - 50 * k), 190 * k, (225, 242, 255, 255), (28, 104, 214, 255))
    scene = Image.alpha_composite(scene, paint(ell(fx, fy, 124 * k, 86 * k, 45), face))
    ImageDraw.Draw(scene).polygon(ell(fx, fy, 124 * k, 86 * k, 45), outline=(255, 255, 255, 200))
    for r in (0, 1, 2):                                 # thicken the highlight edge
        ImageDraw.Draw(scene).line(ell(fx, fy, (124 - r) * k, (86 - r) * k, 45) + [ell(fx, fy, (124 - r) * k, (86 - r) * k, 45)[0]],
                                   fill=(255, 255, 255, 170), width=2 * k)
    # feed arm to the LNB
    tip = (cx + up[0] * 150 * k, cy + up[1] * 150 * k)
    d = ImageDraw.Draw(scene)
    d.line((fx, fy, tip[0], tip[1]), fill=(120, 150, 210, 255), width=11 * k)
    d.line((fx, fy, tip[0], tip[1]), fill=(240, 247, 255, 255), width=7 * k)
    r0 = 15 * k
    d.ellipse((tip[0] - r0, tip[1] - r0, tip[0] + r0, tip[1] + r0), fill=(255, 255, 255, 255),
              outline=(90, 130, 205, 255), width=3 * k)
    # red signal waves
    arcs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(arcs)
    for i, (r, wd) in enumerate(((52, 20), (92, 18), (132, 16))):
        rr, ww = r * k, wd * k
        ad.arc((tip[0] - rr, tip[1] - rr, tip[0] + rr, tip[1] + rr), start=-88, end=-2, fill=(255, 255, 255, 255), width=ww)
        for ang in (-88, -2):
            ex, ey = tip[0] + rr * math.cos(math.radians(ang)), tip[1] + rr * math.sin(math.radians(ang))
            ad.ellipse((ex - ww / 2, ey - ww / 2, ex + ww / 2, ey + ww / 2), fill=(255, 255, 255, 255))
    col = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    col.paste(vgrad(W, H, (255, 110, 120, 255), (214, 16, 40, 255)), (0, 0), arcs.getchannel("A"))
    scene = Image.alpha_composite(scene, glow(col, 12 * k, 1.5))
    return Image.alpha_composite(scene, col)


def text_layer():
    """'Online' over '4Tech' (red 4), bold slightly italic, glossy gradient fill with a soft shadow."""
    k = S
    x0, max_w = 500 * k, 500 * k
    size = 170 * k
    while ImageFont.truetype(FONT, size).getbbox("Online")[2] > max_w:
        size -= 2 * k
    f = ImageFont.truetype(FONT, size)
    lines = [("Online", 70 * k, None), ("4Tech", 70 * k + int(size * 0.86), "4")]

    def grad_text(txt, xy, top, bottom):
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).text(xy, txt, font=f, fill=255)
        bb = m.getbbox()
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        g.paste(vgrad(bb[2] - bb[0], bb[3] - bb[1], top + (255,), bottom + (255,)), (bb[0], bb[1]))
        sh = Image.new("RGBA", (W, H), (0, 12, 60, 0))
        sh.putalpha(m.point(lambda v: int(v * 0.7)))
        sh = ImageChops.offset(sh, 4 * k, 6 * k).filter(ImageFilter.GaussianBlur(4 * k))
        out = sh
        top_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        top_l.paste(g, (0, 0), m)
        return Image.alpha_composite(out, top_l), bb

    def italic(img, yc, shear=0.14):
        return img.transform(img.size, Image.AFFINE, (1, shear, -shear * yc, 0, 1, 0), Image.BICUBIC)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img, bb = grad_text("Online", (x0, lines[0][1]), (255, 255, 255), (150, 205, 255))
    layer = Image.alpha_composite(layer, italic(img, (bb[1] + bb[3]) / 2.0))
    y2 = lines[1][1]
    img, bb = grad_text("4", (x0, y2), (255, 130, 130), (214, 20, 44))
    layer = Image.alpha_composite(layer, italic(img, (bb[1] + bb[3]) / 2.0))
    fw = f.getlength("4") + size * 0.03
    img, bb = grad_text("Tech", (x0 + fw, y2), (232, 246, 255), (120, 190, 255))
    return Image.alpha_composite(layer, italic(img, (bb[1] + bb[3]) / 2.0))


def render():
    img = tile()
    img = Image.alpha_composite(img, text_layer())
    img = Image.alpha_composite(img, dish_scene())
    return img


def main():
    big = render()
    hi = big.resize((1024, 512), Image.LANCZOS)
    os.makedirs(os.path.join(ROOT, "branding"), exist_ok=True)
    hi.save(os.path.join(ROOT, "branding", "online4tech-plugin-icon-1024x512.png"), optimize=True)
    # square avatar (social / GitHub): same artwork centred on a navy rounded square
    sq = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    sq.alpha_composite(hi, (0, 256))
    sq.resize((512, 512), Image.LANCZOS).save(os.path.join(ROOT, "branding", "online4tech-square-512.png"),
                                              optimize=True)
    # receiver icon (plugin browser): crisp 120x60 with a hair of sharpening
    small = big.resize((240, 120), Image.LANCZOS).resize((120, 60), Image.LANCZOS)
    small = small.filter(ImageFilter.UnsharpMask(radius=0.8, percent=90, threshold=2))
    small.save(os.path.join(PLUGIN, "..", "plugin.png") if False else os.path.join(PLUGIN, "plugin.png"),
               optimize=True)
    print("logo written")


if __name__ == "__main__":
    sys.exit(main())
