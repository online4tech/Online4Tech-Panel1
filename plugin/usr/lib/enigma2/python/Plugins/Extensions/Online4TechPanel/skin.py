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
        self.dir = os.path.join(PLUGIN_DIR, "assets", self.assets)

    def S(self, v):
        return int(round(v * self.k))

    def pos(self, x, y):
        return "%d,%d" % (self.S(x), self.S(y))

    def size(self, w, h):
        return "%d,%d" % (self.S(w), self.S(h))

    def rect(self, x, y, w, h):
        return 'position="%s" size="%s"' % (self.pos(x, y), self.size(w, h))

    def font(self, n):
        return "Regular;%d" % self.S(n)

    def pix(self, name):
        return os.path.join(self.dir, name + ".png")


def metrics():
    if "m" not in _cache:
        _cache["m"] = Metrics()
    return _cache["m"]


# ---------------------------------------------------------------- pieces
def _screen_open(m, name):
    return ('<screen name="%s" position="center,center" size="%d,%d" title="Online4Tech Panel" '
            'flags="wfNoBorder" backgroundColor="#000A1020">\n' % (name, m.W, m.H))


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
    MAIN_POS.append((180 + (_i % 4) * 400, 215 + (_i // 4) * 330))


def skin_main():
    m = metrics()
    x = [_screen_open(m, "O4TMain"), _header(m)]
    for i, (tx, ty) in enumerate(MAIN_POS):
        x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="1" />\n'
                 % (m.pix("tile"), m.rect(tx, ty, 360, 300)))
        x.append('<widget name="ic%d" %s alphatest="blend" zPosition="3" />\n'
                 % (i, m.rect(tx + 116, ty + 36, 128, 128)))
        x.append('<widget name="tt%d" %s font="%s" foregroundColor="%s" transparent="1" '
                 'halign="center" valign="center" zPosition="3" />\n'
                 % (i, m.rect(tx + 10, ty + 184, 340, 48), m.font(36), TEXT))
        x.append('<widget name="ts%d" %s font="%s" foregroundColor="%s" transparent="1" '
                 'halign="center" valign="center" zPosition="3" />\n'
                 % (i, m.rect(tx + 10, ty + 234, 340, 36), m.font(23), MUTED))
    x.append('<widget name="sel" pixmap="%s" %s alphatest="blend" zPosition="2" />\n'
             % (m.pix("sel_" + theme()), m.rect(MAIN_POS[0][0] - 16, MAIN_POS[0][1] - 16, 392, 332)))
    x.append('<widget name="hint" %s font="%s" foregroundColor="%s" transparent="1" '
             'halign="center" valign="center" zPosition="3" />\n'
             % (m.rect(180, 880, 1560, 56), m.font(28), SOFT))
    x.append(_footer(m))
    x.append("</screen>")
    return "".join(x)


def skin_list(name):
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


def skin_text(name):
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


def skin_store(name):
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
    lab("dc", 1464, 556, 416, 72, 17, SOFT, "left", valign="top")
    lab("drt", 1464, 632, 416, 30, 22, accent(), "left")
    lab("dr", 1464, 662, 416, 54, 17, SOFT, "left", valign="top")
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
