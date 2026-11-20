#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the glass-style PNG assets (run on a PC, not on the receiver).

    python3 tools/make_assets.py

Needs Pillow. Output goes to the plugin's assets/fhd (1920x1080) and
assets/hd (1280x720) folders.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "plugin", "usr", "lib", "enigma2", "python",
                   "Plugins", "Extensions", "Online4TechPanel", "assets")
SS = 3  # supersampling factor

ACCENT = (56, 189, 248)
ICON_COLORS = [
    (56, 189, 248),   # plugins
    (167, 139, 250),  # skins
    (74, 222, 128),   # updates
    (251, 191, 36),   # installed
    (251, 146, 60),   # tools
    (96, 165, 250),   # info
    (45, 212, 191),   # panel update
    (244, 114, 182),  # about
]


def rrect_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m


def vgrad(w, h, top, bottom):
    """RGBA vertical gradient."""
    g = Image.new("RGBA", (w, h))
    px = g.load()
    for y in range(h):
        t = y / float(max(1, h - 1))
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(4))
        for x in range(w):
            px[x, y] = c
    return g


def glass(w, h, r, tint=(120, 160, 255), strength=1.0, border=110):
    """A frosted-glass rounded card (RGBA) at final pixel size w x h."""
    W, H, R = w * SS, h * SS, r * SS
    base = vgrad(W, H,
                 (255, 255, 255, int(52 * strength)),
                 (tint[0], tint[1], tint[2], int(16 * strength)))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(base, (0, 0), rrect_mask(W, H, R))
    # top gloss
    gh = int(H * 0.5)
    gl = vgrad(W, gh, (255, 255, 255, int(40 * strength)), (255, 255, 255, 0))
    gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gloss.paste(gl, (0, 0))
    gloss = Image.composite(gloss, Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                            rrect_mask(W, H, R))
    img = Image.alpha_composite(img, gloss)
    # border
    bd = ImageDraw.Draw(img)
    bd.rounded_rectangle((0, 0, W - 1, H - 1), R, outline=(255, 255, 255, border),
                         width=SS * 2)
    return img.resize((w, h), Image.LANCZOS)


def selector(w, h, r, color=ACCENT):
    W, H, R = w * SS, h * SS, r * SS
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle((SS * 10, SS * 10, W - SS * 10, H - SS * 10), R,
                         outline=color + (255,), width=SS * 10)
    glow = glow.filter(ImageFilter.GaussianBlur(SS * 7))
    ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.rounded_rectangle((SS * 12, SS * 12, W - SS * 12, H - SS * 12), R - SS * 4,
                         fill=color + (26,), outline=color + (255,), width=SS * 4)
    rd.rounded_rectangle((SS * 17, SS * 17, W - SS * 17, H - SS * 17), R - SS * 8,
                         outline=(255, 255, 255, 120), width=SS * 2)
    img = Image.alpha_composite(glow, ring)
    return img.resize((w, h), Image.LANCZOS)


def pill(w, h, color):
    W, H, R = w * SS, h * SS, (h * SS) // 2
    top = tuple(min(255, c + 60) for c in color) + (235,)
    bot = tuple(int(c * 0.55) for c in color) + (235,)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(vgrad(W, H, top, bot), (0, 0), rrect_mask(W, H, R))
    gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(gloss).rounded_rectangle(
        (SS * 6, SS * 3, W - SS * 6, int(H * 0.5)), R, fill=(255, 255, 255, 70))
    gloss = Image.composite(gloss, Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                            rrect_mask(W, H, R))
    img = Image.alpha_composite(img, gloss)
    ImageDraw.Draw(img).rounded_rectangle((0, 0, W - 1, H - 1), R,
                                          outline=(255, 255, 255, 120), width=SS * 2)
    return img.resize((w, h), Image.LANCZOS)


def background(w, h):
    img = vgrad(w, h, (8, 13, 28, 255), (14, 22, 46, 255)).convert("RGB")

    def blob(cx, cy, scale, color, alpha):
        bw, bh = int(w * scale), int(h * scale * 1.4)
        m = Image.radial_gradient("L").resize((bw, bh), Image.BICUBIC)
        m = Image.eval(m, lambda v: int(max(0, 255 - v * 1.4143) * alpha))
        layer = Image.new("RGB", (bw, bh), color)
        img.paste(layer, (int(cx * w - bw / 2), int(cy * h - bh / 2)), m)

    blob(0.12, 0.10, 0.75, (20, 120, 190), 0.55)
    blob(0.92, 0.95, 0.80, (110, 60, 200), 0.50)
    blob(0.60, 0.40, 0.45, (20, 90, 150), 0.20)
    return img


# ----------------------------------------------------------------- icons
def draw_icon(idx, size, color):
    S = 512
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = color + (255,)
    cx = cy = S // 2
    sw = 34
    if idx == 0:  # plug
        d.rounded_rectangle((150, 190, 362, 350), 40, fill=c)
        d.rounded_rectangle((190, 80, 236, 200), 14, fill=c)
        d.rounded_rectangle((276, 80, 322, 200), 14, fill=c)
        d.rounded_rectangle((226, 340, 286, 440), 20, fill=c)
    elif idx == 1:  # palette
        d.ellipse((70, 90, 442, 420), fill=c)
        d.ellipse((300, 300, 420, 420), fill=(0, 0, 0, 0))
        for (x, y, r) in ((160, 200, 28), (250, 150, 28), (345, 190, 28), (150, 305, 28)):
            d.ellipse((x - r, y - r, x + r, y + r), fill=(0, 0, 0, 0))
    elif idx == 2:  # circular update arrow
        r = 150
        d.arc((cx - r, cy - r, cx + r, cy + r), 40, 320, fill=c, width=sw + 6)
        a = math.radians(320)
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        nx, ny = math.cos(a), math.sin(a)
        d.polygon([(px + tx * 62, py + ty * 62),
                   (px + nx * 66, py + ny * 66),
                   (px - nx * 66, py - ny * 66)], fill=c)
    elif idx == 3:  # installed / check box
        d.rounded_rectangle((90, 90, 422, 422), 70, outline=c, width=sw + 4)
        d.line([(170, 262), (234, 328), (354, 188)], fill=c, width=sw + 14, joint="curve")
    elif idx == 4:  # gear
        for k in range(8):
            a = k * 45
            tooth = Image.new("RGBA", (S, S), (0, 0, 0, 0))
            ImageDraw.Draw(tooth).rounded_rectangle((cx - 34, 52, cx + 34, 170), 14, fill=c)
            img.alpha_composite(tooth.rotate(-a, resample=Image.BICUBIC, center=(cx, cy)))
        d = ImageDraw.Draw(img)
        d.ellipse((cx - 150, cy - 150, cx + 150, cy + 150), fill=c)
        d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=(0, 0, 0, 0))
    elif idx == 5:  # info
        d.ellipse((70, 70, 442, 442), outline=c, width=sw + 4)
        d.ellipse((cx - 26, 140, cx + 26, 192), fill=c)
        d.rounded_rectangle((cx - 24, 224, cx + 24, 376), 14, fill=c)
    elif idx == 6:  # download into tray
        d.rounded_rectangle((cx - 26, 70, cx + 26, 280), 12, fill=c)
        d.polygon([(cx - 120, 250), (cx + 120, 250), (cx, 380)], fill=c)
        d.line([(90, 400), (90, 450), (422, 450), (422, 400)], fill=c, width=sw + 6, joint="curve")
    elif idx == 7:  # star
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rad = 190 if k % 2 == 0 else 84
            pts.append((cx + rad * math.cos(ang), cy + 12 + rad * math.sin(ang)))
        d.polygon(pts, fill=c)
    glow = img.filter(ImageFilter.GaussianBlur(14))
    glow = Image.eval(glow.split()[3], lambda v: int(v * 0.55))
    glow_img = Image.new("RGBA", (S, S), color + (0,))
    glow_img.putalpha(glow)
    out = Image.alpha_composite(glow_img, img)
    return out.resize((size, size), Image.LANCZOS)


def plugin_icon(w, h):
    img = glass(w * 2, h * 2, 18, tint=(56, 189, 248), strength=1.4, border=160)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default(size=int(h * 2 * 0.52))
    except TypeError:
        font = ImageFont.load_default()
    text = "O4T"
    bb = d.textbbox((0, 0), text, font=font)
    d.text(((w * 2 - (bb[2] - bb[0])) / 2 - bb[0], (h * 2 - (bb[3] - bb[1])) / 2 - bb[1]),
           text, font=font, fill=(255, 255, 255, 255))
    return img.resize((w, h), Image.LANCZOS)


def build(name, k):
    out = os.path.join(OUT, name)
    os.makedirs(out, exist_ok=True)

    def s(v):
        return int(round(v * k))

    background(s(1920), s(1080)).save(os.path.join(out, "bg.png"), optimize=True)
    glass(s(360), s(300), s(38)).save(os.path.join(out, "tile.png"), optimize=True)
    for tname, tcol in THEMES.items():
        selector(s(392), s(332), s(48), tcol).save(os.path.join(out, "sel_%s.png" % tname),
                                                  optimize=True)
    glass(s(1060), s(790), s(34), strength=0.8).save(os.path.join(out, "panel_l.png"), optimize=True)
    glass(s(670), s(790), s(34), strength=0.8).save(os.path.join(out, "panel_r.png"), optimize=True)
    glass(s(1760), s(790), s(34), strength=0.8).save(os.path.join(out, "panel_f.png"), optimize=True)
    for nm, col in (("red", (225, 29, 72)), ("green", (34, 197, 94)),
                    ("yellow", (234, 179, 8)), ("blue", (59, 130, 246))):
        pill(s(250), s(56), col).save(os.path.join(out, "btn_%s.png" % nm), optimize=True)
    for i, col in enumerate(ICON_COLORS):
        draw_icon(i, s(128), col).save(os.path.join(out, "ic%d.png" % i), optimize=True)


THEMES = {"cyan": (56, 189, 248), "violet": (167, 139, 250), "green": (74, 222, 128),
          "orange": (251, 146, 60), "pink": (244, 114, 182)}


def main():
    build("fhd", 1.0)
    build("hd", 2.0 / 3.0)
    plugin_icon(120, 60).save(os.path.join(OUT, "..", "plugin.png"), optimize=True)
    print("assets written to", OUT)


if __name__ == "__main__":
    sys.exit(main())
