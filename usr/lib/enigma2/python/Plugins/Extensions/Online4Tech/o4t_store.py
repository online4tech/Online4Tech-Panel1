# -*- coding: utf-8 -*-
from __future__ import print_function
import os, sys, json, time, socket, ssl
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from enigma import eListboxPythonMultiContent, gFont, getDesktop, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eTimer
from Tools.LoadPixmap import LoadPixmap

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

# قاموس تعريب شامل وأوصاف دقيقة لجميع الأقسام
CAT_INFO = [
    ("online4tech", "حصريات أونلاين تكنولوجي", "إضافات وملفات حصرية لمتجر Online4Tech", "default"),
    ("fav",         "المفضلة",                 "الإضافات والبلاجينات الأكثر استخداما", "default"),
    ("depend",      "تحديث المكتبات",          "تحديث مكتبات البايثون ومشغلات النظام", "tools"),
    ("backup",      "صور الباك اب",            "تحميل وتثبيت صور انيجما 2", "display"),
    ("panel",       "البانلات",                "استكشف بانلات انيجما 2 مع روابط المطورين", "panels"),
    ("novaler",     "أجهزة نوفالر",            "بلاجينات وأدوات خاصة لأجهزة نوفالر", "plugins"),
    ("plugin",      "الإضافات",                "إدارة وتثبيت البلاجينات المنوعة", "plugins"),
    ("channel",     "ملفات القنوات",           "تحديث وتثبيت أحدث ملفات القنوات", "channels"),
    ("feed",        "الفيدات",                 "تحديث وتثبيت الفيدات", "feeds"),
    ("bootlogo",    "شعارات الإقلاع",          "تغيير شعارات الإقلاع وأيقونات التحميل", "display"),
    ("spinner",     "أيقونات التحميل",         "تغيير شعار التحميل الدوار (Spinner)", "display"),
    ("cam",         "السوفتكامات",             "إدارة وتثبيت إيموهات التشفير", "cams"),
    ("emu",         "السوفتكامات",             "إدارة وتثبيت إيموهات التشفير", "cams"),
    ("picon",       "البيكونات",               "تثبيت وإدارة شعارات القنوات", "picons"),
    ("skin",        "السكينات",                "اختيار وتطبيق السكينات", "skins"),
    ("media",       "الميديا و IPTV",          "مشغلات الميديا والصوتيات والآي بي تي في", "plugins"),
    ("iptv",        "آي بي تي في",             "إضافات ومشغلات القنوات عبر الإنترنت", "plugins"),
    ("sport",       "الرياضة",                 "جداول المباريات والقنوات الرياضية", "plugins"),
    ("quran",       "القرآن الكريم",           "تطبيقات وإذاعات القرآن الكريم", "plugins"),
    ("islamic",     "إسلاميات",                "تطبيقات القرآن الكريم ومواقيت الصلاة", "plugins"),
    ("epg",         "دليل البرامج",            "مصادر وإضافات دليل البرامج الإلكتروني", "feeds"),
    ("tool",        "الأدوات",                 "أدوات وإضافات خدمية مفيدة", "tools"),
    ("system",      "خدمات النظام",            "إعدادات وأوامر صيانة الرسيفر", "tools"),
    ("setting",     "الإعدادات",               "ضبط إعدادات الرسيفر والشبكة", "tools"),
]

def resolve_cat_meta(raw_name, sec_key, cnt):
    combined = (to_str(raw_name) + " " + to_str(sec_key)).lower()
    for key_sub, ar_title, ar_desc, ic in CAT_INFO:
        if key_sub in combined:
            return ar_title, ar_desc, ic
    clean_title = to_str(raw_name).split("(")[0].strip() or to_str(sec_key)
    return clean_title, "%d حزمة متاحة في هذا القسم" % cnt, "default"

def guess_icon(sec_name):
    _, _, ic = resolve_cat_meta(sec_name, sec_name, 0)
    return ic

class O4TCardList(MenuList):
    def __init__(self, items, is_fhd=True):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(74 if is_fhd else 52)
        self.l.setFont(0, gFont("Regular", 23 if is_fhd else 17))
        self.l.setFont(1, gFont("Regular", 18 if is_fhd else 14))

class O4TGridRows(MenuList):
    def __init__(self, items, is_fhd=True):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(250 if is_fhd else 170)
        self.l.setFont(0, gFont("Regular", 23 if is_fhd else 17))
        self.l.setFont(1, gFont("Regular", 18 if is_fhd else 14))

class O4TSideList(MenuList):
    def __init__(self, items, is_fhd=True):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(50 if is_fhd else 36)
        self.l.setFont(0, gFont("Regular", 20 if is_fhd else 15))
        self.l.setFont(1, gFont("Regular", 17 if is_fhd else 13))

SKIN_FHD = """
<screen name="Online4TechStoreScreen" position="0,0" size="1920,1080" title="Online4Tech Panel" flags="wfNoBorder" backgroundColor="#0b0d12">
    <!-- الشريط العلوي -->
    <eLabel zPosition="1" position="0,0" size="1920,115" backgroundColor="#0f1218" />
    <eLabel zPosition="2" position="0,114" size="1920,2" backgroundColor="#262b38" />

    <widget zPosition="3" name="clock_lbl" position="55,12" size="260,48" font="Regular;40" foregroundColor="#ffffff" backgroundColor="#0f1218" transparent="1" halign="center" />
    <widget zPosition="3" name="date_lbl" position="55,60" size="260,26" font="Regular;18" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />
    <widget zPosition="3" name="net_lbl" position="55,86" size="260,24" font="Regular;16" foregroundColor="#22c55e" backgroundColor="#0f1218" transparent="1" halign="center" />

    <eLabel zPosition="2" position="460,26" size="960,58" backgroundColor="#161922" />
    <widget zPosition="3" name="center_header" position="480,26" size="920,58" font="Regular;22" foregroundColor="#cbd5e1" backgroundColor="#161922" transparent="1" halign="center" valign="center" />

    <eLabel zPosition="3" text="Online4TechPanel" position="1480,16" size="390,46" font="Regular;34" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="center" />
    <eLabel zPosition="3" text="Online4Tech | الإصدار 7.5" position="1480,66" size="390,28" font="Regular;19" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />

    <!-- العمود الأيسر: النظام أو بطاقة المعاينة -->
    <widget zPosition="1" name="left_bg" position="40,165" size="380,800" backgroundColor="#11141c" />
    <widget zPosition="3" name="left_title" position="55,182" size="350,36" font="Regular;23" foregroundColor="#94a3b8" backgroundColor="#11141c" transparent="1" halign="center" />
    <widget zPosition="2" name="left_line" position="65,226" size="330,1" backgroundColor="#262b38" />
    <widget zPosition="4" name="preview_icon" position="198,250" size="64,64" alphatest="blend" />
    <widget zPosition="3" name="left_pkg_name" position="55,330" size="350,70" font="Regular;25" foregroundColor="#f5d061" backgroundColor="#11141c" transparent="1" halign="center" valign="center" />
    <widget zPosition="3" name="left_info" position="55,245" size="350,690" font="Regular;20" foregroundColor="#cbd5e1" backgroundColor="#11141c" transparent="1" halign="center" />

    <!-- العمود الأوسط: قائمة البطاقات -->
    <widget zPosition="3" name="page_info" position="465,126" size="380,34" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="left" />
    <widget zPosition="3" name="section_heading" position="860,122" size="550,38" font="Regular;28" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="right" />
    <widget zPosition="3" name="list" position="460,168" size="960,795" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

    <!-- العمود الأيمن: الفئات والأقسام -->
    <widget zPosition="1" name="right_bg" position="1460,145" size="420,820" backgroundColor="#11141c" />
    <widget zPosition="3" name="right_header" position="1480,160" size="380,34" font="Regular;21" foregroundColor="#94a3b8" backgroundColor="#11141c" transparent="1" halign="center" />
    <widget zPosition="2" name="right_line" position="1480,202" size="380,1" backgroundColor="#262b38" />
    <widget zPosition="3" name="side_list" position="1468,212" size="404,700" backgroundColor="#11141c" backgroundColorSelected="#1d222f" scrollbarMode="showNever" enableWrapAround="1" />
    <widget zPosition="3" name="side_page_lbl" position="1480,922" size="380,30" font="Regular;18" foregroundColor="#94a3b8" backgroundColor="#11141c" transparent="1" halign="right" />

    <!-- وضع الشبكة 4x3 -->
    <widget zPosition="3" name="grid_list" position="55,168" size="1810,780" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

    <!-- الشريط السفلي -->
    <eLabel zPosition="1" position="0,990" size="1920,90" backgroundColor="#0f1218" />
    <eLabel zPosition="2" position="0,990" size="1920,2" backgroundColor="#262b38" />

    <eLabel zPosition="3" position="1830,1022" size="20,20" backgroundColor="#ef4444" />
    <widget zPosition="3" name="key_red" position="1640,1015" size="180,36" font="Regular;21" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

    <eLabel zPosition="3" position="1560,1022" size="20,20" backgroundColor="#22c55e" />
    <widget zPosition="3" name="key_green" position="1340,1015" size="210,36" font="Regular;21" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

    <eLabel zPosition="3" position="1260,1022" size="20,20" backgroundColor="#eab308" />
    <widget zPosition="3" name="key_yellow" position="960,1015" size="290,36" font="Regular;21" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="right" />

    <eLabel zPosition="3" position="880,1022" size="20,20" backgroundColor="#3b82f6" />
    <widget zPosition="3" name="key_blue" position="640,1015" size="230,36" font="Regular;21" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

    <widget zPosition="3" name="mode_badge" position="60,1015" size="540,36" font="Regular;20" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="left" />
</screen>
"""

class Online4TechStoreScreen(Screen):
    def __init__(self, session):
        self.is_fhd = True
        self.skin = SKIN_FHD
        Screen.__init__(self, session)

        self["clock_lbl"] = Label("")
        self["date_lbl"] = Label("")
        self["net_lbl"] = Label("NET: ONLINE")
        self["center_header"] = Label("🔍  ابحث عن البلاجينات والإضافات وملفات القنوات (اضغط زر 0)")
        self["left_bg"] = Label("")
        self["left_title"] = Label("النظام")
        self["left_line"] = Label("")
        self["preview_icon"] = Pixmap()
        self["left_pkg_name"] = Label("")
        self["left_info"] = Label("")
        self["page_info"] = Label("")
        self["section_heading"] = Label("انيجما 2")
        self["right_bg"] = Label("")
        self["right_header"] = Label("الفئات")
        self["right_line"] = Label("")
        self["side_page_lbl"] = Label("")

        self["key_red"] = Label("خروج")
        self["key_green"] = Label("تثبيت / فتح")
        self["key_yellow"] = Label("عرض شبكة 4x3")
        self["key_blue"] = Label("تحديث السيرفر")
        self["mode_badge"] = Label("حديث | متعدد     < > الفئات     0: بحث")

        self["list"] = O4TCardList([], True)
        self["side_list"] = O4TSideList([], True)
        self["grid_list"] = O4TGridRows([], True)

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
        self.nav_stack = []
        self.view_style = "list"
        self.current_items = []
        self.main_cats_meta = []
        self.active_cat_idx = 0
        self.grid_index = 0

        self.card_norm = None
        self.card_sel = None
        self.grid_norm = None
        self.grid_sel = None
        self.pill_gold = None
        self.pill_dark = None
        self.badge_inst = None

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
        return "Enigma2"

    def get_sys_info_text(self):
        lines = []
        try:
            model = "Enigma2"
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
            lines.append("Net: Online")
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

    def get_sub_items(self, item):
        if not isinstance(item, dict):
            return None
        for k in ["items", "list", "sub", "packages", "data"]:
            if isinstance(item.get(k), list):
                return item.get(k)
        sec = item.get("section", "") or item.get("sub_section", "") or item.get("target", "")
        if sec and sec in self.db and isinstance(self.db[sec], list):
            return self.db[sec]
        return None

    def startup(self):
        for attr, fname in [
            ("card_norm", "card_norm_fhd.png"),
            ("card_sel",  "card_sel_fhd.png"),
            ("grid_norm", "grid_norm.png"),
            ("grid_sel",  "grid_sel.png"),
            ("pill_gold", "pill_gold.png"),
            ("pill_dark", "pill_dark.png"),
            ("badge_inst","badge_inst.png"),
        ]:
            p = os.path.join(ICONS_PATH, fname)
            if os.path.exists(p):
                setattr(self, attr, LoadPixmap(p))
        self.update_clock()
        self.timer.start(10000)
        self.apply_view_visibility()
        self.load_database(force=False)

    def apply_view_visibility(self):
        is_grid = (self.view_style == "grid")
        for w in ["left_bg", "left_title", "left_line", "left_info", "left_pkg_name", "preview_icon", "page_info", "section_heading", "list", "right_bg", "right_header", "right_line", "side_list", "side_page_lbl"]:
            if is_grid:
                self[w].hide()
            else:
                self[w].show()
        if is_grid:
            self["grid_list"].show()
            self["key_yellow"].setText("عرض القائمة")
            self["mode_badge"].setText("وضع الشبكة 4x3  |  أصفر للعودة للقائمة")
        else:
            self["grid_list"].hide()
            self["key_yellow"].setText("عرض شبكة 4x3")
            self["mode_badge"].setText("حديث | متعدد     < > الفئات     0: بحث")

    def toggle_view_mode(self):
        self.view_style = "grid" if self.view_style == "list" else "list"
        self.apply_view_visibility()
        self.render_current_items()
        self.update_left_panel()

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
            self.nav_stack = []
            self.build_main_categories_meta()
            self.show_main()
        except Exception as e:
            self["center_header"].setText("Error: " + str(e))

    def build_main_categories_meta(self):
        self.main_cats_meta = []
        for item in self.db.get("main", []):
            sec = item.get("section", "")
            raw_title = item.get("name", "") or item.get("title", "") or sec
            sub_list = self.get_sub_items(item) or []
            cnt = len(sub_list)
            ar_title, ar_desc, ic_key = resolve_cat_meta(raw_title, sec, cnt)
            self.main_cats_meta.append({
                "title": ar_title,
                "subtitle": ar_desc,
                "count": cnt,
                "badge": str(cnt),
                "icon": ic_key,
                "installed": False,
                "data": item
            })

    def get_icon_pix(self, icon_key):
        ic_file = os.path.join(ICONS_PATH, "ic_%s.png" % icon_key)
        if not os.path.exists(ic_file):
            ic_file = os.path.join(ICONS_PATH, "ic_default.png")
        return LoadPixmap(ic_file) if os.path.exists(ic_file) else None

    def refresh_sidebar(self):
        side_entries = []
        total = len(self.main_cats_meta)
        for i, meta in enumerate(self.main_cats_meta):
            is_act = (i == self.active_cat_idx)
            pill = self.pill_gold if is_act else self.pill_dark
            cnt_col = 0x000b0d12 if is_act else 0x00cbd5e1
            txt_col = 0x00f5d061 if is_act else 0x00cbd5e1
            res = [meta["data"]]
            if pill:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 12, 10, 56, 30, pill))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 12, 10, 56, 30, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, str(meta["count"]), cnt_col, cnt_col))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 78, 6, 305, 38, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, to_str(meta["title"]), txt_col, 0x00f5d061))
            if is_act:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 392, 8, 5, 34, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "", 0x00f5d061, 0x00f5d061, 0x00f5d061, 0x00f5d061))
            side_entries.append(res)
        self["side_list"].setList(side_entries)
        if side_entries and 0 <= self.active_cat_idx < total:
            self["side_list"].moveToIndex(self.active_cat_idx)
        self["side_page_lbl"].setText("%d / %d" % (self.active_cat_idx + 1, max(1, total)))

    def make_list_card(self, entry, is_selected):
        ic_pix = self.get_icon_pix(entry["icon"])
        bg_pix = self.card_sel if is_selected else self.card_norm
        title = to_str(entry["title"])
        subtitle = to_str(entry["subtitle"])
        badge = to_str(entry["badge"])
        is_installed = entry["installed"]
        res = [entry["data"]]

        if bg_pix:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 6, 3, 948, 68, bg_pix))
        if ic_pix:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 874, 5, 64, 64, ic_pix))

        t_col = 0x00f5d061 if is_selected else 0x00ffffff
        if subtitle:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 480, 12, 380, 50, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, title, t_col, t_col))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 115, 12, 350, 50, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, subtitle, 0x0094a3b8, 0x00cbd5e1))
        else:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 130, 12, 730, 50, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, title, t_col, t_col))

        if is_installed:
            if self.badge_inst:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 24, 21, 88, 32, self.badge_inst))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 24, 21, 88, 32, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "مثبت", 0x00fca5a5, 0x00ffffff))
        elif badge:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 24, 18, 88, 38, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, badge, 0x00f5d061, 0x00ffffff))
        return res

    def build_grid_rows(self):
        cols = 4
        col_x = [1365, 915, 465, 15]
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
                bg_pix = self.grid_sel if is_selected else self.grid_norm
                if bg_pix:
                    row_entries.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x0, 6, 430, 235, bg_pix))
                ic_pix = self.get_icon_pix(entry["icon"])
                if ic_pix:
                    row_entries.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x0 + 345, 22, 64, 64, ic_pix))
                t_col = 0x00f5d061 if is_selected else 0x00ffffff
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 24, 310, 60, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, to_str(entry["title"]), t_col, t_col))
                sub_txt = to_str(entry["subtitle"]) or "متجر أونلاين تكنولوجي"
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 100, 390, 80, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, sub_txt, 0x00cbd5e1, 0x00ffffff))
                if entry["installed"]:
                    if self.badge_inst:
                        row_entries.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x0 + 24, 190, 88, 32, self.badge_inst))
                    row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 24, 190, 88, 32, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "مثبت", 0x00fca5a5, 0x00ffffff))
            rows.append(row_entries)
        self["grid_list"].setList(rows)
        if rows:
            self["grid_list"].moveToIndex(self.grid_index // cols)

    def update_page_counter(self):
        total = len(self.current_items)
        per_page = 12 if self.view_style == "grid" else 10
        tot_pages = max(1, (total + per_page - 1) // per_page)
        cur_page = min(tot_pages, (self.grid_index // per_page) + 1)
        unit = "عنصر" if self.mode == "main" else "حزمة"
        self["page_info"].setText("%d %s   صفحة %d/%d" % (total, unit, cur_page, tot_pages))

    def render_current_items(self):
        self.update_page_counter()
        if self.view_style == "grid":
            self.build_grid_rows()
        else:
            cards = []
            for i, entry in enumerate(self.current_items):
                cards.append(self.make_list_card(entry, i == self.grid_index))
            self["list"].setList(cards)
            if cards and 0 <= self.grid_index < len(cards):
                self["list"].moveToIndex(self.grid_index)

    def update_left_panel(self):
        if self.view_style == "grid":
            return
        if self.mode == "main":
            self["preview_icon"].hide()
            self["left_pkg_name"].setText("")
            self["left_title"].setText("النظام")
            self["left_info"].setText(self.get_sys_info_text())
            return

        self["left_title"].setText("معاينة الحزمة")
        if not self.current_items or self.grid_index < 0 or self.grid_index >= len(self.current_items):
            return
        entry = self.current_items[self.grid_index]
        data = entry["data"]
        name = to_str(entry["title"])
        ic_file = os.path.join(ICONS_PATH, "ic_%s.png" % entry["icon"])
        if not os.path.exists(ic_file):
            ic_file = os.path.join(ICONS_PATH, "ic_default.png")
        if os.path.exists(ic_file) and self["preview_icon"].instance:
            self["preview_icon"].instance.setPixmapFromFile(ic_file)
            self["preview_icon"].show()

        self["left_pkg_name"].setText(name[:34])
        sub_list = self.get_sub_items(data)
        sec_title = self["section_heading"].getText()
        if sub_list is not None:
            details = "\n\n\n\n\nالنوع :  قسم فرعي\n\nالفئة :  %s\n\nالمحتوى :  %d ملف متاح\n\nاضغط OK لاستعراض الملفات" % (sec_title, len(sub_list))
        else:
            inst = "مثبت على الجهاز" if entry["installed"] else "متاح للتثبيت"
            details = "\n\n\n\n\nالحالة :  %s\n\nالفئة :  %s\n\nالمصدر :  Online4Tech Cloud\n\nاضغط OK أو الأخضر للتثبيت المباشر" % (inst, sec_title)
        self["left_info"].setText(details)

    def show_main(self):
        self.mode = "main"
        self.nav_stack = []
        self.grid_index = self.active_cat_idx
        self["key_red"].setText("خروج")
        self["section_heading"].setText("انيجما 2")
        self.current_items = list(self.main_cats_meta)
        self.refresh_sidebar()
        self.render_current_items()
        self.update_left_panel()

    def show_items_list(self, items_list, sec_name, icon_hint=""):
        self.mode = "section"
        self.grid_index = 0
        self["key_red"].setText("رجوع")
        ar_sec_title, _, ic_key = resolve_cat_meta(sec_name, icon_hint, len(items_list))
        self["section_heading"].setText(to_str(ar_sec_title))

        self.current_items = []
        for item in items_list:
            name = item.get("name", "") or item.get("title", "Package")
            sub_list = self.get_sub_items(item)
            if sub_list is not None:
                cnt = len(sub_list)
                self.current_items.append({
                    "title": name,
                    "subtitle": "قسم فرعي (%d ملف)" % cnt,
                    "badge": "(%d)" % cnt,
                    "icon": guess_icon(name + " " + icon_hint),
                    "installed": False,
                    "data": item
                })
            else:
                path = item.get("path", "")
                inst = bool(path and os.path.exists(path))
                self.current_items.append({
                    "title": name,
                    "subtitle": "",
                    "badge": "",
                    "icon": ic_key,
                    "installed": inst,
                    "data": item
                })

        self.refresh_sidebar()
        self.render_current_items()
        self.update_left_panel()

    def open_search(self):
        self.session.openWithCallback(self.run_search, VirtualKeyBoard, title="ابحث عن بلجن أو ملف قنوات في Online4Tech:", text="")

    def run_search(self, keyword):
        if not keyword:
            return
        kw = to_str(keyword).lower().strip()
        results = []
        seen = set()
        for k, val in self.db.items():
            if k == "main" or not isinstance(val, list):
                continue
            for item in val:
                if not isinstance(item, dict):
                    continue
                name = to_str(item.get("name", "") or item.get("title", ""))
                if kw in name.lower() and item.get("cmd") and name not in seen:
                    seen.add(name)
                    results.append(item)
        self.nav_stack.append((list(self.current_items), self["section_heading"].getText(), self.mode, self.grid_index))
        self.show_items_list(results, "بحث: " + to_str(keyword), "plugins")

    def move_up(self):
        total = len(self.current_items)
        if not total:
            return
        if self.view_style == "grid":
            if self.grid_index >= 4:
                self.grid_index -= 4
        else:
            self.grid_index = (self.grid_index - 1) % total
            if self.mode == "main":
                self.active_cat_idx = self.grid_index
                self.refresh_sidebar()
        self.render_current_items()
        self.update_left_panel()

    def move_down(self):
        total = len(self.current_items)
        if not total:
            return
        if self.view_style == "grid":
            if self.grid_index + 4 < total:
                self.grid_index += 4
        else:
            self.grid_index = (self.grid_index + 1) % total
            if self.mode == "main":
                self.active_cat_idx = self.grid_index
                self.refresh_sidebar()
        self.render_current_items()
        self.update_left_panel()

    def move_left(self):
        if self.view_style == "grid":
            if self.grid_index + 1 < len(self.current_items):
                self.grid_index += 1
                self.render_current_items()
        elif self.main_cats_meta:
            self.active_cat_idx = (self.active_cat_idx + 1) % len(self.main_cats_meta)
            cat_data = self.main_cats_meta[self.active_cat_idx]["data"]
            sub_list = self.get_sub_items(cat_data) or []
            self.nav_stack = []
            self.show_items_list(sub_list, self.main_cats_meta[self.active_cat_idx]["title"], cat_data.get("section", ""))

    def move_right(self):
        if self.view_style == "grid":
            if self.grid_index > 0:
                self.grid_index -= 1
                self.render_current_items()
        elif self.main_cats_meta:
            self.active_cat_idx = (self.active_cat_idx - 1) % len(self.main_cats_meta)
            cat_data = self.main_cats_meta[self.active_cat_idx]["data"]
            sub_list = self.get_sub_items(cat_data) or []
            self.nav_stack = []
            self.show_items_list(sub_list, self.main_cats_meta[self.active_cat_idx]["title"], cat_data.get("section", ""))

    def ok_pressed(self):
        if not self.current_items or self.grid_index < 0 or self.grid_index >= len(self.current_items):
            return
        entry = self.current_items[self.grid_index]
        data = entry["data"]
        title = to_str(entry["title"])
        sub_list = self.get_sub_items(data)

        if sub_list is not None:
            if len(sub_list) == 0:
                self.session.open(MessageBox, "هذا القسم (%s) فارغ حاليا." % title, MessageBox.TYPE_INFO, timeout=4)
                return
            if self.mode == "main":
                self.active_cat_idx = self.grid_index
            self.nav_stack.append((list(self.current_items), self["section_heading"].getText(), self.mode, self.grid_index))
            self.show_items_list(sub_list, title, data.get("section", ""))
            return

        cmd = data.get("cmd", "")
        if cmd:
            self.session.open(Console, title="Online4Tech: " + title, cmdlist=[to_str(cmd)])
        else:
            self.session.open(MessageBox, "لا يوجد أمر تثبيت مسجل لهذا العنصر (%s)." % title, MessageBox.TYPE_INFO, timeout=4)

    def refresh_server(self):
        self["center_header"].setText("جاري مزامنة قاعدة بيانات Online4Tech...")
        self.load_database(force=True)
        self["center_header"].setText("🔍  ابحث عن البلاجينات والإضافات وملفات القنوات (اضغط زر 0)")

    def back_pressed(self):
        if self.nav_stack:
            prev_items, prev_heading, prev_mode, prev_idx = self.nav_stack.pop()
            if prev_mode == "main":
                self.show_main()
            else:
                self.mode = "section"
                self.current_items = prev_items
                self.grid_index = prev_idx
                self["section_heading"].setText(prev_heading)
                self.refresh_sidebar()
                self.render_current_items()
                self.update_left_panel()
        elif self.mode == "section":
            self.show_main()
        else:
            self.timer.stop()
            self.close()