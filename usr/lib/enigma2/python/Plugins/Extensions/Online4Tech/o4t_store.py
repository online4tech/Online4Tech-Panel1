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
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eTimer
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

def split_name_desc(raw_name, fallback_desc=""):
    s = to_str(raw_name).strip()
    if "(" in s and ")" in s and s.find("(") < s.rfind(")"):
        i1 = s.find("(")
        i2 = s.rfind(")")
        title_part = s[:i1].strip()
        desc_part = s[i1 + 1:i2].strip()
        if title_part:
            return title_part, (desc_part if desc_part else to_str(fallback_desc))
    return s, to_str(fallback_desc)

CAT_INFO = [
    ("online4tech", "حصريات أونلاين تكنولوجي", "إضافات وملفات حصرية لمتجر Online4Tech", "default"),
    ("fav",         "المفضلة",                 "أهم البلاجينات والإضافات المختارة", "default"),
    ("depend",      "تحديث المكتبات",          "تحديث مكتبات البايثون ومشغلات النظام", "feeds"),
    ("ciefp",       "إضافات سييف",             "إدارة وتثبيت بلاجينات وملفات سييف", "ciefp"),
    ("multiboot",   "ملتي بوت",                "تثبيت وإدارة بلاجينات الملتي بوت ومثبتات الصور", "multiboot"),
    ("restore",     "الاستعادة والنسخ",        "استعادة الإعدادات والنسخ الاحتياطي للنظام", "tools"),
    ("remove",      "حذف الإضافات",            "إزالة وحذف البلاجينات والحزم من الرسيفر", "remove"),
    ("backup",      "صور الباك اب",            "تحميل وتثبيت صور انيجما 2 الجاهزة", "display"),
    ("image",       "صور الأجهزة",             "تحميل وتثبيت صور انيجما 2 الخام والباك اب", "display"),
    ("panel",       "البانلات",                "استكشف بانلات انيجما 2 مع روابط المطورين", "panels"),
    ("novaler",     "نوفالر",                  "بلاجينات وأدوات لأجهزة نوفالر", "novaler"),
    ("plugin",      "الإضافات",                "إدارة وتثبيت البلاجينات", "plugins"),
    ("channel",     "ملفات القنوات",           "تحديث وتثبيت أحدث ملفات القنوات", "channels"),
    ("feed",        "الفيدات",                 "تحديث وتثبيت الفيدات", "feeds"),
    ("bootlogo",    "شعارات الإقلاع",          "تغيير شعارات الإقلاع وأيقونات التحميل", "display"),
    ("spinner",     "العرض والسبينر",          "تغيير شعارات الإقلاع وأيقونات التحميل", "display"),
    ("cam",         "السوفتكامات",             "إدارة السوفتكامات وإيموهات التشفير", "cams"),
    ("emu",         "السوفتكامات",             "إدارة السوفتكامات وإيموهات التشفير", "cams"),
    ("picon",       "البيكونات",               "تثبيت وإدارة شعارات القنوات", "picons"),
    ("skin",        "السكينات",                "اختيار وتطبيق السكينات", "skins"),
    ("media",       "الميديا و IPTV",          "مشغلات الميديا والصوتيات والآي بي تي في", "plugins"),
    ("iptv",        "آي بي تي في",             "إضافات ومشغلات القنوات عبر الإنترنت", "plugins"),
    ("sport",       "الرياضة",                 "جداول المباريات والقنوات الرياضية", "plugins"),
    ("quran",       "القرآن الكريم",           "تطبيقات وإذاعات القرآن الكريم", "plugins"),
    ("islamic",     "إسلاميات",                "تطبيقات القرآن الكريم ومواقيت الصلاة", "plugins"),
    ("epg",         "دليل البرامج",            "مصادر وإضافات دليل البرامج الإلكتروني", "feeds"),
    ("tool",        "الأدوات",                 "أدوات وإضافات مفيدة", "tools"),
    ("system",      "خدمات النظام",            "إعدادات وأوامر صيانة الرسيفر", "tools"),
    ("setting",     "الإعدادات",               "جرب قنوات وترددات وإعدادات جديدة", "channels"),
]

def resolve_cat_meta(raw_name, sec_key, cnt):
    combined = (to_str(raw_name) + " " + to_str(sec_key)).lower()
    for key_sub, ar_title, ar_desc, ic in CAT_INFO:
        if key_sub in combined:
            return ar_title, ar_desc, ic
    clean_title, ext_desc = split_name_desc(raw_name, "%d حزمة متاحة في هذا القسم" % cnt)
    return (clean_title or to_str(sec_key)), ext_desc, "plugins"

def guess_icon(sec_name):
    _, _, ic = resolve_cat_meta(sec_name, sec_name, 0)
    return ic

class O4TCardList(MenuList):
    def __init__(self, items):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(74)
        self.l.setFont(0, gFont("Regular", 23))
        self.l.setFont(1, gFont("Regular", 19))

class O4TGridRows(MenuList):
    def __init__(self, items):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(250)
        self.l.setFont(0, gFont("Regular", 22))
        self.l.setFont(1, gFont("Regular", 18))

class O4TSideList(MenuList):
    def __init__(self, items):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        self.l.setFont(0, gFont("Regular", 21))
        self.l.setFont(1, gFont("Regular", 17))

SKIN_FHD = """
<screen name="Online4TechStoreScreen" position="0,0" size="1920,1080" title="Online4Tech Panel" flags="wfNoBorder" backgroundColor="#0b0d12">
    <widget zPosition="1" name="bg_main" position="0,0" size="1920,1080" alphatest="blend" />

    <widget zPosition="3" name="clock_lbl" position="55,12" size="260,48" font="Regular;40" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="center" />
    <widget zPosition="3" name="date_lbl" position="55,62" size="260,26" font="Regular;18" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="center" />

    <widget zPosition="3" name="center_header" position="645,28" size="710,56" font="Regular;21" foregroundColor="#94a3b8" backgroundColor="#161a24" transparent="1" halign="right" valign="center" />

    <eLabel zPosition="3" text="Online4TechPanel" position="1480,18" size="390,46" font="Regular;34" foregroundColor="#f5d061" backgroundColor="#0b0d12" transparent="1" halign="center" />
    <eLabel zPosition="3" text="Online4Tech | الإصدار 7.5" position="1480,66" size="390,28" font="Regular;19" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="center" />

    <widget zPosition="3" name="left_title" position="55,192" size="350,34" font="Regular;22" foregroundColor="#94a3b8" backgroundColor="#12151d" transparent="1" halign="center" />
    <widget zPosition="3" name="left_info" position="55,250" size="350,650" font="Regular;20" foregroundColor="#cbd5e1" backgroundColor="#12151d" transparent="1" halign="center" />

    <widget zPosition="4" name="preview_icon" position="155,245" size="150,150" alphatest="blend" />
    <widget zPosition="4" name="left_pkg_name" position="50,412" size="360,42" font="Regular;24" foregroundColor="#f5d061" backgroundColor="#12151d" transparent="1" halign="center" />
    <widget zPosition="4" name="left_pkg_ver" position="55,456" size="350,30" font="Regular;19" foregroundColor="#94a3b8" backgroundColor="#12151d" transparent="1" halign="center" />

    <widget zPosition="4" name="left_stat_lbl" position="235,515" size="150,32" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="4" name="left_stat_val" position="65,515" size="165,32" font="Regular;20" foregroundColor="#ef4444" backgroundColor="#12151d" transparent="1" halign="left" />

    <widget zPosition="4" name="left_cat_lbl" position="235,558" size="150,32" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="4" name="left_cat_val" position="65,558" size="165,32" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#12151d" transparent="1" halign="left" />

    <widget zPosition="4" name="left_desc" position="55,620" size="350,220" font="Regular;20" foregroundColor="#cbd5e1" backgroundColor="#12151d" transparent="1" halign="center" />

    <!-- ارتفاع 740 بكسل يعرض 10 بطاقات كاملة بالضبط بدون قص البطاقة رقم 11 -->
    <widget zPosition="3" name="page_info" position="465,134" size="380,32" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="left" />
    <widget zPosition="3" name="section_heading" position="860,126" size="550,40" font="Regular;29" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="right" />
    <widget zPosition="3" name="list" position="460,180" size="960,740" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

    <!-- ارتفاع 700 بكسل يعرض 14 فئة كاملة بالضبط -->
    <widget zPosition="3" name="right_header" position="1480,162" size="380,34" font="Regular;21" foregroundColor="#94a3b8" backgroundColor="#12151d" transparent="1" halign="center" />
    <widget zPosition="3" name="side_list" position="1468,210" size="404,700" backgroundColor="#12151d" backgroundColorSelected="#1d222f" scrollbarMode="showNever" enableWrapAround="1" />
    <widget zPosition="3" name="side_page_lbl" position="1480,918" size="380,30" font="Regular;18" foregroundColor="#94a3b8" backgroundColor="#12151d" transparent="1" halign="right" />

    <!-- ارتفاع 750 بكسل يعرض 3 صفوف شبكة كاملة (12 بطاقة) -->
    <widget zPosition="4" name="grid_list" position="55,175" size="1810,750" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

    <widget zPosition="3" name="key_red" position="1635,1003" size="180,36" font="Regular;21" foregroundColor="#e2e8f0" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="3" name="key_green" position="1325,1003" size="210,36" font="Regular;21" foregroundColor="#e2e8f0" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="3" name="key_yellow" position="945,1003" size="290,36" font="Regular;21" foregroundColor="#f5d061" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="3" name="key_blue" position="655,1003" size="230,36" font="Regular;21" foregroundColor="#e2e8f0" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="3" name="mode_badge" position="75,1003" size="540,36" font="Regular;20" foregroundColor="#f5d061" backgroundColor="#12151d" transparent="1" halign="left" />
</screen>
"""

class Online4TechStoreScreen(Screen):
    def __init__(self, session):
        self.skin = SKIN_FHD
        Screen.__init__(self, session)

        self["bg_main"] = Pixmap()
        self["clock_lbl"] = Label("")
        self["date_lbl"] = Label("")
        self["center_header"] = Label("ابحث عن البلاجينات والإضافات (اضغط زر 0)")
        self["left_title"] = Label("النظام")
        self["left_info"] = Label("")

        self["preview_icon"] = Pixmap()
        self["left_pkg_name"] = Label("")
        self["left_pkg_ver"] = Label("")
        self["left_stat_lbl"] = Label("")
        self["left_stat_val"] = Label("")
        self["left_cat_lbl"] = Label("")
        self["left_cat_val"] = Label("")
        self["left_desc"] = Label("")

        self["page_info"] = Label("")
        self["section_heading"] = Label("انيجما 2")
        self["right_header"] = Label("الفئات")
        self["side_page_lbl"] = Label("")

        self["key_red"] = Label("خروج")
        self["key_green"] = Label("تثبيت / فتح")
        self["key_yellow"] = Label("عرض شبكة 4x3")
        self["key_blue"] = Label("تحديث السيرفر")
        self["mode_badge"] = Label("حديث | متعدد     < > الفئات     0: بحث")

        self["list"] = O4TCardList([])
        self["side_list"] = O4TSideList([])
        self["grid_list"] = O4TGridRows([])

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
        return "EGAMI-Team"

    def get_sys_info_text(self):
        lines = []
        try:
            model = "Vu+ DUO4K"
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
            except Exception:
                lines.append("IP: Local")
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
        bg_name = "bg_grid.png" if is_grid else "bg_main.png"
        bg_file = os.path.join(ICONS_PATH, bg_name)
        if not os.path.exists(bg_file):
            bg_file = os.path.join(ICONS_PATH, "bg_main.png")
        if os.path.exists(bg_file) and self["bg_main"].instance:
            self["bg_main"].instance.setPixmapFromFile(bg_file)

        for w in ["left_title", "page_info", "section_heading", "list", "right_header", "side_list", "side_page_lbl"]:
            if is_grid:
                self[w].hide()
            else:
                self[w].show()
        if is_grid:
            for w in ["left_info", "preview_icon", "left_pkg_name", "left_pkg_ver", "left_stat_lbl", "left_stat_val", "left_cat_lbl", "left_cat_val", "left_desc"]:
                self[w].hide()
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
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 485, 12, 375, 50, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, title, t_col, t_col))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 118, 12, 355, 50, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, subtitle, 0x0094a3b8, 0x00cbd5e1))
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
                    row_entries.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x0 + 344, 22, 64, 64, ic_pix))
                t_col = 0x00f5d061 if is_selected else 0x00ffffff
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 16, 24, 316, 60, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, to_str(entry["title"]), t_col, t_col))
                sub_txt = to_str(entry["subtitle"]) or "متجر أونلاين تكنولوجي"
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 18, 102, 390, 78, 1, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, sub_txt, 0x00cbd5e1, 0x00ffffff))
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
            for w in ["preview_icon", "left_pkg_name", "left_pkg_ver", "left_stat_lbl", "left_stat_val", "left_cat_lbl", "left_cat_val", "left_desc"]:
                self[w].hide()
            self["left_title"].setText("النظام")
            self["left_info"].setText(self.get_sys_info_text())
            self["left_info"].show()
            return

        self["left_info"].hide()
        for w in ["preview_icon", "left_pkg_name", "left_pkg_ver", "left_stat_lbl", "left_stat_val", "left_cat_lbl", "left_cat_val", "left_desc"]:
            self[w].show()

        self["left_title"].setText("معاينة الحزمة")
        if not self.current_items or self.grid_index < 0 or self.grid_index >= len(self.current_items):
            return
        entry = self.current_items[self.grid_index]
        data = entry["data"]
        name = to_str(entry["title"])
        sub_desc = to_str(entry["subtitle"])

        ic_big = os.path.join(ICONS_PATH, "ic_%s_big.png" % entry["icon"])
        if not os.path.exists(ic_big):
            ic_big = os.path.join(ICONS_PATH, "ic_default_big.png")
        if os.path.exists(ic_big) and self["preview_icon"].instance:
            self["preview_icon"].instance.setPixmapFromFile(ic_big)

        self["left_pkg_name"].setText(name[:28])
        sec_title = self["section_heading"].getText()
        sub_list = self.get_sub_items(data)

        self["left_stat_lbl"].setText("الحالة")
        self["left_cat_lbl"].setText("الفئة")
        self["left_cat_val"].setText(sec_title)

        if sub_list is not None:
            self["left_pkg_ver"].setText("قسم فرعي (%d ملف)" % len(sub_list))
            self["left_stat_val"].setText("متاح")
            self["left_desc"].setText("يحتوي هذا القسم على %d ملف.\nاضغط زر OK لاستعراض الملفات." % len(sub_list))
        else:
            self["left_pkg_ver"].setText(sub_desc if sub_desc else "الإصدار الرسمي")
            self["left_stat_val"].setText("مثبت" if entry["installed"] else "غير مثبت")
            desc_line = sub_desc if sub_desc else name
            self["left_desc"].setText("%s\nاضغط OK أو الزر الأخضر للتثبيت المباشر على الرسيفر." % desc_line)

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
            raw_name = item.get("name", "") or item.get("title", "Package")
            clean_title, ext_desc = split_name_desc(raw_name, "")
            sub_list = self.get_sub_items(item)
            if sub_list is not None:
                cnt = len(sub_list)
                self.current_items.append({
                    "title": clean_title,
                    "subtitle": ext_desc or ("قسم فرعي (%d ملف)" % cnt),
                    "badge": "(%d)" % cnt,
                    "icon": guess_icon(raw_name + " " + icon_hint),
                    "installed": False,
                    "data": item
                })
            else:
                path = item.get("path", "")
                inst = bool(path and os.path.exists(path))
                self.current_items.append({
                    "title": clean_title,
                    "subtitle": ext_desc,
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
        self["center_header"].setText("ابحث عن البلاجينات والإضافات (اضغط زر 0)")

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