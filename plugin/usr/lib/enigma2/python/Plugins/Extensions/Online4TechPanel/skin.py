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


def _header(m, title_size=46):
    return (
        '<ePixmap pixmap="%s" position="0,0" size="%d,%d" zPosition="-5" />\n'
        '<widget name="title" %s font="%s" foregroundColor="%s" transparent="1" '
        'halign="left" valign="center" zPosition="3" />\n'
        '<widget name="slogan" %s font="%s" foregroundColor="%s" transparent="1" '
        'halign="left" valign="center" zPosition="3" />\n'
        '<widget source="global.CurrentTime" render="Label" %s font="%s" '
        'foregroundColor="%s" transparent="1" halign="right" valign="center" zPosition="3">'
        '<convert type="ClockToText">Format:%%H:%%M</convert></widget>\n'
        % (m.pix("bg"), m.W, m.H,
           m.rect(80, 36, 1000, 64), m.font(title_size), TEXT,
           m.rect(80, 94, 1000, 36), m.font(26), accent(),
           m.rect(1560, 40, 280, 64), m.font(44), TEXT))


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
    MAIN_POS.append((180 + (_i % 4) * 400, 240 + (_i // 4) * 340))


def skin_main():
    m = metrics()
    x = [_screen_open(m, "O4TMain"), _header(m, 54)]
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
             % (m.rect(180, 896, 1560, 56), m.font(28), SOFT))
    x.append(_footer(m))
    x.append("</screen>")
    return "".join(x)


def skin_list(name):
    m = metrics()
    x = [_screen_open(m, name), _header(m)]
    x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="0" />\n'
             % (m.pix("panel_l"), m.rect(80, 140, 1060, 790)))
    x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="0" />\n'
             % (m.pix("panel_r"), m.rect(1170, 140, 670, 790)))
    x.append('<widget name="list" %s font="%s" itemHeight="%d" scrollbarMode="showOnDemand" '
             'transparent="1" foregroundColor="%s" foregroundColorSelected="#FFFFFF" '
             'backgroundColorSelected="#44%s" zPosition="2" />\n'
             % (m.rect(106, 166, 1008, 738), m.font(30), m.S(54), TEXT, accent()[1:]))
    x.append('<widget name="status" %s font="%s" foregroundColor="%s" transparent="1" '
             'halign="center" valign="center" zPosition="3" />\n'
             % (m.rect(106, 166, 1008, 738), m.font(32), MUTED))
    x.append('<widget name="detail" %s font="%s" foregroundColor="%s" transparent="1" '
             'scrollbarMode="showOnDemand" zPosition="2" />\n'
             % (m.rect(1200, 170, 610, 730), m.font(27), SOFT))
    x.append(_footer(m))
    x.append("</screen>")
    return "".join(x)


def skin_text(name):
    m = metrics()
    x = [_screen_open(m, name), _header(m)]
    x.append('<ePixmap pixmap="%s" %s alphatest="blend" zPosition="0" />\n'
             % (m.pix("panel_f"), m.rect(80, 140, 1760, 790)))
    x.append('<widget name="detail" %s font="%s" foregroundColor="%s" transparent="1" '
             'scrollbarMode="showOnDemand" zPosition="2" />\n'
             % (m.rect(120, 175, 1680, 720), m.font(30), SOFT))
    x.append(_footer(m))
    x.append("</screen>")
    return "".join(x)
