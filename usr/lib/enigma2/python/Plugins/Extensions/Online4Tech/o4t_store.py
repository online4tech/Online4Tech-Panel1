# -*- coding: utf-8 -*-
from __future__ import print_function
import os, sys, json, time, socket, ssl
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from enigma import eListboxPythonMultiContent, gFont, getDesktop, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eTimer
from Tools.LoadPixmap import LoadPixmap

# توافق Python 2.7 و Python 3.x للاتصال بالإنترنت
PY3 = sys.version_info[0] >= 3
if PY3:
    import urllib.request as urlreq
else:
    import urllib2 as urlreq

PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech"
ICONS_PATH = os.path.join(PLUGIN_PATH, "icons")
DB_URL = "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/o4t_database.json"
CACHE_FILE = "/tmp/o4t_database.json"

def to_str(val):
    if val is None:
        return ""
    if not PY3 and isinstance(val, unicode):
        return val.encode("utf-8")
    return str(val)

def guess_icon(sec_name):
    s = to_str(sec_name).lower()
    if "plugin" in s or "novaler" in s: return "plugins"
    if "channel" in s or "sat" in s: return "channels"
    if "cam" in s or "emu" in s or "oscam" in s: return "cams"
    if "feed" in s or "update" in s: return "feeds"
    if "picon" in s: return "picons"
    if "skin" in s: return "skins"
    if "panel" in s: return "panels"
    if "boot" in s or "spinner" in s or "image" in s: return "display"
    if "tool" in s or "system" in s or "setting" in s: return "tools"
    return "default"

class O4TCardList(MenuList):
    def __init__(self, items, is_fhd=True):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(76 if is_fhd else 54)
        self.l.setFont(0, gFont("Regular", 24 if is_fhd else 18))
        self.l.setFont(1, gFont("Regular", 19 if is_fhd else 14))

class O4TGridRows(MenuList):
    def __init__(self, items, is_fhd=True):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(255 if is_fhd else 172)
        self.l.setFont(0, gFont("Regular", 24 if is_fhd else 18))
        self.l.setFont(1, gFont("Regular", 19 if is_fhd else 14))

class O4TSideList(MenuList):
    def __init__(self, items, is_fhd=True):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(52 if is_fhd else 38)
        self.l.setFont(0, gFont("Regular", 22 if is_fhd else 16))

SKIN_FHD = """
<screen name="Online4TechStoreScreen" position="0,0" size="1920,1080" title="Online4Tech Panel" flags="wfNoBorder" backgroundColor="#0b0d12">
    <eLabel zPosition="1" position="0,0" size="1920,115" backgroundColor="#0f1218" />
    <eLabel zPosition="2" position="0,114" size="1920,2" backgroundColor="#d4af37" />

    <widget zPosition="3" name="clock_lbl" position="55,12" size="260,48" font="Regular;40" foregroundColor="#ffffff" backgroundColor="#0f1218" transparent="1" halign="center" />
    <widget zPosition="3" name="date_lbl" position="55,60" size="260,26" font="Regular;18" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />
    <widget zPosition="3" name="net_lbl" position="55,86" size="260,24" font="Regular;16" foregroundColor="#22c55e" backgroundColor="#0f1218" transparent="1" halign="center" />

    <eLabel zPosition="2" position="460,26" size="960,60" backgroundColor="#161922" />
    <widget zPosition="3" name="center_header" position="480,26" size="920,60" font="Regular;24" foregroundColor="#f5d061" backgroundColor="#161922" transparent="1" halign="center" valign="center" />

    <eLabel zPosition="3" text="Online4TechPanel" position="1480,16" size="390,46" font="Regular;34" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="center" />
    <eLabel zPosition="3" text="Online4Tech | v7.5 Universal" position="1480,66" size="390,28" font="Regular;19" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />

    <widget zPosition="1" name="left_bg" position="40,145" size="380,820" backgroundColor="#11141c" />
    <widget zPosition="3" name="left_title" position="55,165" size="350,38" font="Regular;24" foregroundColor="#f5d061" backgroundColor="#11141c" transparent="1" halign="center" />
    <widget zPosition="2" name="left_line" position="65,212" size="330,1" backgroundColor="#262b38" />
    <widget zPosition="3" name="left_info" position="60,230" size="340,710" font="Regular;20" foregroundColor="#cbd5e1" backgroundColor="#11141c" transparent="1" halign="center" />

    <widget zPosition="3" name="page_info" position="460,128" size="320,32" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="left" />
    <widget zPosition="3" name="section_heading" position="920,124" size="500,38" font="Regular;28" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="right" />
    <widget zPosition="3" name="list" position="460,170" size="960,795" backgroundColor="#0b0d12" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

    <widget zPosition="1" name="right_bg" position="1460,145" size="420,820" backgroundColor="#11141c" />
    <widget zPosition="3" name="right_header" position="1480,165" size="380,36" font="Regular;22" foregroundColor="#f5d061" backgroundColor="#11141c" transparent="1" halign="center" />
    <widget zPosition="2" name="right_line" position="1480,210" size="380,1" backgroundColor="#262b38" />
    <widget zPosition="3" name="side_list" position="1475,225" size="390,720" backgroundColor="#11141c" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

    <widget zPosition="3" name="grid_list" position="55,165" size="1810,780" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

    <eLabel zPosition="1" position="0,990" size="1920,90" backgroundColor="#0f1218" />
    <eLabel zPosition="2" position="0,990" size="1920,2" backgroundColor="#1e222d" />

    <eLabel zPosition="3" position="1830,1022" size="22,22" backgroundColor="#ef4444" />
    <widget zPosition="3" name="key_red" position="1640,1015" size="180,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

    <eLabel zPosition="3" position="1560,1022" size="22,22" backgroundColor="#22c55e" />
    <widget zPosition="3" name="key_green" position="1340,1015" size="210,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

    <eLabel zPosition="3" position="1260,1022" size="22,22" backgroundColor="#eab308" />
    <widget zPosition="3" name="key_yellow" position="960,1015" size="290,36" font="Regular;22" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="right" />

    <eLabel zPosition="3" position="880,1022" size="22,22" backgroundColor="#3b82f6" />
    <widget zPosition="3" name="key_blue" position="640,1015" size="230,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

    <widget zPosition="3" name="mode_badge" position="60,1015" size="520,36" font="Regular;21" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="left" />
</screen>
"""

SKIN_HD = """
<screen name="Online4TechStoreScreen" position="0,0" size="1280,720" title="Online4Tech Panel" flags="wfNoBorder" backgroundColor="#0b0d12">
    <eLabel zPosition="1" position="0,0" size="1280,76" backgroundColor="#0f1218" />
    <eLabel zPosition="2" position="0,75" size="1280,2" backgroundColor="#d4af37" />

    <widget zPosition="3" name="clock_lbl" position="25,8" size="190,32" font="Regular;26" foregroundColor="#ffffff" backgroundColor="#0f1218" transparent="1" halign="center" />
    <widget zPosition="3" name="date_lbl" position="25,40" size="190,18" font="Regular;13" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />
    <widget zPosition="3" name="net_lbl" position="25,58" size="190,16" font="Regular;12" foregroundColor="#22c55e" backgroundColor="#0f1218" transparent="1" halign="center" />

    <eLabel zPosition="2" position="300,18" size="650,40" backgroundColor="#161922" />
    <widget zPosition="3" name="center_header" position="310,18" size="630,40" font="Regular;18" foregroundColor="#f5d061" backgroundColor="#161922" transparent="1" halign="center" valign="center" />

    <eLabel zPosition="3" text="Online4TechPanel" position="980,10" size="280,32" font="Regular;24" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="center" />
    <eLabel zPosition="3" text="Online4Tech | v7.5 Universal" position="980,44" size="280,22" font="Regular;14" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />

    <widget zPosition="1" name="left_bg" position="20,92" size="255,555" backgroundColor="#11141c" />
    <widget zPosition="3" name="left_title" position="30,102" size="235,28" font="Regular;18" foregroundColor="#f5d061" backgroundColor="#11141c" transparent="1" halign="center" />
    <widget zPosition="2" name="left_line" position="35,134" size="225,1" backgroundColor="#262b38" />
    <widget zPosition="3" name="left_info" position="30,145" size="235,490" font="Regular;14" foregroundColor="#cbd5e1" backgroundColor="#11141c" transparent="1" halign="center" />

    <widget zPosition="3" name="page_info" position="295,84" size="220,24" font="Regular;15" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="left" />
    <widget zPosition="3" name="section_heading" position="620,82" size="340,28" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="right" />
    <widget zPosition="3" name="list" position="295,112" size="665,535" backgroundColor="#0b0d12" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

    <widget zPosition="1" name="right_bg" position="980,92" size="280,555" backgroundColor="#11141c" />
    <widget zPosition="3" name="right_header" position="990,102" size="260,28" font="Regular;17" foregroundColor="#f5d061" backgroundColor="#11141c" transparent="1" halign="center" />
    <widget zPosition="2" name="right_line" position="995,134" size="250,1" backgroundColor="#262b38" />
    <widget zPosition="3" name="side_list" position="988,142" size="264,495" backgroundColor="#11141c" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

    <widget zPosition="3" name="grid_list" position="30,105" size="1220,535" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

    <eLabel zPosition="1" position="0,660" size="1280,60" backgroundColor="#0f1218" />
    <eLabel zPosition="2" position="0,660" size="1280,2" backgroundColor="#1e222d" />

    <eLabel zPosition="3" position="1225,682" size="16,16" backgroundColor="#ef4444" />
    <widget zPosition="3" name="key_red" position="1100,676" size="115,28" font="Regular;15" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

    <eLabel zPosition="3" position="1050,682" size="16,16" backgroundColor="#22c55e" />
    <widget zPosition="3" name="key_green" position="910,676" size="130,28" font="Regular;15" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

    <eLabel zPosition="3" position="860,682" size="16,16" backgroundColor="#eab308" />
    <widget zPosition="3" name="key_yellow" position="660,676" size="190,28" font="Regular;15" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="right" />

    <eLabel zPosition="3" position="610,682" size="16,16" backgroundColor="#3b82f6" />
    <widget zPosition="3" name="key_blue" position="460,676" size="140,28" font="Regular;15" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

    <widget zPosition="3" name="mode_badge" position="30,676" size="380,28" font="Regular;15" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="left" />
</screen>
"""

class Online4TechStoreScreen(Screen):
    def __init__(self, session):
        desktop_w = getDesktop(0).size().width()
        self.is_fhd = (desktop_w >= 1600)
        self.skin = SKIN_FHD if self.is_fhd else SKIN_HD
        Screen.__init__(self, session)

        self["clock_lbl"] = Label("")
        self["date_lbl"] = Label("")
        self["net_lbl"] = Label("NET: ONLINE")
        self["center_header"] = Label("متجر أونلاين تكنولوجي الشامل (اضغط 0 للبحث)")
        self["left_bg"] = Label("")
        self["left_title"] = Label("النظام")
        self["left_line"] = Label("")
        self["left_info"] = Label("")
        self["page_info"] = Label("")
        self["section_heading"] = Label("الأقسام الرئيسية")
        self["right_bg"] = Label("")
        self["right_header"] = Label("الأقسام")
        self["right_line"] = Label("")

        self["key_red"] = Label("خروج")
        self["key_green"] = Label("تثبيت / فتح")
        self["key_yellow"] = Label("عرض شبكة 4x3")
        self["key_blue"] = Label("تحديث السيرفر")
        self["mode_badge"] = Label("0: بحث سريع  |  أصفر: شبكة 4x3")

        self["list"] = O4TCardList([], self.is_fhd)
        self["side_list"] = O4TSideList([], self.is_fhd)
        self["grid_list"] = O4TGridRows([], self.is_fhd)

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "NumberActions"], {
            "ok": self.ok_pressed,
            "cancel": self.back_pressed,
            "red": self.back_pressed,
            "green": self.ok_pressed,
            "yellow": self.toggle_view_mode,
            "blue": self.refresh_server,
            "0": self.open_search,
            "up": self.move_up,
            "down": self.move_down,
            "left": self.move_left,
            "right": self.move_right,
        }, -1)

        self.db = {}
        self.mode = "main"
        self.view_style = "list"
        self.current_items = []
        self.grid_index = 0
        self.timer = eTimer()
        self.timer.callback.append(self.update_clock)
        self.onLayoutFinish.append(self.startup)

    def update_clock(self):
        self["clock_lbl"].setText(time.strftime("%H:%M"))
        self["date_lbl"].setText(time.strftime("%A %d %B"))

    def detect_image_name(self):
        for p in ["/etc/issue", "/etc/image-version"]:
            if os.path.exists(p):
                try:
                    txt = open(p, "r").read().splitlines()[0].replace("\\n", "").replace("\\l", "").strip()
                    if txt:
                        return txt[:22]
                except Exception:
                    pass
        return "Enigma2 Image"

    def get_sys_info_text(self):
        lines = []
        try:
            model = "Enigma2 Box"
            if os.path.exists("/proc/stb/info/vumodel"):
                model = "Vu+ " + open("/proc/stb/info/vumodel").read().strip().upper()
            elif os.path.exists("/proc/stb/info/boxtype"):
                model = open("/proc/stb/info/boxtype").read().strip().upper()
            lines.append("Box: " + model)
            lines.append("Image: " + self.detect_image_name())
            lines.append("Python: %d.%d.%d" % sys.version_info[:3])
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                lines.append("IP: " + ip)
                self["net_lbl"].setText("NET: ONLINE")
            except Exception:
                lines.append("IP: Local")
                self["net_lbl"].setText("NET: LOCAL")
            st = os.statvfs("/")
            free_gb = (st.f_bavail * st.f_frsize) / (1024.0 ** 3)
            tot_gb = (st.f_blocks * st.f_frsize) / (1024.0 ** 3)
            lines.append("Flash: %.1fGB / %.1fGB" % (free_gb, tot_gb))
            if os.path.exists("/proc/meminfo"):
                mem = open("/proc/meminfo").read()
                tot_m = int([x for x in mem.splitlines() if "MemTotal" in x][0].split()[1]) // 1024
                avl_m = int([x for x in mem.splitlines() if "MemAvailable" in x][0].split()[1]) // 1024
                lines.append("Ram: %dMB / %dMB" % (tot_m - avl_m, tot_m))
        except Exception:
            pass
        return "\n\n".join(lines)

    def startup(self):
        self.update_clock()
        self.timer.start(10000)
        self.apply_view_visibility()
        self.load_database(force=False)

    def apply_view_visibility(self):
        is_grid = (self.view_style == "grid")
        for w in ["left_bg", "left_title", "left_line", "left_info", "page_info", "section_heading", "list", "right_bg", "right_header", "right_line", "side_list"]:
            if is_grid:
                self[w].hide()
            else:
                self[w].show()
        if is_grid:
            self["grid_list"].show()
            self["key_yellow"].setText("عرض قائمة")
            self["mode_badge"].setText("وضع الشبكة 4x3  |  أصفر للقائمة")
        else:
            self["grid_list"].hide()
            self["key_yellow"].setText("عرض شبكة 4x3")
            self["mode_badge"].setText("0: بحث سريع  |  أصفر: شبكة 4x3")

    def toggle_view_mode(self):
        if self.view_style == "list":
            self.grid_index = self["list"].getSelectedIndex()
            self.view_style = "grid"
        else:
            self.view_style = "list"
        self.apply_view_visibility()
        self.render_current_items()

    def load_database(self, force=False):
        try:
            if force or not os.path.exists(CACHE_FILE):
                if PY3:
                    ctx = ssl._create_unverified_context()
                    req = urlreq.urlopen(DB_URL, context=ctx, timeout=15)
                else:
                    req = urlreq.urlopen(DB_URL, timeout=15)
                raw = req.read().decode("utf-8")
                with open(CACHE_FILE, "wb") as f:
                    f.write(raw.encode("utf-8"))
            else:
                with open(CACHE_FILE, "rb") as f:
                    raw = f.read().decode("utf-8")
            self.db = json.loads(raw)
            self.show_main()
        except Exception as e:
            self["center_header"].setText("Error: " + str(e))

    def get_icon_pix(self, icon_key):
        ic_file = os.path.join(ICONS_PATH, "ic_%s.png" % icon_key)
        if not os.path.exists(ic_file):
            ic_file = os.path.join(ICONS_PATH, "ic_default.png")
        return LoadPixmap(ic_file) if os.path.exists(ic_file) else None

    def make_side_entry(self, label, data):
        w = 385 if self.is_fhd else 260
        h = 46 if self.is_fhd else 34
        return [
            data,
            (eListboxPythonMultiContent.TYPE_TEXT, 8, 3, w - 16, h, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, to_str(label), 0x00cbd5e1, 0x00f5d061)
        ]

    def make_list_card(self, title, subtitle, badge, icon_key, is_installed, data):
        ic_pix = self.get_icon_pix(icon_key)
        res = [data]
        if self.is_fhd:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 5, 4, 950, 68, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "", 0x00161922, 0x00262012, 0x00161922, 0x00262012))
            if ic_pix:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 875, 6, 64, 64, ic_pix))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 440, 12, 415, 52, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, to_str(title), 0x00ffffff, 0x00f5d061))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 140, 12, 285, 52, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, to_str(subtitle), 0x00cbd5e1, 0x00ffffff))
            if is_installed:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 20, 18, 105, 40, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "مثبت", 0x00ff5555, 0x00ff8888))
            elif badge:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 20, 18, 105, 40, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, to_str(badge), 0x00f5d061, 0x00ffffff))
        else:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 4, 3, 656, 48, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "", 0x00161922, 0x00262012, 0x00161922, 0x00262012))
            if ic_pix:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 604, 5, 44, 44, ic_pix))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 310, 8, 280, 38, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, to_str(title), 0x00ffffff, 0x00f5d061))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 95, 8, 205, 38, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, to_str(subtitle), 0x00cbd5e1, 0x00ffffff))
            if is_installed:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 14, 11, 75, 32, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "مثبت", 0x00ff5555, 0x00ff8888))
            elif badge:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 14, 11, 75, 32, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, to_str(badge), 0x00f5d061, 0x00ffffff))
        return res

    def build_grid_rows(self):
        cols = 4
        col_x = [1365, 915, 465, 15] if self.is_fhd else [920, 615, 310, 5]
        cw = 430 if self.is_fhd else 295
        ch = 235 if self.is_fhd else 160
        rows = []
        total = len(self.current_items)
        for r_start in range(0, total, cols):
            row_entries = [r_start]
            for c in range(cols):
                idx = r_start + c
                if idx >= total:
                    break
                entry = self.current_items[idx]
                x0 = col_x[c]
                is_selected = (idx == self.grid_index)
                bg_col = 0x00262012 if is_selected else 0x00161922
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0, 6, cw, ch, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "", bg_col, bg_col, bg_col, bg_col))
                ic_pix = self.get_icon_pix(entry["icon"])
                if ic_pix and self.is_fhd:
                    row_entries.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x0 + 345, 22, 64, 64, ic_pix))
                t_col = 0x00f5d061 if is_selected else 0x00ffffff
                if self.is_fhd:
                    row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 24, 310, 60, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, to_str(entry["title"]), t_col, t_col))
                    row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 100, 390, 85, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, to_str(entry["subtitle"]), 0x00cbd5e1, 0x00ffffff))
                else:
                    row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 12, 14, 270, 44, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, to_str(entry["title"]), t_col, t_col))
                    row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 12, 68, 270, 65, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, to_str(entry["subtitle"]), 0x00cbd5e1, 0x00ffffff))
            rows.append(row_entries)
        self["grid_list"].setList(rows)
        if rows:
            self["grid_list"].moveToIndex(self.grid_index // cols)

    def render_current_items(self):
        if self.view_style == "grid":
            self.build_grid_rows()
        else:
            cards = []
            for entry in self.current_items:
                cards.append(self.make_list_card(entry["title"], entry["subtitle"], entry["badge"], entry["icon"], entry["installed"], entry["data"]))
            self["list"].setList(cards)
            if cards and self.grid_index < len(cards):
                self["list"].moveToIndex(self.grid_index)

    def show_main(self):
        self.mode = "main"
        self.grid_index = 0
        self["key_red"].setText("خروج")
        self["section_heading"].setText("الأقسام الرئيسية")
        self["left_title"].setText("النظام")
        self["left_info"].setText(self.get_sys_info_text())

        cats = self.db.get("main", [])
        self.current_items = []
        side_items = []
        for item in cats:
            sec = item.get("section", "")
            raw_title = item.get("name", "") or item.get("title", "") or sec
            cnt = len(self.db.get(sec, []))
            ic_key = guess_icon(sec + " " + raw_title)
            self.current_items.append({
                "title": raw_title,
                "subtitle": "%d حزمة متاحة" % cnt,
                "badge": "(%d)" % cnt,
                "icon": ic_key,
                "installed": False,
                "data": item
            })
            side_items.append(self.make_side_entry("%s  (%d)" % (raw_title, cnt), item))

        self["side_list"].setList(side_items)
        self["page_info"].setText("%d قسم" % len(self.current_items))
        self.render_current_items()

    def show_section(self, sec_key, sec_name):
        self.mode = "section"
        self.grid_index = 0
        self["key_red"].setText("رجوع")
        self["section_heading"].setText(to_str(sec_name))
        self["left_title"].setText("تفاصيل العنصر")
        ic_key = guess_icon(sec_key + " " + sec_name)

        items = self.db.get(sec_key, [])
        self.current_items = []
        for item in items:
            name = item.get("name", "") or item.get("title", "Package")
            path = item.get("path", "")
            inst = bool(path and os.path.exists(path))
            self.current_items.append({
                "title": name,
                "subtitle": "Online4Tech Official",
                "badge": "",
                "icon": ic_key,
                "installed": inst,
                "data": item
            })

        self["page_info"].setText("%d حزمة" % len(self.current_items))
        self.render_current_items()
        self.update_left_detail()

    def open_search(self):
        self.session.openWithCallback(self.run_search, VirtualKeyBoard, title="ابحث عن بلجن أو باقة في Online4Tech:", text="")

    def run_search(self, keyword):
        if not keyword:
            return
        kw = to_str(keyword).lower().strip()
        self.mode = "section"
        self.grid_index = 0
        self["key_red"].setText("رجوع")
        self["section_heading"].setText("نتائج البحث: " + keyword)
        self["left_title"].setText("تفاصيل العنصر")
        self.current_items = []
        for cat in self.db.get("main", []):
            sec = cat.get("section", "")
            for item in self.db.get(sec, []):
                name = to_str(item.get("name", ""))
                if kw in name.lower():
                    path = item.get("path", "")
                    inst = bool(path and os.path.exists(path))
                    self.current_items.append({
                        "title": name,
                        "subtitle": sec,
                        "badge": "",
                        "icon": guess_icon(sec),
                        "installed": inst,
                        "data": item
                    })
        self["page_info"].setText("%d نتيجة" % len(self.current_items))
        self.render_current_items()
        self.update_left_detail()

    def update_left_detail(self):
        if self.mode != "section" or not self.current_items:
            return
        idx = self.grid_index if self.view_style == "grid" else self["list"].getSelectedIndex()
        if idx < 0 or idx >= len(self.current_items):
            return
        data = self.current_items[idx]["data"]
        name = to_str(data.get("name", "") or data.get("title", ""))
        path = data.get("path", "")
        inst = "مثبت" if (path and os.path.exists(path)) else "غير مثبت"
        txt = "%s\n\nالحالة: %s\n\nالمصدر:\nOnline4Tech Official" % (name, inst)
        self["left_info"].setText(txt)

    def move_up(self):
        if self.view_style == "grid":
            if self.grid_index >= 4:
                self.grid_index -= 4
                self.build_grid_rows()
        else:
            self["list"].up()
            self.grid_index = self["list"].getSelectedIndex()
            if self.mode == "main":
                self["side_list"].moveToIndex(self.grid_index)
            else:
                self.update_left_detail()

    def move_down(self):
        if self.view_style == "grid":
            if self.grid_index + 4 < len(self.current_items):
                self.grid_index += 4
                self.build_grid_rows()
        else:
            self["list"].down()
            self.grid_index = self["list"].getSelectedIndex()
            if self.mode == "main":
                self["side_list"].moveToIndex(self.grid_index)
            else:
                self.update_left_detail()

    def move_left(self):
        if self.view_style == "grid" and self.grid_index + 1 < len(self.current_items):
            self.grid_index += 1
            self.build_grid_rows()

    def move_right(self):
        if self.view_style == "grid" and self.grid_index > 0:
            self.grid_index -= 1
            self.build_grid_rows()

    def ok_pressed(self):
        if not self.current_items:
            return
        idx = self.grid_index if self.view_style == "grid" else self["list"].getSelectedIndex()
        if idx < 0 or idx >= len(self.current_items):
            return
        data = self.current_items[idx]["data"]
        if self.mode == "main":
            sec = data.get("section", "")
            title = data.get("name", "") or data.get("title", "") or sec
            self.show_section(sec, title)
        else:
            cmd = data.get("cmd", "")
            if cmd:
                self.session.open(Console, title="Online4Tech: " + to_str(data.get("name", "") or "Install"), cmdlist=[to_str(cmd)])

    def refresh_server(self):
        self["center_header"].setText("جاري تحديث قاعدة البيانات...")
        self.load_database(force=True)
        self["center_header"].setText("متجر أونلاين تكنولوجي الشامل (اضغط 0 للبحث)")

    def back_pressed(self):
        if self.mode == "section":
            self.show_main()
        else:
            self.timer.stop()
            self.close()