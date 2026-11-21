"""Logo + narrow row assets for the console/flame designs (run after make_assets.py)."""
import os
from PIL import Image, ImageChops
ROOT = os.path.join(os.path.dirname(__file__), "..", "plugin", "usr", "lib", "enigma2", "python",
                    "Plugins", "Extensions", "Online4TechPanel", "assets")
HDR = Image.open(os.path.join(os.path.dirname(__file__), "src", "header.png")).convert("RGB")


def logo(width):
    crop = HDR.crop((18, 6, 380, 132))                      # dish + Online4Tech + slogan
    r, g, b = crop.split()
    lum = ImageChops.lighter(ImageChops.lighter(r, g), b)
    alpha = lum.point(lambda v: 0 if v < 90 else min(255, int((v - 90) * 3.2)))
    im = crop.convert("RGBA"); im.putalpha(alpha)
    h = int(round(width * im.height / float(im.width)))
    return im.resize((width, h), Image.LANCZOS)


def narrow(src, dst, w, k):
    im = Image.open(src).convert("RGBA")
    cut = int(60 * k)
    left, right = im.crop((0, 0, cut, im.height)), im.crop((im.width - cut, 0, im.width, im.height))
    mid = im.crop((cut, 0, cut + 4, im.height)).resize((w - 2 * cut, im.height))
    out = Image.new("RGBA", (w, im.height)); out.paste(left, (0, 0)); out.paste(mid, (cut, 0))
    out.paste(right, (w - cut, 0)); out.save(dst)


for design in ("console", "flame"):
    for d, k in (("fhd", 1.0), ("hd", 2 / 3.0)):
        base = os.path.join(ROOT, design, d)
        logo(int(round(340 * k))).save(os.path.join(base, "logo.png"))
        logo(int(round(620 * k))).save(os.path.join(base, "logo_big.png"))
        if design == "console":
            narrow(os.path.join(base, "row.png"), os.path.join(base, "rowm.png"), int(round(520 * k)), k)
            narrow(os.path.join(base, "row_sel.png"), os.path.join(base, "rowm_sel.png"), int(round(544 * k)), k)
print("ok")
