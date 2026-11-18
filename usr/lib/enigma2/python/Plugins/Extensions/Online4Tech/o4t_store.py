# -*- coding: utf-8 -*-
from __future__ import print_function
import os, sys, json, time, socket, ssl
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
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
SETTINGS_FILE = "/etc/enigma2/o4t_settings.json"

def to_str(val):
    if val is None:
        return ""
    if not PY3 and isinstance(val, unicode):
        return val.encode("utf-8")
    if PY3 and isinstance(val, bytes):
        return val.decode("utf-8", "ignore")
    return str(val)

def load_settings():
    cfg = {"lang": "ar", "font_scale": "normal", "font_type": "Regular"}
    if os.path.exists(SETTINGS_FILE):
        try:
            raw = open(SETTINGS_FILE, "rb").read().decode("utf-8", "ignore")
            data = json.loads(raw)
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            pass
    return cfg

def save_settings(cfg):
    try:
        raw = json.dumps(cfg, indent=2)
        with open(SETTINGS_FILE, "wb") as f:
            f.write(raw.encode("utf-8"))
    except Exception:
        pass

# قاموس تصحيح الأخطاء الإملائية في الأسماء الإنجليزية
SPELL_FIXES = {
    "Update Dependencic": "Update Dependencies",
    "update dependencic": "Update Dependencies",
    "Dependencic": "Dependencies",
    "vaninbal": "Vhannibal",
    "Vaninbal": "Vhannibal",
    "Puere2": "Pure2",
    "puere2": "Pure2",
    "OpenPli_py3": "OpenPLi (Python 3)",
    "OpenPli_py2": "OpenPLi (Python 2)",
    "Chanal": "Channel",
}

def fix_spelling(text):
    s = to_str(text).strip()
    for wrong, right in SPELL_FIXES.items():
        if wrong in s:
            s = s.replace(wrong, right)
    return s

def split_name_desc(raw_name, fallback_desc=""):
    s = fix_spelling(raw_name)
    if "(" in s and ")" in s and s.find("(") < s.rfind(")"):
        i1 = s.find("(")
        i2 = s.rfind(")")
        title_part = s[:i1].strip()
        desc_part = s[i1 + 1:i2].strip()
        if title_part:
            return title_part, (desc_part if desc_part else to_str(fallback_desc))
    return s, to_str(fallback_desc)

# نصوص الواجهة الكاملة بالعربية والإنجليزية بدون أي أخطاء إملائية
UI_TEXT = {
    "ar": {
        "ver_title": "Online4Tech | الإصدار 7.5",
        "search_hint": "ابحث عن البلاجينات والإضافات (0: بحث | MENU: اللغة والخط)",
        "sys_title": "النظام",
        "preview_title": "معاينة الحزمة",
        "cats_header": "الأقسام",
        "exit": "خروج",
        "back": "رجوع",
        "back_cats": "رجوع للأقسام",
        "enter_cat": "دخول للقسم",
        "install_open": "تثبيت / فتح",
        "grid_view": "عرض شبكة 4x3",
        "list_view": "عرض القائمة",
        "refresh": "تحديث السيرفر",
        "badge_side": "MENU: اللغة والخط  |  OK أو السهم للدخول",
        "badge_center": "MENU: اللغة والخط  |  0: بحث سريع",
        "badge_grid": "وضع الشبكة 4x3  |  أصفر للقائمة  |  MENU: الإعدادات",
        "installed": "مثبت",
        "not_installed": "غير مثبت",
        "available": "متاح",
        "status_lbl": "الحالة",
        "cat_lbl": "الفئة",
        "official_ver": "الإصدار الرسمي",
        "store_sub": "متجر أونلاين تكنولوجي الرسمي",
        "sub_fmt": "قسم فرعي (%d ملف)",
        "sec_fmt": "قسم (%d عنصر)",
        "page_fmt": "%d عنصر   صفحة %d/%d",
        "sub_desc_fmt": "%s\nيحتوي على %d عنصر. اضغط OK للاستعراض.",
        "pkg_desc_fmt": "%s\nاضغط OK أو الزر الأخضر للتثبيت المباشر على الرسيفر.",
        "empty_msg": "هذا القسم (%s) فارغ حاليا.",
        "no_cmd_msg": "لا يوجد أمر تثبيت مسجل لهذا العنصر (%s).",
        "sync_msg": "جاري مزامنة قاعدة بيانات Online4Tech...",
        "search_kbd": "ابحث عن بلجن أو ملف قنوات في Online4Tech:",
        "search_res": "بحث: ",
        "menu_title": "إعدادات Online4Tech (اللغة ونوع وحجم الخط):",
    },
    "en": {
        "ver_title": "Online4Tech | v7.5 Gold",
        "search_hint": "Search Plugins & Packages (0: Search | MENU: Language & Font)",
        "sys_title": "System Info",
        "preview_title": "Package Preview",
        "cats_header": "Categories",
        "exit": "Exit",
        "back": "Back",
        "back_cats": "Categories",
        "enter_cat": "Open Section",
        "install_open": "Install / Open",
        "grid_view": "Grid View 4x3",
        "list_view": "List View",
        "refresh": "Sync Server",
        "badge_side": "MENU: Lang & Font  |  OK / Arrows: Enter",
        "badge_center": "MENU: Lang & Font  |  0: Quick Search",
        "badge_grid": "Grid View 4x3  |  Yellow: List  |  MENU: Settings",
        "installed": "Installed",
        "not_installed": "Not Installed",
        "available": "Available",
        "status_lbl": "Status",
        "cat_lbl": "Category",
        "official_ver": "Official Release",
        "store_sub": "Online4Tech Official Store",
        "sub_fmt": "Sub-category (%d files)",
        "sec_fmt": "Section (%d items)",
        "page_fmt": "%d Items   Page %d/%d",
        "sub_desc_fmt": "%s\nContains %d items. Press OK to browse.",
        "pkg_desc_fmt": "%s\nPress OK or Green button for direct installation.",
        "empty_msg": "This section (%s) is currently empty.",
        "no_cmd_msg": "No installation command found for (%s).",
        "sync_msg": "Synchronizing Online4Tech cloud database...",
        "search_kbd": "Search plugins or channel lists in Online4Tech:",
        "search_res": "Search: ",
        "menu_title": "Online4Tech Preferences (Language, Font Type & Size):",
    }
}

# قاموس الأقسام الفرعية ثنائي اللغة (العربية + الإنجليزية الصحيحة إملائيا)
CAT_INFO = [
    ("online4tech", "حصريات أونلاين تكنولوجي", "إضافات وملفات حصرية لمتجر Online4Tech", "Online4Tech Exclusives", "Official Online4Tech plugins & tools",      "default",   "exclusive"),
    ("fav",         "المفضلة",                 "أهم البلاجينات والإضافات المختارة",     "My Favorites",           "Most popular & essential Enigma2 plugins",   "default",   "exclusive"),
    ("channel",     "ملفات القنوات",           "تحديث وتثبيت أحدث ملفات القنوات",       "Channel Settings",       "Install latest satellite channel lists",     "channels",  "exclusive"),
    ("plugin",      "الإضافات",                "إدارة وتثبيت البلاجينات",               "Enigma2 Plugins",        "Browse & install general Enigma2 plugins",   "plugins",   "enigma2"),
    ("panel",       "البانلات",                "استكشف بانلات انيجما 2 مع روابط المطورين", "Panels & Stores",     "Explore popular Enigma2 addon panels",       "panels",    "enigma2"),
    ("feed",        "الفيدات",                 "تحديث وتثبيت الفيدات",                  "System Feeds",           "Install & update official image feeds",      "feeds",     "enigma2"),
    ("ciefp",       "إضافات سييف",             "إدارة وتثبيت بلاجينات وملفات سييف",     "Ciefp Plugins",          "Ciefp settings, picons & utilities",         "ciefp",     "enigma2"),
    ("media",       "الميديا و IPTV",          "مشغلات الميديا والصوتيات والآي بي تي في", "Media & IPTV",         "VOD, IPTV players & streaming addons",       "plugins",   "enigma2"),
    ("iptv",        "آي بي تي في",             "إضافات ومشغلات القنوات عبر الإنترنت",   "IPTV Players",           "Stream live TV & VOD playlists",             "plugins",   "enigma2"),
    ("novaler",     "نوفالر",                  "بلاجينات وأدوات لأجهزة نوفالر",         "Novaler Addons",         "Dedicated plugins for Novaler receivers",    "novaler",   "enigma2"),
    ("cam",         "السوفتكامات",             "إدارة السوفتكامات وإيموهات التشفير",    "Softcams & Emulators",   "OSCam, NCam & CCcam softcam packages",       "cams",      "cams"),
    ("emu",         "السوفتكامات",             "إدارة السوفتكامات وإيموهات التشفير",    "Softcams & Emulators",   "OSCam, NCam & CCcam softcam packages",       "cams",      "cams"),
    ("skin",        "السكينات",                "اختيار وتطبيق السكينات",                "Enigma2 Skins",          "FHD & HD graphical user interface skins",    "skins",     "display"),
    ("picon",       "البيكونات",               "تثبيت وإدارة شعارات القنوات",           "Channel Picons",         "High-resolution satellite channel logos",    "picons",    "display"),
    ("bootlogo",    "شعارات الإقلاع",          "تغيير شعارات الإقلاع وأيقونات التحميل", "Bootlogos",              "Custom startup bootlogo wallpapers",         "display",   "display"),
    ("spinner",     "العرض والسبينر",          "تغيير شعارات الإقلاع وأيقونات التحميل", "Loading Spinners",       "Animated waiting & loading spinners",        "display",   "display"),
    ("multiboot",   "ملتي بوت",                "تثبيت وإدارة بلاجينات الملتي بوت",      "Multiboot Tools",        "Multi-image boot managers & flashers",       "multiboot", "images"),
    ("backup",      "صور الباك اب",            "تحميل وتثبيت صور انيجما 2 الجاهزة",     "Backup Images",          "Pre-configured full Enigma2 backup images",  "display",   "images"),
    ("image",       "صور الأجهزة",             "تحميل وتثبيت صور انيجما 2 الخام",       "Clean Images",           "Official clean firmware receiver images",    "display",   "images"),
    ("depend",      "تحديث المكتبات",          "تحديث مكتبات البايثون ومشغلات النظام",  "Update Dependencies",    "Fix & install missing Python libraries",     "feeds",     "system"),
    ("tool",        "الأدوات",                 "أدوات وإضافات خدمية مفيدة",             "Utility Tools",          "System maintenance & helper tools",          "tools",     "system"),
    ("system",      "خدمات النظام",            "إعدادات وأوامر صيانة الرسيفر",          "System Services",        "Core system tweaks & service scripts",       "tools",     "system"),
    ("restore",     "الاستعادة والنسخ",        "استعادة الإعدادات والنسخ الاحتياطي",    "Backup & Restore",       "Save & restore settings and bouquets",       "tools",     "system"),
    ("remove",      "حذف الإضافات",            "إزالة وحذف البلاجينات والحزم من الرسيفر", "Remove Packages",      "Uninstall plugins, skins & extensions",      "remove",    "system"),
    ("setting",     "الإعدادات",               "جرب قنوات وترددات وإعدادات جديدة",      "Tuner & Settings",       "Transponders, satellites.xml & configs",     "channels",  "system"),
]

# الأقسام الستة الرئيسية ثنائية اللغة مرتبة من الأهم إلى الأقل أهمية
MASTER_GROUPS = [
    ("exclusive", "أونلاين تكنولوجي", "الحصريات والمفضلة وأحدث ملفات القنوات",             "Online4Tech", "Exclusives, Favorites & Channel Lists",     "default"),
    ("enigma2",   "البلاجنز",         "الإضافات والبانلات والفيدات والميديا وسييف ونوفالر", "Plugins",     "Addons, Panels, Feeds, Media & Novaler",    "plugins"),
    ("display",   "الاسكينات",        "السكينات والبيكونات وشعارات الإقلاع والسبينر",       "Skins & UI",  "Skins, Picons, Bootlogos & Spinners",       "skins"),
    ("cams",      "السوفتكام",        "إدارة وتثبيت السوفتكامات وإيموهات التشفير",         "Softcams",    "Manage & install OSCam, NCam & Emulators",  "cams"),
    ("images",    "الملتي بوت",       "الملتي بوت وصور الأجهزة الخام وصور الباك اب",       "Multiboot",   "Multiboot managers, Clean & Backup Images", "multiboot"),
    ("system",    "النظام",           "تحديث المكتبات والأدوات والاستعادة وحذف الإضافات",   "System",      "Dependencies, Tools, Restore & Uninstaller","tools"),
]

def resolve_cat_full(raw_name, sec_key, cnt, lang="ar"):
    combined = (to_str(raw_name) + " " + to_str(sec_key)).lower()
    for key_sub, ar_t, ar_d, en_t, en_d, ic, grp in CAT_INFO:
        if key_sub in combined:
            title = en_t if lang == "en" else ar_t
            desc = en_d if lang == "en" else ar_d
            return title, desc, ic, grp
    clean_title, ext_desc = split_name_desc(raw_name, "")
    if lang == "en":
        fallback = "%d packages available" % cnt
        # في الوضع الإنجليزي إذا كان الوصف بين القوسين عربيا نستبدله بوصف إنجليزي نظيف
        if any(ord(ch) > 127 for ch in ext_desc):
            ext_desc = fallback
    else:
        fallback = "%d حزمة متاحة في هذا القسم" % cnt
    return (clean_title or to_str(sec_key)), (ext_desc or fallback), "plugins", "enigma2"

def guess_icon(sec_name):
    _, _, ic, _ = resolve_cat_full(sec_name, sec_name, 0, "ar")
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
        self.l.setItemHeight(64)
        self.l.setFont(0, gFont("Regular", 23))
        self.l.setFont(1, gFont("Regular", 18))

SKIN_FHD = """
<screen name="Online4TechStoreScreen" position="0,0" size="1920,1080" title="Online4Tech Panel" flags="wfNoBorder" backgroundColor="#0b0d12">
    <widget zPosition="1" name="bg_main" position="0,0" size="1920,1080" alphatest="blend" />

    <widget zPosition="3" name="clock_lbl" position="55,12" size="260,48" font="Regular;40" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="center" />
    <widget zPosition="3" name="date_lbl" position="55,62" size="260,26" font="Regular;18" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="center" />

    <widget zPosition="3" name="center_header" position="645,28" size="710,56" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#161a24" transparent="1" halign="center" valign="center" />

    <eLabel zPosition="3" text="Online4TechPanel" position="1480,18" size="390,46" font="Regular;34" foregroundColor="#f5d061" backgroundColor="#0b0d12" transparent="1" halign="center" />
    <widget zPosition="3" name="ver_lbl" position="1480,66" size="390,28" font="Regular;19" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="center" />

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

    <widget zPosition="3" name="page_info" position="465,134" size="380,32" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="left" />
    <widget zPosition="3" name="section_heading" position="860,126" size="550,40" font="Regular;29" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="right" />
    <widget zPosition="3" name="list" position="460,180" size="960,740" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

    <widget zPosition="3" name="right_header" position="1480,162" size="380,34" font="Regular;21" foregroundColor="#94a3b8" backgroundColor="#12151d" transparent="1" halign="center" />
    <widget zPosition="3" name="side_list" position="1468,220" size="404,640" backgroundColor="#12151d" backgroundColorSelected="#1d222f" scrollbarMode="showNever" enableWrapAround="1" />
    <widget zPosition="3" name="side_page_lbl" position="1480,918" size="380,30" font="Regular;18" foregroundColor="#94a3b8" backgroundColor="#12151d" transparent="1" halign="right" />

    <widget zPosition="4" name="grid_list" position="55,175" size="1810,750" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

    <widget zPosition="3" name="key_red" position="1635,1003" size="180,36" font="Regular;21" foregroundColor="#e2e8f0" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="3" name="key_green" position="1325,1003" size="210,36" font="Regular;21" foregroundColor="#e2e8f0" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="3" name="key_yellow" position="945,1003" size="290,36" font="Regular;21" foregroundColor="#f5d061" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="3" name="key_blue" position="655,1003" size="230,36" font="Regular;21" foregroundColor="#e2e8f0" backgroundColor="#12151d" transparent="1" halign="right" />
    <widget zPosition="3" name="mode_badge" position="75,1003" size="560,36" font="Regular;20" foregroundColor="#f5d061" backgroundColor="#12151d" transparent="1" halign="left" />
</screen>
"""

class Online4TechStoreScreen(Screen):
    def __init__(self, session):
        self.skin = SKIN_FHD
        Screen.__init__(self, session)

        self.cfg = load_settings()
        self.lang = self.cfg.get("lang", "ar")
        if self.lang not in ("ar", "en"):
            self.lang = "ar"

        self["bg_main"] = Pixmap()
        self["clock_lbl"] = Label("")
        self["date_lbl"] = Label("")
        self["ver_lbl"] = Label("")
        self["center_header"] = Label("")
        self["left_title"] = Label("")
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
        self["section_heading"] = Label("")
        self["right_header"] = Label("")
        self["side_page_lbl"] = Label("")

        self["key_red"] = Label("")
        self["key_green"] = Label("")
        self["key_yellow"] = Label("")
        self["key_blue"] = Label("")
        self["mode_badge"] = Label("")

        self["list"] = O4TCardList([])
        self["side_list"] = O4TSideList([])
        self["grid_list"] = O4TGridRows([])

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "NumberActions", "MenuActions"], {
            "ok": self.ok_pressed,
            "cancel": self.back_pressed,
            "red": self.back_pressed,
            "green": self.ok_pressed,
            "yellow": self.toggle_view_mode,
            "blue": self.refresh_server,
            "menu": self.open_settings_menu,
            "9": self.open_settings_menu,
            "0": self.open_search,
            "up": self.move_up,
            "down": self.move_down,
            "left": self.move_left,
            "right": self.move_right,
        }, -1)

        self.db = {}
        self.focus_pane = "side"
        self.nav_stack = []
        self.view_style = "list"
        self.current_items = []
        self.main_cats_meta = []
        self.active_cat_idx = 0
        self.grid_index = 0

        self.icon_cache = {}
        self.cached_sys_info = ""

        self.card_norm = None
        self.card_sel = None
        self.grid_norm = None
        self.grid_sel = None
        self.pill_gold = None
        self.pill_dark = None
        self.badge_inst = None
        self.badge_inst_en = None

        self.timer = eTimer()
        try:
            self.timer.callback.append(self.update_clock)
        except AttributeError:
            self.timer_conn = self.timer.timeout.connect(self.update_clock)
        self.onLayoutFinish.append(self.startup)

    def tr(self, key):
        return UI_TEXT.get(self.lang, UI_TEXT["ar"]).get(key, key)

    def apply_font_settings(self):
        f_type = self.cfg.get("font_type", "Regular")
        scale_key = self.cfg.get("font_scale", "normal")
        delta = -2 if scale_key == "small" else (3 if scale_key == "large" else 0)

        try:
            self["list"].l.setFont(0, gFont(f_type, 23 + delta))
            self["list"].l.setFont(1, gFont(f_type, 19 + delta))
            self["grid_list"].l.setFont(0, gFont(f_type, 22 + delta))
            self["grid_list"].l.setFont(1, gFont(f_type, 18 + delta))
            self["side_list"].l.setFont(0, gFont(f_type, 23 + delta))
            self["side_list"].l.setFont(1, gFont(f_type, 18 + delta))
        except Exception:
            pass

        widget_sizes = [
            ("center_header", 20), ("ver_lbl", 19), ("left_title", 22),
            ("left_info", 20), ("left_pkg_name", 24), ("left_pkg_ver", 19),
            ("left_stat_lbl", 20), ("left_stat_val", 20), ("left_cat_lbl", 20),
            ("left_cat_val", 20), ("left_desc", 20), ("page_info", 20),
            ("section_heading", 28), ("right_header", 21), ("key_red", 21),
            ("key_green", 21), ("key_yellow", 21), ("key_blue", 21), ("mode_badge", 20)
        ]
        for w_name, base_sz in widget_sizes:
            if w_name in self and self[w_name].instance:
                try:
                    self[w_name].instance.setFont(gFont(f_type, max(14, base_sz + delta)))
                except Exception:
                    pass

    def open_settings_menu(self):
        cur_lang_lbl = "English" if self.lang == "ar" else "العربية (Arabic)"
        if self.lang == "ar":
            options = [
                ("تغيير اللغة إلى: %s" % cur_lang_lbl, "toggle_lang"),
                ("حجم الخط: صغير (Small)", "scale_small"),
                ("حجم الخط: قياسي (Normal)", "scale_normal"),
                ("حجم الخط: كبير (Large)", "scale_large"),
                ("نوع الخط: قياسي (Regular)", "font_regular"),
                ("نوع الخط: عريض / واضح (Bold)", "font_bold"),
            ]
        else:
            options = [
                ("Switch Language to: %s" % cur_lang_lbl, "toggle_lang"),
                ("Font Size: Small", "scale_small"),
                ("Font Size: Normal (Default)", "scale_normal"),
                ("Font Size: Large", "scale_large"),
                ("Font Type: Regular", "font_regular"),
                ("Font Type: Bold / Clear", "font_bold"),
            ]
        self.session.openWithCallback(self.settings_menu_cb, ChoiceBox, title=self.tr("menu_title"), list=options)

    def settings_menu_cb(self, choice):
        if not choice:
            return
        act = choice[1]
        if act == "toggle_lang":
            self.lang = "en" if self.lang == "ar" else "ar"
            self.cfg["lang"] = self.lang
        elif act == "scale_small":
            self.cfg["font_scale"] = "small"
        elif act == "scale_normal":
            self.cfg["font_scale"] = "normal"
        elif act == "scale_large":
            self.cfg["font_scale"] = "large"
        elif act == "font_regular":
            self.cfg["font_type"] = "Regular"
        elif act == "font_bold":
            self.cfg["font_type"] = "Bold"

        save_settings(self.cfg)
        self.apply_font_settings()
        self.apply_static_labels()
        self.build_main_categories_meta()
        self.preview_active_category()

    def apply_static_labels(self):
        self["ver_lbl"].setText(self.tr("ver_title"))
        self["center_header"].setText(self.tr("search_hint"))
        self["right_header"].setText(self.tr("cats_header"))
        self["key_blue"].setText(self.tr("refresh"))
        self.update_footer_hints()

    def update_clock(self):
        self["clock_lbl"].setText(time.strftime("%H:%M"))
        self["date_lbl"].setText(time.strftime("%A %d %B"))

    def detect_image_name(self):
        for p in ["/etc/issue", "/etc/image-version"]:
            if os.path.exists(p):
                try:
                    raw = open(p, "rb").read().decode("utf-8", "ignore")
                    txt = raw.splitlines()[0].replace("\\n", "").replace("\\l", "").strip()
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
                model = "Vu+ " + open("/proc/stb/info/vumodel", "rb").read().decode("utf-8", "ignore").strip().upper()
            elif os.path.exists("/proc/stb/info/boxtype"):
                model = open("/proc/stb/info/boxtype", "rb").read().decode("utf-8", "ignore").strip().upper()
            lines.append("Box: " + model)
            lines.append("Image: " + self.detect_image_name())
            lines.append("Python: %d.%d.%d" % sys.version_info[:3])
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(0.4)
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
                mem_lines = open("/proc/meminfo", "rb").read().decode("utf-8", "ignore").splitlines()
                mem_map = {}
                for line in mem_lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            mem_map[parts[0].rstrip(":")] = int(parts[1])
                        except Exception:
                            pass
                tot_m = mem_map.get("MemTotal", 0) // 1024
                if "MemAvailable" in mem_map:
                    avl_m = mem_map["MemAvailable"] // 1024
                else:
                    avl_m = (mem_map.get("MemFree", 0) + mem_map.get("Buffers", 0) + mem_map.get("Cached", 0)) // 1024
                if tot_m > 0:
                    lines.append("Ram: %dMB / %dMB" % (max(0, tot_m - avl_m), tot_m))
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
            ("card_norm",     "card_norm_fhd.png"),
            ("card_sel",      "card_sel_fhd.png"),
            ("grid_norm",     "grid_norm.png"),
            ("grid_sel",      "grid_sel.png"),
            ("pill_gold",     "pill_gold.png"),
            ("pill_dark",     "pill_dark.png"),
            ("badge_inst",    "badge_inst.png"),
            ("badge_inst_en", "badge_inst_en.png"),
        ]:
            p = os.path.join(ICONS_PATH, fname)
            if os.path.exists(p):
                setattr(self, attr, LoadPixmap(p))
        self.cached_sys_info = self.get_sys_info_text()
        self.update_clock()
        self.timer.start(10000)
        self.apply_font_settings()
        self.apply_static_labels()
        self.apply_view_visibility()
        self.load_database(force=False)

    def update_footer_hints(self):
        if self.view_style == "grid":
            self["key_red"].setText(self.tr("back"))
            self["key_green"].setText(self.tr("install_open"))
            self["key_yellow"].setText(self.tr("list_view"))
            self["mode_badge"].setText(self.tr("badge_grid"))
            return

        self["key_yellow"].setText(self.tr("grid_view"))
        if self.focus_pane == "side":
            self["key_red"].setText(self.tr("exit"))
            self["key_green"].setText(self.tr("enter_cat"))
            self["mode_badge"].setText(self.tr("badge_side"))
        else:
            self["key_red"].setText(self.tr("back") if self.nav_stack else self.tr("back_cats"))
            self["key_green"].setText(self.tr("install_open"))
            self["mode_badge"].setText(self.tr("badge_center"))

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
        else:
            self["grid_list"].hide()
        self.update_footer_hints()

    def toggle_view_mode(self):
        if self.view_style == "list":
            self.view_style = "grid"
        else:
            self.view_style = "list"
            if self.current_items:
                self.focus_pane = "center"
        self.apply_view_visibility()
        self.refresh_sidebar()
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
            self.active_cat_idx = 0
            self.focus_pane = "side"
            self.preview_active_category()
        except Exception as e:
            self["center_header"].setText("Error: " + str(e))

    def build_main_categories_meta(self):
        grouped = {g[0]: [] for g in MASTER_GROUPS}
        for item in self.db.get("main", []):
            sec = item.get("section", "")
            raw_title = item.get("name", "") or item.get("title", "") or sec
            sub_list = self.get_sub_items(item) or []
            cnt = len(sub_list)
            cat_title, cat_desc, ic_key, grp_key = resolve_cat_full(raw_title, sec, cnt, self.lang)
            sub_cat_obj = {
                "name": cat_title,
                "desc": cat_desc,
                "icon": ic_key,
                "section": sec,
                "items": sub_list
            }
            grouped.setdefault(grp_key, []).append(sub_cat_obj)

        self.main_cats_meta = []
        for grp_key, ar_title, ar_desc, en_title, en_desc, grp_ic in MASTER_GROUPS:
            subs = grouped.get(grp_key, [])
            if not subs:
                continue
            target_items = subs[0]["items"] if len(subs) == 1 else subs
            g_title = en_title if self.lang == "en" else ar_title
            g_desc = en_desc if self.lang == "en" else ar_desc
            self.main_cats_meta.append({
                "title": g_title,
                "subtitle": g_desc,
                "count": len(target_items),
                "badge": str(len(target_items)),
                "icon": grp_ic,
                "installed": False,
                "data": {"name": g_title, "items": target_items}
            })

    def get_icon_pix(self, icon_key):
        if icon_key in self.icon_cache:
            return self.icon_cache[icon_key]
        ic_file = os.path.join(ICONS_PATH, "ic_%s.png" % icon_key)
        if not os.path.exists(ic_file):
            ic_file = os.path.join(ICONS_PATH, "ic_default.png")
        pix = LoadPixmap(ic_file) if os.path.exists(ic_file) else None
        self.icon_cache[icon_key] = pix
        return pix

    def refresh_sidebar(self):
        side_entries = []
        total = len(self.main_cats_meta)
        align_fl = (RT_HALIGN_LEFT if self.lang == "en" else RT_HALIGN_RIGHT) | RT_VALIGN_CENTER
        for i, meta in enumerate(self.main_cats_meta):
            is_act = (i == self.active_cat_idx)
            pill = self.pill_gold if is_act else self.pill_dark
            cnt_col = 0x000b0d12 if is_act else 0x00cbd5e1
            txt_col = 0x00f5d061 if is_act else 0x00cbd5e1
            res = [meta["data"]]
            if self.lang == "en":
                if is_act:
                    bar_col = 0x00f5d061 if self.focus_pane == "side" else 0x0094a3b8
                    res.append((eListboxPythonMultiContent.TYPE_TEXT, 4, 12, 12, 40, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "|", bar_col, bar_col))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 22, 12, 300, 40, 0, align_fl, to_str(meta["title"]), txt_col, 0x00f5d061))
                if pill:
                    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 334, 17, 56, 30, pill))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 334, 17, 56, 30, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, str(meta["count"]), cnt_col, cnt_col))
            else:
                if pill:
                    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 12, 17, 56, 30, pill))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 12, 17, 56, 30, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, str(meta["count"]), cnt_col, cnt_col))
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 78, 12, 305, 40, 0, align_fl, to_str(meta["title"]), txt_col, 0x00f5d061))
                if is_act:
                    bar_col = 0x00f5d061 if self.focus_pane == "side" else 0x0094a3b8
                    res.append((eListboxPythonMultiContent.TYPE_TEXT, 388, 12, 12, 40, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "|", bar_col, bar_col))
            side_entries.append(res)
        self["side_list"].setList(side_entries)
        if side_entries and 0 <= self.active_cat_idx < total:
            self["side_list"].moveToIndex(self.active_cat_idx)
        self["side_page_lbl"].setText("%d / %d" % (self.active_cat_idx + 1, max(1, total)))

    def make_list_card(self, entry, is_selected):
        ic_pix = self.get_icon_pix(entry["icon"])
        show_gold = (is_selected and self.focus_pane == "center")
        bg_pix = self.card_sel if show_gold else self.card_norm
        title = to_str(entry["title"])
        subtitle = to_str(entry["subtitle"])
        badge = to_str(entry["badge"])
        is_installed = entry["installed"]
        res = [entry["data"]]

        if bg_pix:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 6, 3, 948, 68, bg_pix))
        if ic_pix:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 874, 5, 64, 64, ic_pix))

        t_col = 0x00f5d061 if show_gold else 0x00ffffff
        if subtitle:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 485, 12, 375, 50, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, title, t_col, t_col))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 130, 12, 345, 50, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, subtitle, 0x0094a3b8, 0x00cbd5e1))
        else:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 135, 12, 725, 50, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, title, t_col, t_col))

        if is_installed:
            b_pix = (self.badge_inst_en or self.badge_inst) if self.lang == "en" else self.badge_inst
            b_w = 104 if self.lang == "en" else 88
            if b_pix:
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 22, 21, b_w, 32, b_pix))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 22, 21, b_w, 32, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, self.tr("installed"), 0x00fca5a5, 0x00ffffff))
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
                sub_txt = to_str(entry["subtitle"]) or self.tr("store_sub")
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 18, 102, 390, 78, 1, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, sub_txt, 0x00cbd5e1, 0x00ffffff))
                if entry["installed"]:
                    b_pix = (self.badge_inst_en or self.badge_inst) if self.lang == "en" else self.badge_inst
                    b_w = 104 if self.lang == "en" else 88
                    if b_pix:
                        row_entries.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x0 + 24, 190, b_w, 32, b_pix))
                    row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 24, 190, b_w, 32, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, self.tr("installed"), 0x00fca5a5, 0x00ffffff))
            rows.append(row_entries)
        self["grid_list"].setList(rows)
        if rows:
            self["grid_list"].moveToIndex(self.grid_index // cols)

    def update_page_counter(self):
        total = len(self.current_items)
        per_page = 12 if self.view_style == "grid" else 10
        tot_pages = max(1, (total + per_page - 1) // per_page)
        cur_page = min(tot_pages, (self.grid_index // per_page) + 1)
        self["page_info"].setText(self.tr("page_fmt") % (total, cur_page, tot_pages))

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
        if self.focus_pane == "side" or not self.current_items:
            for w in ["preview_icon", "left_pkg_name", "left_pkg_ver", "left_stat_lbl", "left_stat_val", "left_cat_lbl", "left_cat_val", "left_desc"]:
                self[w].hide()
            self["left_title"].setText(self.tr("sys_title"))
            if not self.cached_sys_info:
                self.cached_sys_info = self.get_sys_info_text()
            self["left_info"].setText(self.cached_sys_info)
            self["left_info"].show()
            return

        self["left_info"].hide()
        for w in ["preview_icon", "left_pkg_name", "left_pkg_ver", "left_stat_lbl", "left_stat_val", "left_cat_lbl", "left_cat_val", "left_desc"]:
            self[w].show()

        self["left_title"].setText(self.tr("preview_title"))
        if self.grid_index < 0 or self.grid_index >= len(self.current_items):
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

        self["left_stat_lbl"].setText(self.tr("status_lbl"))
        self["left_cat_lbl"].setText(self.tr("cat_lbl"))
        self["left_cat_val"].setText(sec_title)

        if sub_list is not None:
            self["left_pkg_ver"].setText(self.tr("sec_fmt") % len(sub_list))
            self["left_stat_val"].setText(self.tr("available"))
            self["left_desc"].setText(self.tr("sub_desc_fmt") % (sub_desc, len(sub_list)))
        else:
            self["left_pkg_ver"].setText(sub_desc if sub_desc else self.tr("official_ver"))
            self["left_stat_val"].setText(self.tr("installed") if entry["installed"] else self.tr("not_installed"))
            desc_line = sub_desc if sub_desc else name
            self["left_desc"].setText(self.tr("pkg_desc_fmt") % desc_line)

    def populate_items(self, items_list, sec_name, icon_hint=""):
        self.grid_index = 0
        self["section_heading"].setText(to_str(sec_name))
        _, _, default_ic, _ = resolve_cat_full(sec_name, icon_hint, len(items_list), self.lang)

        self.current_items = []
        for item in items_list:
            raw_name = item.get("name", "") or item.get("title", "Package")
            custom_desc = item.get("desc", "")
            custom_ic = item.get("icon", "")
            clean_title, ext_desc = split_name_desc(raw_name, custom_desc)
            if self.lang == "en" and any(ord(ch) > 127 for ch in ext_desc):
                ext_desc = custom_desc if (custom_desc and not any(ord(ch) > 127 for ch in custom_desc)) else ""
            sub_list = self.get_sub_items(item)
            if sub_list is not None:
                cnt = len(sub_list)
                self.current_items.append({
                    "title": clean_title,
                    "subtitle": ext_desc or (self.tr("sub_fmt") % cnt),
                    "badge": "(%d)" % cnt,
                    "icon": custom_ic or guess_icon(raw_name + " " + item.get("section", "") + " " + icon_hint),
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
                    "icon": custom_ic or default_ic,
                    "installed": inst,
                    "data": item
                })

        self.refresh_sidebar()
        self.render_current_items()
        self.update_left_panel()
        self.update_footer_hints()

    def preview_active_category(self):
        if not self.main_cats_meta:
            return
        self.nav_stack = []
        if self.active_cat_idx >= len(self.main_cats_meta):
            self.active_cat_idx = 0
        cat_meta = self.main_cats_meta[self.active_cat_idx]
        cat_data = cat_meta["data"]
        sub_list = self.get_sub_items(cat_data) or []
        self.populate_items(sub_list, cat_meta["title"], cat_meta["icon"])

    def enter_center_pane(self):
        if not self.current_items:
            self.session.open(MessageBox, self.tr("empty_msg") % "", MessageBox.TYPE_INFO, timeout=3)
            return
        self.focus_pane = "center"
        if self.grid_index < 0 or self.grid_index >= len(self.current_items):
            self.grid_index = 0
        self.refresh_sidebar()
        self.render_current_items()
        self.update_left_panel()
        self.update_footer_hints()

    def return_to_sidebar(self):
        self.focus_pane = "side"
        self.refresh_sidebar()
        self.render_current_items()
        self.update_left_panel()
        self.update_footer_hints()

    def after_install_cb(self, *args):
        for entry in self.current_items:
            path = entry["data"].get("path", "")
            if path:
                entry["installed"] = os.path.exists(path)
        self.cached_sys_info = self.get_sys_info_text()
        self.render_current_items()
        self.update_left_panel()

    def open_search(self):
        self.session.openWithCallback(self.run_search, VirtualKeyBoard, title=self.tr("search_kbd"), text="")

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
        self.focus_pane = "center"
        self.nav_stack = []
        self.populate_items(results, self.tr("search_res") + to_str(keyword), "plugins")

    def move_up(self):
        if self.view_style == "grid":
            if self.grid_index >= 4:
                self.grid_index -= 4
                self.render_current_items()
            return

        if self.focus_pane == "side":
            total_cats = len(self.main_cats_meta)
            if total_cats:
                self.active_cat_idx = (self.active_cat_idx - 1) % total_cats
                self.preview_active_category()
        else:
            total = len(self.current_items)
            if total:
                self.grid_index = (self.grid_index - 1) % total
                self.render_current_items()
                self.update_left_panel()

    def move_down(self):
        if self.view_style == "grid":
            if self.grid_index + 4 < len(self.current_items):
                self.grid_index += 4
                self.render_current_items()
            return

        if self.focus_pane == "side":
            total_cats = len(self.main_cats_meta)
            if total_cats:
                self.active_cat_idx = (self.active_cat_idx + 1) % total_cats
                self.preview_active_category()
        else:
            total = len(self.current_items)
            if total:
                self.grid_index = (self.grid_index + 1) % total
                self.render_current_items()
                self.update_left_panel()

    def move_left(self):
        if self.view_style == "grid":
            if self.grid_index + 1 < len(self.current_items):
                self.grid_index += 1
                self.render_current_items()
            return

        if self.focus_pane == "side":
            self.enter_center_pane()
        else:
            self.return_to_sidebar()

    def move_right(self):
        if self.view_style == "grid":
            if self.grid_index > 0:
                self.grid_index -= 1
                self.render_current_items()
            return

        if self.focus_pane == "center":
            self.return_to_sidebar()
        else:
            self.enter_center_pane()

    def ok_pressed(self):
        if self.view_style == "list" and self.focus_pane == "side":
            self.enter_center_pane()
            return

        if not self.current_items or self.grid_index < 0 or self.grid_index >= len(self.current_items):
            return
        entry = self.current_items[self.grid_index]
        data = entry["data"]
        title = to_str(entry["title"])
        sub_list = self.get_sub_items(data)

        if sub_list is not None:
            if len(sub_list) == 0:
                self.session.open(MessageBox, self.tr("empty_msg") % title, MessageBox.TYPE_INFO, timeout=4)
                return
            self.nav_stack.append((list(self.current_items), self["section_heading"].getText(), self.grid_index))
            self.populate_items(sub_list, title, entry["icon"])
            return

        cmd = data.get("cmd", "")
        if cmd:
            self.session.openWithCallback(self.after_install_cb, Console, title="Online4Tech: " + title, cmdlist=[to_str(cmd)])
        else:
            self.session.open(MessageBox, self.tr("no_cmd_msg") % title, MessageBox.TYPE_INFO, timeout=4)

    def refresh_server(self):
        self["center_header"].setText(self.tr("sync_msg"))
        self.cached_sys_info = self.get_sys_info_text()
        self.load_database(force=True)
        self["center_header"].setText(self.tr("search_hint"))

    def back_pressed(self):
        if self.view_style == "grid":
            self.toggle_view_mode()
            return

        if self.nav_stack:
            prev_items, prev_heading, prev_idx = self.nav_stack.pop()
            self.current_items = prev_items
            self.grid_index = prev_idx
            self.focus_pane = "center"
            self["section_heading"].setText(prev_heading)
            self.refresh_sidebar()
            self.render_current_items()
            self.update_left_panel()
            self.update_footer_hints()
        elif self.focus_pane == "center":
            self.return_to_sidebar()
        else:
            self.timer.stop()
            self.close()