# -*- coding: utf-8 -*-
"""Skin builder: one 1920x1080 design scaled for HD (1280x720) images."""
from __future__ import absolute_import
import os

try:
    from enigma import getDesktop
except Exception:  # pragma: no cover
    getDesktop = None

from .utils import THEMES, get_setting
from .version import PLUGIN_DIR

TEXT = "#FFFFFF"
MUTED = "#9FB3D1"
ACCENT = "#38BDF8"
THEME_COLORS = {"cyan": "#38BDF8", "violet": "#A78BFA", "green": "#4ADE80",
                "orange": "#FB923C", "pink": "#F472B6"}


def theme():
    t = get_setting("theme", "cyan")
    return t if t in THEMES else "cyan"


def accent():
    return THEME_COLORS[theme()]
SOFT = "#E5EDFF"

_cache = {}


DESIGNS = ("glass", "console", "flame", "lite")
FONT_SCALES = (90, 100, 115)


def design():
    d = get_setting("design", "glass")
    return d if d in DESIGNS else "glass"


def font_scale():
    v = get_setting("font_scale", 100)
    v = {"small": 90, "normal": 100, "large": 115}.get(v, v)   # old text values
    try:
        v = int(v)
    except (TypeError, ValueError):
        return 100
    return v if v in FONT_SCALES else 100


STYLES = {
    "glass": dict(text=TEXT, muted=MUTED, soft=SOFT, accent=None, flat=False, rows=False,
                  pilltext=TEXT, bg="#0A1020"),
    "console": dict(text="#F1F5F9", muted="#98A6BC", soft="#DDE6F5", accent="#E2B23C", flat=False,
                    rows=True, pilltext="#1B1405", bg="#0A0F1A"),
    "flame": dict(text="#FFFFFF", muted="#B7A99A", soft="#F1E6DA", accent="#FF8A2A", flat=False,
                  rows=True, pilltext="#FFFFFF", bg="#08080A"),
    "lite": dict(text="#FFFFFF", muted="#9AA7B8", soft="#DDE6F2", accent=None, flat=True,
                 rows=True, pilltext="#001018", bg="#0B0F14", panel="#141A22", row="#1B232E"),
}


def style():
    st = dict(STYLES[design()])
    if not st.get("accent"):
        st["accent"] = THEME_COLORS[theme()]
    return st


def is_flat():
    return STYLES[design()]["flat"]


def uses_rows():
    return STYLES[design()]["rows"]


class Metrics(object):
    def __init__(self):
        try:
            w = getDesktop(0).size().width()
        except Exception:
            w = 1280
        if w >= 1920:
            self.W, self.H, self.assets, self.k = 1920, 1080, "fhd", 1.0
        else:
            self.W, self.H, self.assets, self.k = 1280, 720, "hd", 2.0 / 3.0
        self.design, self.fs = design(), font_scale()
        base = os.path.join(PLUGIN_DIR, "assets")
        if self.design != "glass":
            base = os.path.join(base, self.design)
        self.dir = os.path.join(base, self.assets)

    def S(self, v):
        return int(round(v * self.k))

    def pos(self, x, y):
        return "%d,%d" % (self.S(x), self.S(y))

    def size(self, w, h):
        return "%d,%d" % (self.S(w), self.S(h))

    def rect(self, x, y, w, h):
        return 'position="%s" size="%s"' % (self.pos(x, y), self.size(w, h))

    def font(self, n):
        return "Regular;%d" % max(8, int(round(n * self.k * self.fs / 100.0)))

    def pix(self, name):
        return os.path.join(self.dir, name + ".png")


def metrics():
    key = (design(), font_scale())
    if _cache.get("key") != key:
        _cache["m"], _cache["key"] = Metrics(), key
    return _cache["m"]


# ---------------------------------------------------------------- pieces
def _screen_open(m, name):
    return ('<screen name="%s" position="center,center" size="%d,%d" title="Online4Tech Panel" '
            'flags="wfNoBorder" backgroundColor="#00%s">\n'
            % (name, m.W, m.H, STYLES[m.design]["bg"][1:]))


def _header(m, title_size=36):
    """Banner is baked into bg.png; only a section title sits below it."""
    return (
        '<ePixmap pixmap="%s" position="0,0" size="%d,%d" zPosition="-5" />\n'
        '<widget name="title" %s font="%s" foregroundColor="%s" transparent="1" '
        'halign="left" valign="center" zPosition="3" />\n'
        % (m.pix("bg"), m.W, m.H, m.rect(90, 184, 1300, 48), m.font(title_size), accent()))


def _footer(m):
    out = []
    for i, c in enumerate(("red", "green", "yellow", "blue")):
        x = 80 + i * 274
        out.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="1" />\n'
                   % (m.pix("btn_" + c), m.rect(x, 972, 250, 56)))
        out.append('<widget name="key_%s" %s font="%s" foregroundColor="%s" transparent="1" '
                   'halign="center" valign="center" zPosition="3" />\n'
                   % (c, m.rect(x, 972, 250, 56), m.font(25), TEXT))
    out.append('<widget name="ver" %s font="%s" foregroundColor="%s" transparent="1" '
               'halign="right" valign="center" zPosition="3" />\n'
               % (m.rect(1440, 972, 400, 56), m.font(24), MUTED))
    return "".join(out)


# ---------------------------------------------------------------- screens
MAIN_POS = []
for _i in range(8):
    MAIN_POS.append((40 + (_i % 4) * 333, 215 + (_i // 4) * 282))
GLASS_TILE = (300, 250)
CARD = (1384, 196, 496, 700)      # device card on the main screen (glass)


def _glass_main():
    m = metrics()
    x = [_screen_open(m, "O4TMain"), _header(m)]
    tw, th = GLASS_TILE
    for i, (tx, ty) in enumerate(MAIN_POS):
        x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="1" />\n'
                 % (m.pix("tile_s"), m.rect(tx, ty, tw, th)))
        x.append('<widget name="ic%d" %s alphatest="blend" zPosition="3" />\n'
                 % (i, m.rect(tx + 86, ty + 10, 128, 128)))
        x.append('<widget name="tt%d" %s font="%s" foregroundColor="%s" transparent="1" '
                 'halign="center" valign="center" zPosition="3" />\n'
                 % (i, m.rect(tx + 8, ty + 142, tw - 16, 44), m.font(30), TEXT))
        x.append('<widget name="ts%d" %s font="%s" foregroundColor="%s" transparent="1" '
                 'halign="center" valign="center" zPosition="3" />\n'
                 % (i, m.rect(tx + 8, ty + 190, tw - 16, 34), m.font(20), MUTED))
    x.append('<widget name="sel" pixmap="%s" %s alphatest="blend" zPosition="2" />\n'
             % (m.pix("sel_" + theme() + "_s"), m.rect(MAIN_POS[0][0] - 16, MAIN_POS[0][1] - 16, tw + 32, th + 32)))
    cx, cy, cw, ch = CARD
    x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="1" />\n'
             % (m.pix("panel_dm"), m.rect(cx, cy, cw, ch)))
    x.append(_devcard_labels(m, cx, cy, cw, TEXT, MUTED, THEME_COLORS[theme()]))
    x.append('<widget name="hint" %s font="%s" foregroundColor="%s" transparent="1" '
             'halign="center" valign="center" zPosition="3" />\n'
             % (m.rect(40, 800, 1300, 56), m.font(28), SOFT))
    x.append(_footer(m))
    x.append("</screen>")
    return "".join(x)


def _devcard_labels(m, cx, cy, cw, text, muted, accent):
    """Device card text: 5 blocks, each a small caption (dcN) over a value (dvN)."""
    out = ['<widget name="dct" %s font="%s" foregroundColor="%s" transparent="1" halign="center" '
           'valign="center" zPosition="3" />\n' % (m.rect(cx + 16, cy + 18, cw - 32, 50), m.font(32), accent)]
    for k in range(5):
        yy = cy + 90 + k * 118
        out.append('<widget name="dc%d" %s font="%s" foregroundColor="%s" transparent="1" halign="left" '
                   'valign="center" zPosition="3" />\n' % (k, m.rect(cx + 28, yy, cw - 56, 30), m.font(21), accent))
        out.append('<widget name="dv%d" %s font="%s" foregroundColor="%s" transparent="1" halign="left" '
                   'valign="top" zPosition="3" />\n' % (k, m.rect(cx + 28, yy + 32, cw - 56, 70), m.font(27), text))
    return "".join(out)


def _glass_list(name):
    m = metrics()
    x = [_screen_open(m, name), _header(m)]
    x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="0" />\n'
             % (m.pix("panel_l"), m.rect(80, 236, 1060, 700)))
    x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="0" />\n'
             % (m.pix("panel_r"), m.rect(1170, 236, 670, 700)))
    x.append('<widget name="list" %s font="%s" itemHeight="%d" scrollbarMode="showOnDemand" '
             'transparent="1" foregroundColor="%s" foregroundColorSelected="#FFFFFF" '
             'backgroundColorSelected="#44%s" zPosition="2" />\n'
             % (m.rect(106, 258, 1008, 656), m.font(30), m.S(54), TEXT, accent()[1:]))
    x.append('<widget name="status" %s font="%s" foregroundColor="%s" transparent="1" '
             'halign="center" valign="center" zPosition="3" />\n'
             % (m.rect(106, 258, 1008, 656), m.font(32), MUTED))
    x.append('<widget name="detail" %s font="%s" foregroundColor="%s" transparent="1" '
             'scrollbarMode="showOnDemand" zPosition="2" />\n'
             % (m.rect(1200, 262, 610, 640), m.font(27), SOFT))
    x.append(_footer(m))
    x.append("</screen>")
    return "".join(x)


def _glass_text(name):
    m = metrics()
    x = [_screen_open(m, name), _header(m)]
    x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="0" />\n'
             % (m.pix("panel_f"), m.rect(80, 236, 1760, 700)))
    x.append('<widget name="detail" %s font="%s" foregroundColor="%s" transparent="1" '
             'scrollbarMode="showOnDemand" zPosition="2" />\n'
             % (m.rect(120, 270, 1680, 640), m.font(30), SOFT))
    x.append(_footer(m))
    x.append("</screen>")
    return "".join(x)


# ------------------------------------------------------------ store (card grid) screen
STORE_COLS, STORE_ROWS = 4, 3
CARD_W, CARD_H, CARD_GX, CARD_GY = 250, 196, 16, 14
GRID_X, GRID_Y = 364, 272


def card_xy(i):
    col, row = i % STORE_COLS, i // STORE_COLS
    return GRID_X + col * (CARD_W + CARD_GX), GRID_Y + row * (CARD_H + CARD_GY)


def _glass_store(name):
    m = metrics()
    x = [_screen_open(m, name),
         '<ePixmap pixmap="%s" position="0,0" size="%d,%d" zPosition="-5" />\n' % (m.pix("bg"), m.W, m.H)]

    def pix(img, x0, y0, w, h, z=0):
        x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="%d" />\n'
                 % (m.pix(img), m.rect(x0, y0, w, h), z))

    def lab(nm, x0, y0, w, h, size, color, align="center", z=4, valign="center"):
        x.append('<widget name="%s" %s font="%s" foregroundColor="%s" transparent="1" '
                 'halign="%s" valign="%s" zPosition="%d" />\n'
                 % (nm, m.rect(x0, y0, w, h), m.font(size), color, align, valign, z))

    pix("panel_s", 24, 190, 300, 770)
    pix("panel_c", 340, 190, 1096, 770)
    pix("panel_d", 1448, 190, 448, 770)
    x.append('<widget name="cats" %s font="%s" itemHeight="%d" scrollbarMode="showOnDemand" '
             'transparent="1" foregroundColor="%s" foregroundColorSelected="#FFFFFF" '
             'backgroundColorSelected="#55%s" zPosition="2" />\n'
             % (m.rect(38, 206, 272, 738), m.font(25), m.S(52), TEXT, accent()[1:]))
    lab("title", 376, 202, 470, 52, 36, TEXT, "left")
    pix("search", 868, 202, 560, 54, 1)
    lab("search", 904, 204, 490, 50, 24, MUTED, "left")
    # cards
    for i in range(STORE_COLS * STORE_ROWS):
        cx, cy = card_xy(i)
        x.append('<widget name="cbg%d" pixmap="%s" %s alphatest="blend" zPosition="1" />\n'
                 % (i, m.pix("card"), m.rect(cx, cy, CARD_W, CARD_H)))
        x.append('<widget name="ci%d" %s alphatest="blend" scale="1" zPosition="3" />\n'
                 % (i, m.rect(cx + 89, cy + 12, 72, 72)))
        lab("cn%d" % i, cx + 8, cy + 88, CARD_W - 16, 34, 25, TEXT)
        lab("cd%d" % i, cx + 8, cy + 120, CARD_W - 16, 28, 19, MUTED)
        x.append('<widget name="cp%d" pixmap="%s" %s alphatest="blend" zPosition="2" />\n'
                 % (i, m.pix("pill_blue"), m.rect(cx + 30, cy + 152, 190, 38)))
        lab("cl%d" % i, cx + 30, cy + 152, 190, 38, 21, TEXT)
    x.append('<widget name="sel" pixmap="%s" %s alphatest="blend" zPosition="5" />\n'
             % (m.pix("card_sel_" + theme()), m.rect(GRID_X - 21, GRID_Y - 17, 292, 230)))
    lab("status", 376, 400, 1020, 200, 30, MUTED)
    lab("pager", 376, 906, 1020, 44, 24, SOFT)
    # details
    x.append('<widget name="di" %s alphatest="blend" scale="1" zPosition="3" />\n' % m.rect(1608, 206, 128, 128))
    lab("dn", 1464, 340, 416, 44, 32, TEXT)
    lab("dd", 1464, 384, 416, 52, 21, MUTED, valign="top")
    lab("dpt", 1464, 442, 416, 30, 22, accent(), "left")
    lab("dp", 1464, 472, 416, 50, 18, SOFT, "left", valign="top")
    lab("dct", 1464, 526, 416, 30, 22, accent(), "left")
    lab("dc", 1464, 556, 416, 40, 20, SOFT, "left", valign="top")
    lab("drt", 1464, 612, 416, 30, 22, accent(), "left")
    lab("dr", 1464, 642, 416, 40, 20, SOFT, "left", valign="top")
    for j, nm in enumerate(("green", "red", "blue")):
        yy = 744 + j * 68
        pix("wpill_" + nm, 1472, yy, 400, 50, 2)
        lab("db%d" % j, 1472, yy, 400, 50, 24, TEXT)
    # footer
    for k, c in enumerate(("red", "green", "yellow", "blue")):
        bx = 24 + k * 264
        pix("btn_" + c, bx, 972, 250, 56, 1)
        lab("key_" + c, bx, 972, 250, 56, 25, TEXT)
    lab("contact", 1100, 972, 796, 56, 26, SOFT, "right")
    lab("ver", 1100, 1030, 796, 40, 18, MUTED, "right")
    x.append("</screen>")
    return "".join(x)


# ====================================================================
# Row based designs: console / flame / lite
# ====================================================================
ROW_W, ROW_H, ROW_STEP = 940, 76, 84
ROWS_PER_PAGE = 8
ROW_X, ROW_Y = 460, 262


STATIC = {}      # widget name -> fixed text (tx*) of the screen being built


class _B(object):
    """Tiny helper that emits either pixmaps or flat coloured boxes."""

    def __init__(self, name):
        self.m = metrics()
        self.st = style()
        self.flat = self.st["flat"]
        self.x = [_screen_open(self.m, name)]
        self.n = 0
        STATIC.clear()
        if not self.flat:
            self.x.append('<ePixmap pixmap="%s" position="0,0" size="%d,%d" zPosition="-5" />\n'
                          % (self.m.pix("bg"), self.m.W, self.m.H))

    def box(self, img, x, y, w, h, z=0, color=None):
        if self.flat:
            self.n += 1
            self.x.append('<widget name="bx%d" %s backgroundColor="%s" transparent="0" zPosition="%d" />\n'
                          % (self.n, self.m.rect(x, y, w, h), color or self.st["panel"], z))
        else:
            self.x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="%d" />\n'
                          % (self.m.pix(img), self.m.rect(x, y, w, h), z))

    def wbox(self, nm, img, x, y, w, h, z=0, color=None, scale=False):
        """A named, show/hide-able box (pixmap or flat colour)."""
        if self.flat:
            self.x.append('<widget name="%s" %s backgroundColor="%s" transparent="0" zPosition="%d" />\n'
                          % (nm, self.m.rect(x, y, w, h), color or self.st["row"], z))
        else:
            self.x.append('<widget name="%s" %s %s alphatest="blend" %szPosition="%d" />\n'
                          % (nm, ('pixmap="%s"' % self.m.pix(img)) if img else "", self.m.rect(x, y, w, h),
                             'scale="1" ' if scale else "", z))

    def icon(self, nm, x, y, w, h, z=3):
        if self.flat:
            return
        self.x.append('<widget name="%s" %s alphatest="blend" scale="1" zPosition="%d" />\n'
                      % (nm, self.m.rect(x, y, w, h), z))

    def lab(self, nm, x, y, w, h, size, color, align="left", z=4, valign="center"):
        self.x.append('<widget name="%s" %s font="%s" foregroundColor="%s" transparent="1" '
                      'halign="%s" valign="%s" zPosition="%d" />\n'
                      % (nm, self.m.rect(x, y, w, h), self.m.font(size), color, align, valign, z))

    def static(self, text, x, y, w, h, size, color, align="left", z=4):
        self.n += 1
        nm = "tx%d" % self.n
        STATIC[nm] = text
        self.x.append('<widget name="%s" %s font="%s" foregroundColor="%s" transparent="1" '
                      'halign="%s" valign="center" zPosition="%d" />\n'
                      % (nm, self.m.rect(x, y, w, h), self.m.font(size), color, align, z))

    def header(self, title=True):
        st = self.st
        self.static("Online4Tech Panel", 60, 18, 900, 60, 46, st["accent"])
        self.static("خليك دايما اونلاين", 62, 78, 900, 36, 26, st["muted"])
        self.lab("clock", 1380, 18, 480, 56, 36, st["text"], "right")
        if title:
            self.lab("title", 60, 124, 1200, 46, 34, st["accent"])

    def footer(self, with_ver=True):
        st = self.st
        self.box("bar", 40, 978, 1840, 72, 0, st.get("panel"))
        for k, c in enumerate(("red", "green", "yellow", "blue")):
            bx = 76 + k * 350
            col = {"red": "#EF4444", "green": "#22C55E", "yellow": "#EAB308", "blue": "#3B82F6"}[c]
            self.box("dot_" + c, bx, 1000, 28, 28, 2, col)
            self.lab("key_" + c, bx + 44, 978, 290, 72, 25, st["text"])
        if with_ver:
            self.lab("ver", 1480, 978, 380, 72, 22, st["muted"], "right")

    def done(self):
        self.x.append("</screen>")
        return "".join(self.x)


def row_xy(i):
    return ROW_X, ROW_Y + i * ROW_STEP


def _rows_main():
    b = _B("O4TMain")
    st = b.st
    b.header(title=False)
    for i in range(8):
        x, y = ROW_X, 196 + i * 88
        b.box("row", x, y, ROW_W, ROW_H, 1, st.get("row"))
        b.icon("ic%d" % i, x + 14, y + 12, 52, 52)
        b.lab("tt%d" % i, x + 84, y, 330, ROW_H, 30, st["text"])
        b.lab("ts%d" % i, x + 420, y, 500, ROW_H, 21, st["muted"])
    b.wbox("sel", "row_sel", ROW_X - 12, 196 - 12, 964, 100, 0 if b.flat else 2, st["accent"])
    b.box("panel_d", 1440, 196, 440, 700, 0, st.get("panel"))
    b.x.append(_devcard_labels(b.m, 1440, 196, 440, st["text"], st["muted"], st["accent"]))
    b.lab("hint", ROW_X, 906, ROW_W, 48, 24, st["soft"], "center")
    b.footer()
    return b.done()


def main_rows_pos(i):
    return ROW_X, 196 + i * 88


def _rows_list(name):
    b = _B(name)
    st = b.st
    b.header()
    b.box("panel_l", 80, 190, 1060, 700, 0, st.get("panel"))
    b.box("panel_r", 1170, 190, 670, 700, 0, st.get("panel"))
    b.x.append('<widget name="list" %s font="%s" itemHeight="%d" scrollbarMode="showOnDemand" '
               'transparent="1" foregroundColor="%s" foregroundColorSelected="#FFFFFF" '
               'backgroundColorSelected="#55%s" zPosition="2" />\n'
               % (b.m.rect(106, 212, 1008, 656), b.m.font(30), b.m.S(54), st["text"], st["accent"][1:]))
    b.lab("status", 106, 212, 1008, 656, 32, st["muted"], "center")
    b.x.append('<widget name="detail" %s font="%s" foregroundColor="%s" transparent="1" '
               'scrollbarMode="showOnDemand" zPosition="2" />\n'
               % (b.m.rect(1200, 216, 610, 640), b.m.font(27), st["soft"]))
    b.footer()
    return b.done()


def _rows_text(name):
    b = _B(name)
    st = b.st
    b.header()
    b.box("panel_f", 80, 190, 1760, 700, 0, st.get("panel"))
    b.x.append('<widget name="detail" %s font="%s" foregroundColor="%s" transparent="1" '
               'scrollbarMode="showOnDemand" zPosition="2" />\n'
               % (b.m.rect(120, 224, 1680, 640), b.m.font(30), st["soft"]))
    b.footer()
    return b.done()


def _rows_store(name):
    b = _B(name)
    st = b.st
    b.header(title=False)
    b.lab("contact", 900, 78, 960, 36, 22, st["muted"], "right")
    b.box("panel_s", 40, 190, 380, 770, 0, st.get("panel"))
    b.box("panel_d", 1440, 190, 440, 770, 0, st.get("panel"))
    b.x.append('<widget name="cats" %s font="%s" itemHeight="%d" scrollbarMode="showOnDemand" '
               'transparent="1" foregroundColor="%s" foregroundColorSelected="#FFFFFF" '
               'backgroundColorSelected="#55%s" zPosition="2" />\n'
               % (b.m.rect(54, 206, 352, 738), b.m.font(25), b.m.S(52), st["text"], st["accent"][1:]))
    b.lab("title", ROW_X, 192, 400, 58, 34, st["accent"])
    b.box("search", 840, 194, 560, 54, 1, st.get("row"))
    b.lab("search", 876, 196, 490, 50, 23, st["muted"])
    for i in range(ROWS_PER_PAGE):
        x, y = row_xy(i)
        b.wbox("cbg%d" % i, "row", x, y, ROW_W, ROW_H, 1, st.get("row"))
        b.icon("ci%d" % i, x + 14, y + 12, 52, 52)
        b.lab("cn%d" % i, x + 80, y, 320, ROW_H, 27, st["text"])
        b.lab("cd%d" % i, x + 408, y, 262, ROW_H, 19, st["muted"])
        b.lab("cv%d" % i, x + 676, y, 90, ROW_H, 21, st["muted"], "right")
        b.wbox("cp%d" % i, "pill", x + 776, y + 18, 150, 40, 2, st["accent"])
        b.lab("cl%d" % i, x + 776, y + 18, 150, 40, 20, st["pilltext"], "center")
    b.wbox("sel", "row_sel", ROW_X - 12, ROW_Y - 12, 964, 100, 0 if b.flat else 5, st["accent"])
    b.lab("status", ROW_X, 400, ROW_W, 200, 30, st["muted"], "center")
    b.lab("pager", ROW_X, 934, ROW_W, 34, 22, st["soft"], "center")
    # details
    b.icon("di", 1600, 206, 120, 120)
    b.lab("dn", 1456, 332, 408, 44, 30, st["text"], "center")
    b.lab("dd", 1456, 376, 408, 52, 20, st["muted"], "center", valign="top")
    for nm, yy, h, size, col, al in (("dpt", 442, 30, 22, st["accent"], "left"),
                                     ("dp", 472, 50, 18, st["soft"], "left"),
                                     ("dct", 526, 30, 22, st["accent"], "left"),
                                     ("dc", 556, 40, 20, st["soft"], "left"),
                                     ("drt", 612, 30, 22, st["accent"], "left"),
                                     ("dr", 642, 40, 20, st["soft"], "left")):
        b.lab(nm, 1456, yy, 408, h, size, col, al, valign="top" if nm in ("dp", "dc", "dr") else "center")
    for j, nm in enumerate(("green", "red", "blue")):
        yy = 744 + j * 68
        b.box("wpill_" + nm, 1464, yy, 388, 50, 2,
              {"green": st["accent"], "red": "#B3303A", "blue": "#3B4A63"}[nm])
        b.lab("db%d" % j, 1464, yy, 388, 50, 24, st["pilltext"] if nm == "green" else "#FFFFFF", "center")
    b.footer()
    return b.done()


# ------------------------------------------------------------ public entry points
def skin_main():
    return _rows_main() if uses_rows() else _glass_main()


def skin_list(name):
    return _rows_list(name) if uses_rows() else _glass_list(name)


def skin_text(name):
    return _rows_text(name) if uses_rows() else _glass_text(name)


def skin_store(name):
    return _rows_store(name) if uses_rows() else _glass_store(name)


def store_geometry():
    """(columns, per-page, xy(i)) for the active design."""
    if uses_rows():
        return 1, ROWS_PER_PAGE, row_xy, (-12, -12)
    return STORE_COLS, STORE_COLS * STORE_ROWS, card_xy, (-21, -17)
