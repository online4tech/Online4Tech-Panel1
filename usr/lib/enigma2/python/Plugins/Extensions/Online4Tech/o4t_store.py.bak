# -*- coding: utf-8 -*-
import io
import json
import math
import os
import re
import socket
import ssl
import sys
from datetime import datetime

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

from enigma import (
    eListboxPythonMultiContent,
    gFont,
    RT_HALIGN_RIGHT,
    RT_HALIGN_LEFT,
    RT_HALIGN_CENTER,
    RT_VALIGN_CENTER,
    addFont,
)
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
try:
    from enigma import BT_SCALE
except ImportError:
    BT_SCALE = 0
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap

PLUGIN_DIR = "/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech"
FONTS_DIR = os.path.join(PLUGIN_DIR, "fonts")
ICONS_DIR = os.path.join(PLUGIN_DIR, "icons")
DB_URL = "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/o4t_database.json"
CACHE_DB = "/tmp/o4t_database.json"

STORE_URL = "sllr.co/online4tech"
SUPPORT_PHONE = "01006699169"
ITEMS_PER_PAGE = 9

ARABIC_SECTIONS = {
    "online4tech_official": "Online4Tech الرسمي",
    "favourites": "المفضلة المختارة",
    "updated-dependencic": "تحديث الحزم والمكتبات",
    "backupimages": "باك اب الصور",
    "panels": "لوحات التحكم (Panels)",
    "plugins": "البلجنات (Plugins)",
    "novaler": "إضافات Novaler",
    "channels": "ملفات القنوات",
    "feeds": "الفيدات (Feeds)",
    "bootlogos": "شاشات الإقلاع",
    "spinners": "أيقونات التحميل",
    "tools": "أدوات الصيانة",
    "system": "إضافات النظام",
    "media": "الميديا و IPTV",
    "ciefp": "باقة Ciefp",
    "multiboot": "المالتي بوت (Multiboot)",
    "softcams": "السوفت كام (Softcams)",
    "backup": "نسخ احتياطي",
    "restore": "استعادة النسخ",
    "skins": "السكينات (Skins)",
    "images": "صور الإنيجما 2",
    "picons": "البيكونات (Picons)",
    "remove": "حذف الإضافات",
}

PACKAGE_TYPE_LABELS = {
    "online4tech_official": "حزمة رسمية • Online4Tech",
    "favourites": "إضافة مختارة • Enigma2",
    "panels": "لوحة تحكم وإضافات",
    "plugins": "بلجن إضافي • Enigma2",
    "channels": "ملف قنوات وباقات",
    "feeds": "مصدر تحديثات (Feed)",
    "bootlogos": "شاشة إقلاع (Bootlogo)",
    "spinners": "مؤشر تحميل (Spinner)",
    "tools": "أداة صيانة وإصلاح",
    "system": "إضافة نظام أساسية",
    "media": "مشغل وسائط و IPTV",
    "softcams": "محاكي شفرات (Softcam)",
    "skins": "واجهة عرض (FHD Skin)",
    "images": "صورة نظام كاملة",
    "picons": "حزمة شعارات قنوات",
    "remove": "أداة تنظيف وإزالة",
}

_PIXMAP_CACHE = {}


def ensure_fonts_loaded():
    loaded = set()
    candidates = [
        ("O4TArabic", ["Cairo-Bold.ttf", "Cairo-Regular.ttf", "Amiri-Bold.ttf", "Amiri-Regular.ttf"]),
        ("O4TRegular", ["Cairo-Regular.ttf", "Amiri-Regular.ttf", "Cairo-Bold.ttf"]),
    ]
    if not os.path.isdir(FONTS_DIR):
        return loaded
    for alias, files in candidates:
        for fname in files:
            fpath = os.path.join(FONTS_DIR, fname)
            if os.path.isfile(fpath) and os.path.getsize(fpath) > 0:
                try:
                    addFont(fpath, alias, 100, False)
                    loaded.add(alias)
                    break
                except Exception:
                    pass
    return loaded


def clean_text(txt):
    if not txt:
        return ""
    if not isinstance(txt, type(u"")):
        try:
            txt = txt.decode("utf-8", "ignore")
        except Exception:
            txt = str(txt)
    txt = re.sub(r"\(\s*\)", "", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def parse_item_name(raw_name):
    txt = clean_text(raw_name)
    m = re.search(r"\(([^)]*[\u0600-\u06FF][^)]*)\)", txt)
    if m:
        ar_desc = m.group(1).strip()
        title = (txt[:m.start()] + txt[m.end():]).strip(" -_")
        return (title if title else txt), ar_desc
    return txt, ""


def truncate_text(txt, max_len=36):
    if not txt or len(txt) <= max_len:
        return txt
    return txt[: max_len - 3].rstrip() + "..."


def get_device_info():
    py_ver = "%d.%d" % (sys.version_info[0], sys.version_info[1])
    ip = "Offline"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    image_name = "Enigma2"
    for p in ["/etc/issue", "/etc/version"]:
        if os.path.isfile(p):
            try:
                with io.open(p, "r", encoding="utf-8", errors="ignore") as f:
                    raw = f.read()
                    raw = re.sub(r"\\[a-zA-Z]", "", raw)
                    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
                    if lines:
                        image_name = lines[0][:22].upper()
                        break
            except Exception:
                pass

    now = datetime.now()
    clock_str = now.strftime("%I:%M %p").lstrip("0")
    date_str = now.strftime("%Y-%m-%d")
    return image_name, py_ver, ip, clock_str, date_str


def find_icon_path(icon_name):
    candidates = []
    if icon_name:
        candidates.append(os.path.join(ICONS_DIR, icon_name))
        candidates.append(os.path.join(PLUGIN_DIR, icon_name))
    candidates.append(os.path.join(PLUGIN_DIR, "logo.png"))
    candidates.append(os.path.join(PLUGIN_DIR, "plugin.png"))
    candidates.append(os.path.join(PLUGIN_DIR, "icon.png"))
    candidates.append(os.path.join(PLUGIN_DIR, "icon.png"))
    for path in candidates:
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            return path
    return None


def get_cached_pixmap(icon_name):
    path = find_icon_path(icon_name)
    if not path:
        return None
    if path not in _PIXMAP_CACHE:
        try:
            _PIXMAP_CACHE[path] = LoadPixmap(path, cached=True)
        except Exception:
            _PIXMAP_CACHE[path] = None
    return _PIXMAP_CACHE[path]


class Online4TechMenuList(MenuList):
    def __init__(self, list_items, font_name="Regular", font_size=24, item_height=64):
        MenuList.__init__(self, list_items, enableWrapAround=True, content=eListboxPythonMultiContent)
        self.l.setFont(0, gFont(font_name, font_size))
        self.l.setFont(1, gFont(font_name, max(18, font_size - 5)))
        self.l.setItemHeight(item_height)


def build_category_entry(title, count_num, icon_name=""):
    display_title = truncate_text(title, 24)
    count_str = str(count_num) if count_num is not None else ""
    px = get_cached_pixmap(icon_name)

    res = [(title, count_num, icon_name)]
    # Card Background & Bottom Divider
    res.append(
        MultiContentEntryText(
            pos=(4, 4),
            size=(417, 58),
            font=0,
            flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER,
            text="",
            color=0xFFFFFF,
            color_sel=0xF3D778,
            backcolor=0x162038,
            backcolor_sel=0x2B2412,
        )
    )
    # Right Icon Box
    res.append(
        MultiContentEntryText(
            pos=(366, 11),
            size=(44, 44),
            font=1,
            flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
            text="" if px else "◈",
            color=0xD4AF37,
            color_sel=0xF3D778,
            backcolor=0x0D1322,
            backcolor_sel=0x1C170B,
        )
    )
    if px:
        res.append(
            MultiContentEntryPixmapAlphaBlend(
                pos=(370, 15),
                size=(36, 36),
                png=px, flags=BT_SCALE,
            )
        )
    # Category Title (Right-aligned)
    res.append(
        MultiContentEntryText(
            pos=(78, 8),
            size=(278, 50),
            font=0,
            flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER,
            text=display_title,
            color=0xE2E8F0,
            color_sel=0xF3D778,
        )
    )
    # Left Count Badge
    if count_str:
        res.append(
            MultiContentEntryText(
                pos=(12, 16),
                size=(56, 34),
                font=1,
                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                text=count_str,
                color=0x94A3B8,
                color_sel=0x0B0D14,
                backcolor=0x0D1322,
                backcolor_sel=0xD4AF37,
            )
        )
    return res


def build_item_entry(title, subtitle, installed=False, icon_name=""):
    display_title = truncate_text(title, 36)
    display_sub = truncate_text(subtitle, 44)
    px = get_cached_pixmap(icon_name)
    status_txt = "✓ مثبت" if installed else "متاح"
    status_col = 0x22C55E if installed else 0x94A3B8

    res = [(title, subtitle, installed, icon_name)]
    # Card Background
    res.append(
        MultiContentEntryText(
            pos=(4, 4),
            size=(692, 74),
            font=0,
            flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER,
            text="",
            color=0xFFFFFF,
            color_sel=0xF3D778,
            backcolor=0x162038,
            backcolor_sel=0x2B2412,
        )
    )
    # Right Icon Frame
    res.append(
        MultiContentEntryText(
            pos=(624, 11),
            size=(60, 60),
            font=0,
            flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
            text="" if px else "★",
            color=0xD4AF37,
            color_sel=0xF3D778,
            backcolor=0x0D1322,
            backcolor_sel=0x1C170B,
        )
    )
    if px:
        res.append(
            MultiContentEntryPixmapAlphaBlend(
                pos=(630, 17),
                size=(48, 48),
                png=px, flags=BT_SCALE,
            )
        )
    # Left Status Pill
    res.append(
        MultiContentEntryText(
            pos=(14, 21),
            size=(112, 40),
            font=1,
            flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
            text=status_txt,
            color=status_col,
            color_sel=0x22C55E if installed else 0xF3D778,
            backcolor=0x0D1322,
            backcolor_sel=0x1C170B,
        )
    )
    # Main Title (Line 1)
    res.append(
        MultiContentEntryText(
            pos=(136, 8),
            size=(476, 36),
            font=0,
            flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER,
            text=display_title,
            color=0xF8FAFC,
            color_sel=0xF3D778,
        )
    )
    # Clean Arabic Subtitle (Line 2)
    res.append(
        MultiContentEntryText(
            pos=(136, 42),
            size=(476, 30),
            font=1,
            flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER,
            text=display_sub,
            color=0x38BDF8,
            color_sel=0xE2E8F0,
        )
    )
    return res


class Online4TechStoreScreen(Screen):
    skin = """
    <screen name="Online4TechStoreScreen" position="0,0" size="1920,1080" title="Online4Tech Store v7.5 Gold" backgroundColor="#0a0e17" flags="wfNoBorder">
        <!-- Top Header Bar -->
        <eLabel position="28,20" size="1864,118" backgroundColor="#111827" zPosition="-10" />
        <eLabel position="28,20" size="1864,3" backgroundColor="#d4af37" zPosition="-5" />
        <eLabel position="28,136" size="1864,2" backgroundColor="#243049" zPosition="-5" />

        <!-- Right Header: Brand & Support Card -->
        <widget name="brand_logo" position="1786,34" size="88,88" alphatest="blend" scale="1" zPosition="5" />
        <eLabel text="ONLINE4TECH STORE" position="1385,30" size="385,42" font="Regular;31" halign="right" foregroundColor="#f3d778" backgroundColor="#111827" transparent="1" zPosition="5" />
        <eLabel text="VU+ • DREAMBOX • ENIGMA2 GOLD v7.5" position="1340,70" size="430,26" font="Regular;18" halign="right" foregroundColor="#38bdf8" backgroundColor="#111827" transparent="1" zPosition="5" />
        <eLabel position="1340,98" size="430,30" backgroundColor="#1f2937" zPosition="-6" />
        <widget name="brand_sub" position="1345,99" size="420,28" font="Regular;19" halign="center" noWrap="1" foregroundColor="#f3d778" backgroundColor="#1f2937" transparent="1" zPosition="5" />

        <!-- Center Header: Active Section Title -->
        <widget name="top_title" position="640,34" size="680,44" font="Regular;31" halign="center" foregroundColor="#f3d778" backgroundColor="#111827" transparent="1" zPosition="5" />
        <widget name="top_subtitle" position="640,84" size="680,34" font="Regular;21" halign="center" foregroundColor="#94a3b8" backgroundColor="#111827" transparent="1" zPosition="5" />

        <!-- Left Header Card 1: Clock & Date -->
        <eLabel position="46,32" size="255,92" backgroundColor="#162038" zPosition="-8" />
        <eLabel position="46,32" size="255,2" backgroundColor="#334155" zPosition="-5" />
        <widget name="clock_lbl" position="54,40" size="239,42" font="Regular;30" halign="center" foregroundColor="#ffffff" backgroundColor="#162038" transparent="1" zPosition="5" />
        <widget name="date_lbl" position="54,84" size="239,30" font="Regular;19" halign="center" foregroundColor="#d4af37" backgroundColor="#162038" transparent="1" zPosition="5" />

        <!-- Left Header Card 2: Receiver & Python Info -->
        <eLabel position="315,32" size="305,92" backgroundColor="#162038" zPosition="-8" />
        <eLabel position="315,32" size="305,2" backgroundColor="#334155" zPosition="-5" />
        <widget name="dev_info_top" position="325,42" size="285,36" font="Regular;23" halign="center" foregroundColor="#38bdf8" backgroundColor="#162038" transparent="1" zPosition="5" />
        <widget name="dev_info_bot" position="325,82" size="285,32" font="Regular;19" halign="center" foregroundColor="#cbd5e1" backgroundColor="#162038" transparent="1" zPosition="5" />

        <!-- Column 1 (Right): Categories Sidebar (x: 1437..1892) -->
        <eLabel position="1437,154" size="455,834" backgroundColor="#111827" zPosition="-10" />
        <eLabel position="1437,154" size="455,3" backgroundColor="#d4af37" zPosition="-5" />
        <widget name="cats_header" position="1455,168" size="418,44" font="Regular;28" halign="right" foregroundColor="#f3d778" backgroundColor="#111827" transparent="1" zPosition="5" />
        <eLabel position="1455,220" size="418,2" backgroundColor="#243049" zPosition="-5" />
        <widget name="cat_list" position="1452,232" size="425,726" scrollbarMode="showNever" backgroundColor="#111827" backgroundColorSelected="#2b2412" foregroundColorSelected="#f3d778" transparent="1" zPosition="5" />

        <!-- Column 2 (Center): Items & Packages List (x: 682..1417) -->
        <eLabel position="682,154" size="735,834" backgroundColor="#111827" zPosition="-10" />
        <eLabel position="682,154" size="735,3" backgroundColor="#38bdf8" zPosition="-5" />
        <widget name="items_header" position="940,168" size="455,44" font="Regular;27" halign="right" foregroundColor="#f8fafc" backgroundColor="#111827" transparent="1" zPosition="5" />
        <widget name="page_info" position="702,172" size="230,36" font="Regular;21" halign="left" foregroundColor="#d4af37" backgroundColor="#111827" transparent="1" zPosition="5" />
        <eLabel position="702,220" size="695,2" backgroundColor="#243049" zPosition="-5" />
        <widget name="item_list" position="698,232" size="700,738" scrollbarMode="showNever" backgroundColor="#111827" backgroundColorSelected="#2b2412" foregroundColorSelected="#f3d778" transparent="1" zPosition="5" />

        <!-- Column 3 (Left): Preview & Details Card (x: 28..662) -->
        <eLabel position="28,154" size="634,834" backgroundColor="#111827" zPosition="-10" />
        <eLabel position="28,154" size="634,3" backgroundColor="#d4af37" zPosition="-5" />

        <!-- Top Status Dot Indicator -->
        <eLabel position="54,174" size="26,26" backgroundColor="#162038" zPosition="-8" />
        <widget name="status_dot" position="54,172" size="26,28" font="Regular;22" halign="center" foregroundColor="#22c55e" backgroundColor="#162038" transparent="1" zPosition="5" />

        <!-- Centered Icon Frame -->
        <eLabel position="255,182" size="180,180" backgroundColor="#162038" zPosition="-8" />
        <eLabel position="255,182" size="180,2" backgroundColor="#d4af37" zPosition="-5" />
        <widget name="preview_icon" position="275,202" size="140,140" alphatest="blend" scale="1" zPosition="5" />

        <!-- Item Title & Install Status -->
        <widget name="detail_title" position="48,378" size="594,68" font="Regular;28" halign="center" foregroundColor="#ffffff" backgroundColor="#111827" transparent="1" zPosition="5" />
        <widget name="detail_status" position="48,450" size="594,36" font="Regular;22" halign="center" foregroundColor="#22c55e" backgroundColor="#111827" transparent="1" zPosition="5" />
        <eLabel position="58,496" size="574,2" backgroundColor="#243049" zPosition="-5" />

        <!-- Structured Details Box (Pure Arabic Labels to prevent BiDi scrambling) -->
        <eLabel position="52,510" size="586,155" backgroundColor="#162038" zPosition="-8" />
        <widget name="meta_cat" position="68,520" size="554,36" font="Regular;22" halign="right" foregroundColor="#f3d778" backgroundColor="#162038" transparent="1" zPosition="5" />
        <widget name="meta_type" position="68,566" size="554,36" font="Regular;22" halign="right" foregroundColor="#38bdf8" backgroundColor="#162038" transparent="1" zPosition="5" />
        <widget name="meta_source" position="68,612" size="554,36" font="Regular;21" halign="right" foregroundColor="#cbd5e1" backgroundColor="#162038" transparent="1" zPosition="5" />

        <!-- Item Description Area -->
        <widget name="detail_desc" position="58,682" size="574,158" font="Regular;23" halign="right" foregroundColor="#e2e8f0" backgroundColor="#111827" transparent="1" zPosition="5" />

        <!-- Gold CTA Button inside Preview Column -->
        <eLabel position="58,862" size="574,94" backgroundColor="#d4af37" zPosition="-8" />
        <widget name="action_cta" position="72,874" size="546,40" font="Regular;27" halign="center" foregroundColor="#0a0e17" backgroundColor="#d4af37" transparent="1" zPosition="5" />
        <widget name="action_sub" position="72,916" size="546,30" font="Regular;20" halign="center" foregroundColor="#1e1b10" backgroundColor="#d4af37" transparent="1" zPosition="5" />

        <!-- Bottom Color Buttons Bar (Preserving Existing Button Order & Functionality) -->
        <eLabel position="28,1004" size="1864,58" backgroundColor="#111827" zPosition="-10" />
        <eLabel position="28,1004" size="1864,2" backgroundColor="#243049" zPosition="-5" />

        <!-- Red Button: Back / Exit -->
        <eLabel position="1610,1013" size="265,40" backgroundColor="#162038" zPosition="-6" />
        <eLabel text="●" position="1835,1014" size="30,38" font="Regular;24" halign="center" foregroundColor="#ef4444" backgroundColor="#162038" transparent="1" zPosition="5" />
        <widget name="key_red" position="1618,1015" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#162038" transparent="1" zPosition="5" />

        <!-- Green Button: Install / Open -->
        <eLabel position="1325,1013" size="265,40" backgroundColor="#162038" zPosition="-6" />
        <eLabel text="●" position="1550,1014" size="30,38" font="Regular;24" halign="center" foregroundColor="#22c55e" backgroundColor="#162038" transparent="1" zPosition="5" />
        <widget name="key_green" position="1333,1015" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#162038" transparent="1" zPosition="5" />

        <!-- Yellow Button: Uninstall -->
        <eLabel position="1040,1013" size="265,40" backgroundColor="#162038" zPosition="-6" />
        <eLabel text="●" position="1265,1014" size="30,38" font="Regular;24" halign="center" foregroundColor="#eab308" backgroundColor="#162038" transparent="1" zPosition="5" />
        <widget name="key_yellow" position="1048,1015" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#162038" transparent="1" zPosition="5" />

        <!-- Blue Button: Refresh Server -->
        <eLabel position="755,1013" size="265,40" backgroundColor="#162038" zPosition="-6" />
        <eLabel text="●" position="980,1014" size="30,38" font="Regular;24" halign="center" foregroundColor="#3b82f6" backgroundColor="#162038" transparent="1" zPosition="5" />
        <widget name="key_blue" position="763,1015" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#162038" transparent="1" zPosition="5" />

        <!-- Left Navigation Hint -->
        <widget name="footer_hint" position="48,1014" size="685,38" font="Regular;20" halign="left" valign="center" foregroundColor="#94a3b8" backgroundColor="#111827" transparent="1" zPosition="5" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        loaded_fonts = ensure_fonts_loaded()
        self.ui_font = "O4TArabic" if "O4TArabic" in loaded_fonts else ("O4TRegular" if "O4TRegular" in loaded_fonts else "Regular")

        self.db_data = {}
        self.main_sections = []
        self.current_cat_idx = 0
        self.current_section_key = ""
        self.current_section_title = ""
        self.current_section_icon = ""
        self.current_items = []
        self.focus_pane = "cats"
        self.nav_stack = []

        img_name, py_ver, ip, clock_str, date_str = get_device_info()

        self["brand_logo"] = Pixmap()
        self["brand_sub"] = Label("%s  •  %s" % (SUPPORT_PHONE, STORE_URL))
        self["top_title"] = Label("متجر Online4Tech الرسمي")
        self["top_subtitle"] = Label("جاري تحميل قاعدة البيانات...")

        self["clock_lbl"] = Label(clock_str)
        self["date_lbl"] = Label(date_str)
        self["dev_info_top"] = Label(img_name)
        self["dev_info_bot"] = Label("Py %s  •  IP: %s" % (py_ver, ip))

        self["cats_header"] = Label("أقسام المتجر")
        self["cat_list"] = Online4TechMenuList([], font_name=self.ui_font, font_size=23, item_height=64)

        self["items_header"] = Label("الحزم والإضافات")
        self["page_info"] = Label("0 عنصر")
        self["item_list"] = Online4TechMenuList([], font_name=self.ui_font, font_size=24, item_height=82)

        self["status_dot"] = Label("●")
        self["preview_icon"] = Pixmap()
        self["detail_title"] = Label("Online4Tech v7.5 Gold")
        self["detail_status"] = Label("جاهز للاستعراض")
        self["meta_cat"] = Label("القسم: الرئيسية")
        self["meta_type"] = Label("النوع: متجر إضافات متكامل")
        self["meta_source"] = Label("المصدر: مستودع Online4Tech السحابي")
        self["detail_desc"] = Label("تنقل بين الأقسام على اليمين أو اضغط يسار للدخول إلى قائمة الإضافات وتثبيتها مباشرة.")
        self["action_cta"] = Label("تثبيت / فتح  •  OK")
        self["action_sub"] = Label("الأخضر: تنفيذ  |  الأصفر: إزالة  |  الأزرق: تحديث")

        self["key_red"] = Label("رجوع / إغلاق")
        self["key_green"] = Label("تثبيت / فتح")
        self["key_yellow"] = Label("حذف / إزالة")
        self["key_blue"] = Label("تحديث المصدر")
        self["footer_hint"] = Label("التركيز: الأقسام  |  يسار: العناصر  |  OK: اختيار")

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions", "ChannelSelectBaseActions"],
            {
                "ok": self.ok_pressed,
                "cancel": self.back_pressed,
                "red": self.back_pressed,
                "green": self.ok_pressed,
                "yellow": self.remove_pressed,
                "blue": self.refresh_db,
                "up": self.move_up,
                "down": self.move_down,
                "left": self.focus_items_pane,
                "right": self.focus_cats_pane,
                "nextBouquet": self.page_down,
                "prevBouquet": self.page_up,
            },
            -1,
        )

        self.onLayoutFinish.append(self.init_screen)

    def init_screen(self):
        brand_img = find_icon_path("logo.png")
        if brand_img and self["brand_logo"].instance:
            try:
                self["brand_logo"].instance.setScale(1)
            except Exception:
                pass
            try:
                self["brand_logo"].instance.setScale(1)
            except Exception:
                pass
            self["brand_logo"].instance.setPixmapFromFile(brand_img)
        self.load_database(force=False)

    def get_section_arabic_title(self, sec_obj):
        sec_key = sec_obj.get("section", "")
        if sec_key in ARABIC_SECTIONS:
            return ARABIC_SECTIONS[sec_key]
        raw_t = clean_text(sec_obj.get("title", sec_key))
        _, ar_sub = parse_item_name(raw_t)
        return ar_sub if ar_sub else raw_t

    def load_database(self, force=False):
        try:
            if force or not os.path.exists(CACHE_DB) or os.path.getsize(CACHE_DB) == 0:
                self["top_subtitle"].setText("جاري الاتصال بسيرفر Online4Tech...")
                req = Request(DB_URL, headers={"User-Agent": "Online4Tech-Enigma2-v7.5"})
                ctx = ssl._create_unverified_context() if hasattr(ssl, "_create_unverified_context") else None
                resp = urlopen(req, timeout=20, context=ctx) if ctx else urlopen(req, timeout=20)
                raw = resp.read().decode("utf-8", errors="ignore")
                with io.open(CACHE_DB, "w", encoding="utf-8") as f:
                    f.write(raw)

            with io.open(CACHE_DB, "r", encoding="utf-8", errors="ignore") as f:
                self.db_data = json.load(f)

            self.main_sections = self.db_data.get("main", [])
            self.nav_stack = []
            self.current_cat_idx = 0
            self.populate_categories()
            if self.main_sections:
                first_sec = self.main_sections[0]
                self.open_section(
                    first_sec.get("section", ""),
                    self.get_section_arabic_title(first_sec),
                    icon_name=first_(sec.get("icon") or (sec.get("section", "") + ".png")),
                    push_history=False,
                )
            self["top_subtitle"].setText("المتجر متصل • %d قسم رئيسي" % len(self.main_sections))
        except Exception as e:
            self["top_subtitle"].setText("تعذر الاتصال بالسيرفر")
            self["detail_desc"].setText("تأكد من اتصال الإنترنت بالريسيفر ثم اضغط الزر الأزرق للتحديث.\n%s" % clean_text(str(e)))

    def refresh_db(self):
        self.load_database(force=True)

    def populate_categories(self):
        entries = []
        for sec in self.main_sections:
            sec_key = sec.get("section", "")
            ar_title = self.get_section_arabic_title(sec)
            sec_items = self.db_data.get(sec_key, [])
            cnt = len(sec_items) if isinstance(sec_items, list) else 0
            entries.append(build_category_entry(ar_title, cnt, (sec.get("icon") or (sec.get("section", "") + ".png"))))
        self["cat_list"].setList(entries)
        if entries:
            self["cat_list"].moveToIndex(0)

    def update_page_badge(self):
        total = len(self.current_items)
        if total == 0:
            self["page_info"].setText("0 عنصر")
            return
        idx = self["item_list"].getSelectedIndex() or 0
        total_pages = max(1, int(math.ceil(float(total) / ITEMS_PER_PAGE)))
        cur_page = min(total_pages, (idx // ITEMS_PER_PAGE) + 1)
        self["page_info"].setText("%d عنصر • صفحة %d / %d" % (total, cur_page, total_pages))

    def open_section(self, section_key, title, icon_name="", push_history=True):
        if push_history and self.current_section_key:
            self.nav_stack.append((
                self.current_section_key,
                self.current_section_title,
                self.current_section_icon,
                list(self.current_items),
                self["item_list"].getSelectedIndex() or 0,
            ))

        self.current_section_key = section_key
        self.current_section_title = title
        self.current_section_icon = icon_name
        raw_items = self.db_data.get(section_key, [])
        self.current_items = raw_items if isinstance(raw_items, list) else []

        self["top_title"].setText(title or "Online4Tech Store")
        self["items_header"].setText(title or "الحزم والإضافات")

        list_entries = []
        for it in self.current_items:
            if "section" in it:
                sub_title = self.get_section_arabic_title(it)
                sub_key = it.get("section", "")
                sub_count = len(self.db_data.get(sub_key, []))
                sub_icon = (it.get("icon") or (it.get("section", "") + ".png") or icon_name)
                list_entries.append(build_item_entry(sub_title, "قسم فرعي • يحتوي على %d عنصر" % sub_count, False, sub_icon))
            else:
                clean_title, ar_desc = parse_item_name(it.get("name", "حزمة"))
                path = it.get("path", "")
                installed = bool(path and os.path.exists(path))
                sub_txt = ar_desc if ar_desc else ("قسم: %s" % title)
                item_icon = (it.get("icon") or (it.get("section", "") + ".png") or icon_name)
                list_entries.append(build_item_entry(clean_title, sub_txt, installed, item_icon))

        self["item_list"].setList(list_entries)
        if list_entries:
            self["item_list"].moveToIndex(0)
        self.update_page_badge()
        self.update_preview(icon_override=icon_name)

    def update_preview(self, icon_override=""):
        self.update_page_badge()
        idx = self["item_list"].getSelectedIndex()
        if idx is None or idx < 0 or idx >= len(self.current_items):
            self["detail_title"].setText(self.current_section_title or "Online4Tech")
            self["detail_status"].setText("لا توجد عناصر في هذا القسم")
            self["meta_cat"].setText("القسم: %s" % (self.current_section_title or "غير محدد"))
            self["meta_type"].setText("النوع: قسم فارغ")
            self["meta_source"].setText("المصدر: مستودع Online4Tech")
            self["detail_desc"].setText("اختر قسماً آخر من القائمة اليمنى أو اضغط الزر الأزرق لتحديث البيانات.")
            return

        item = self.current_items[idx]
        pkg_type = PACKAGE_TYPE_LABELS.get(self.current_section_key, "حزمة إضافية • Enigma2")

        if "section" in item:
            title = self.get_section_arabic_title(item)
            sub_key = item.get("section", "")
            cnt = len(self.db_data.get(sub_key, []))
            self["detail_title"].setText(truncate_text(title, 34))
            self["detail_status"].setText("قسم فرعي • %d عنصر متاح" % cnt)
            self["meta_cat"].setText("القسم الرئيسي: %s" % self.current_section_title)
            self["meta_type"].setText("النوع: مجلد أقسام فرعية")
            self["meta_source"].setText("المصدر: Online4Tech Official")
            self["detail_desc"].setText("اضغط OK أو الزر الأخضر لفتح هذا القسم واستعراض جميع الحزم والإضافات المتوفرة بداخله.")
            self["action_cta"].setText("فتح القسم الفرعي  •  OK")
            self["action_sub"].setText("استعراض %d عنصر" % cnt)
            icon_file = find_icon_path((item.get("icon") or (item.get("section", "") + ".png") or icon_override) or self.current_section_icon)
        else:
            clean_title, ar_desc = parse_item_name(item.get("name", "حزمة"))
            path = item.get("path", "")
            installed = bool(path and os.path.exists(path))
            has_remove = bool(item.get("remove_cmd"))

            self["detail_title"].setText(truncate_text(clean_title, 34))
            self["detail_status"].setText("✓ مثبتة على جهازك وجاهزة" if installed else "متاحة للتثبيت المباشر")
            self["meta_cat"].setText("القسم: %s" % self.current_section_title)
            self["meta_type"].setText("النوع: %s" % pkg_type)
            self["meta_source"].setText("الإزالة التلقائية: %s" % ("مدعومة بالزر الأصفر" if has_remove else "غير متوفرة"))

            if ar_desc:
                desc_body = "الوصف: %s\n\nاضغط زر موافق أو الزر الأخضر لبدء التحميل والتثبيت التلقائي على الجهاز." % ar_desc
            else:
                desc_body = "حزمة جاهزة للتحميل والتثبيت المباشر من خوادم Online4Tech المتوافقة مع صورة جهازك."
            self["detail_desc"].setText(desc_body)
            self["action_cta"].setText("إعادة تثبيت / تحديث  •  OK" if installed else "تثبيت الآن  •  OK")
            self["action_sub"].setText("الأخضر: تثبيت  |  الأصفر: إزالة  |  EXIT: رجوع")
            icon_file = find_icon_path((item.get("icon") or (item.get("section", "") + ".png") or icon_override) or self.current_section_icon)

        if icon_file and self["preview_icon"].instance:
            try:
                self["preview_icon"].instance.setScale(1)
            except Exception:
                pass
            try:
                self["preview_icon"].instance.setScale(1)
            except Exception:
                pass
            self["preview_icon"].instance.setPixmapFromFile(icon_file)

    def move_up(self):
        if self.focus_pane == "cats":
            self["cat_list"].up()
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.main_sections):
                self.current_cat_idx = idx
                sec = self.main_sections[idx]
                self.open_section(
                    sec.get("section", ""),
                    self.get_section_arabic_title(sec),
                    icon_name=(sec.get("icon") or (sec.get("section", "") + ".png")),
                    push_history=False,
                )
        else:
            self["item_list"].up()
            self.update_preview()

    def move_down(self):
        if self.focus_pane == "cats":
            self["cat_list"].down()
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.main_sections):
                self.current_cat_idx = idx
                sec = self.main_sections[idx]
                self.open_section(
                    sec.get("section", ""),
                    self.get_section_arabic_title(sec),
                    icon_name=(sec.get("icon") or (sec.get("section", "") + ".png")),
                    push_history=False,
                )
        else:
            self["item_list"].down()
            self.update_preview()

    def page_up(self):
        if self.focus_pane == "cats":
            self["cat_list"].pageUp()
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.main_sections):
                self.current_cat_idx = idx
                sec = self.main_sections[idx]
                self.open_section(sec.get("section", ""), self.get_section_arabic_title(sec), icon_name=(sec.get("icon") or (sec.get("section", "") + ".png")), push_history=False)
        else:
            self["item_list"].pageUp()
            self.update_preview()

    def page_down(self):
        if self.focus_pane == "cats":
            self["cat_list"].pageDown()
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.main_sections):
                self.current_cat_idx = idx
                sec = self.main_sections[idx]
                self.open_section(sec.get("section", ""), self.get_section_arabic_title(sec), icon_name=(sec.get("icon") or (sec.get("section", "") + ".png")), push_history=False)
        else:
            self["item_list"].pageDown()
            self.update_preview()

    def focus_cats_pane(self):
        self.focus_pane = "cats"
        self["footer_hint"].setText("التركيز: الأقسام  |  OK: فتح  |  يسار: العناصر  |  EXIT: رجوع")

    def focus_items_pane(self):
        self.focus_pane = "items"
        self["footer_hint"].setText("التركيز: العناصر  |  OK: تثبيت  |  يمين: الأقسام  |  EXIT: رجوع")

    def ok_pressed(self):
        if self.focus_pane == "cats":
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.main_sections):
                self.current_cat_idx = idx
                sec = self.main_sections[idx]
                self.open_section(
                    sec.get("section", ""),
                    self.get_section_arabic_title(sec),
                    icon_name=(sec.get("icon") or (sec.get("section", "") + ".png")),
                    push_history=True,
                )
                self.focus_items_pane()
            return

        idx = self["item_list"].getSelectedIndex()
        if idx is None or idx < 0 or idx >= len(self.current_items):
            return
        item = self.current_items[idx]
        if "section" in item:
            self.open_section(
                item.get("section", ""),
                self.get_section_arabic_title(item),
                icon_name=item.get("icon", "") or self.current_section_icon,
                push_history=True,
            )
        else:
            cmd = item.get("cmd", "")
            clean_title, _ = parse_item_name(item.get("name", "Package"))
            if cmd:
                self.session.open(Console, title="Online4Tech - %s" % clean_title, cmdlist=[cmd], closeOnSuccess=False)

    def remove_pressed(self):
        idx = self["item_list"].getSelectedIndex()
        if idx is None or idx < 0 or idx >= len(self.current_items):
            return
        item = self.current_items[idx]
        rem_cmd = item.get("remove_cmd", "")
        clean_title, _ = parse_item_name(item.get("name", "Package"))
        if rem_cmd:
            self.session.open(Console, title="Online4Tech Remove - %s" % clean_title, cmdlist=[rem_cmd], closeOnSuccess=False)
        else:
            self.session.open(MessageBox, "لا يوجد أمر حذف تلقائي متاح لهذا العنصر.", MessageBox.TYPE_INFO, timeout=3)

    def back_pressed(self):
        if self.nav_stack:
            prev_key, prev_title, prev_icon, prev_items, prev_idx = self.nav_stack.pop()
            self.current_section_key = prev_key
            self.current_section_title = prev_title
            self.current_section_icon = prev_icon
            self.current_items = prev_items
            self["top_title"].setText(prev_title or "Online4Tech Store")
            self["items_header"].setText(prev_title or "الحزم والإضافات")

            entries = []
            for it in prev_items:
                if "section" in it:
                    sub_t = self.get_section_arabic_title(it)
                    cnt = len(self.db_data.get(it.get("section", ""), []))
                    entries.append(build_item_entry(sub_t, "قسم فرعي • يحتوي على %d عنصر" % cnt, False, it.get("icon", "") or prev_icon))
                else:
                    nm, ar_d = parse_item_name(it.get("name", "حزمة"))
                    pth = it.get("path", "")
                    inst = bool(pth and os.path.exists(pth))
                    entries.append(build_item_entry(nm, ar_d if ar_d else ("قسم: %s" % prev_title), inst, it.get("icon", "") or prev_icon))

            self["item_list"].setList(entries)
            if entries:
                self["item_list"].moveToIndex(min(prev_idx, len(entries) - 1))
            self.update_preview(icon_override=prev_icon)
        else:
            self.close()