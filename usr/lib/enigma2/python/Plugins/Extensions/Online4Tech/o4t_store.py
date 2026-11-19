# -*- coding: utf-8 -*-
import io
import json
import math
import os
import re
import socket
import ssl
import struct
import sys
import zlib
from datetime import datetime

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

from enigma import (
    eListboxPythonMultiContent,
    gFont,
    gRGB,
    RT_HALIGN_RIGHT,
    RT_HALIGN_LEFT,
    RT_HALIGN_CENTER,
    RT_VALIGN_CENTER,
    addFont,
)

try:
    from enigma import BT_SCALE
except ImportError:
    BT_SCALE = 0

from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
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
PREFS_FILE = "/etc/enigma2/o4t_store_prefs.json"
DB_URL = "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/o4t_database.json"
CACHE_DB = "/tmp/o4t_database.json"

STORE_URL = "sllr.co/online4tech"
SUPPORT_PHONE = "01006699169"
ITEMS_PER_PAGE = 9

DEFAULT_PREFS = {
    "lang": "ar",
    "font_family": "Cairo",
    "font_scale": 0,
}

FONT_FAMILIES = [
    ("Cairo", "Cairo (خط القاهرة العصري)", "Cairo (Modern Sans)"),
    ("Amiri", "Amiri (خط أميري الكلاسيكي)", "Amiri (Classic Serif)"),
    ("System", "خط النظام الافتراضي", "System Default Font"),
]

FONT_SCALES = [
    (-2, "صغير (-2)", "Small (-2)"),
    (0, "قياسي (0)", "Normal (0)"),
    (2, "كبير (+2)", "Large (+2)"),
    (4, "كبير جداً (+4)", "Extra Large (+4)"),
]

MASTER_CATEGORIES = [
    {
        "id": "online4tech_official",
        "title_ar": "Online4Tech الرسمي",
        "title_en": "Online4Tech Official",
        "icon": "online4tech_official.png",
        "sections": ["online4tech_official"],
    },
    {
        "id": "favourites",
        "title_ar": "المفضلة المختارة",
        "title_en": "Selected Favourites",
        "icon": "favourites.png",
        "sections": ["favourites"],
    },
    {
        "id": "grp_plugins",
        "title_ar": "البلجنات ولوحات التحكم",
        "title_en": "Plugins & Control Panels",
        "icon": "plugins.png",
        "sections": ["panels", "plugins", "novaler", "ciefp"],
    },
    {
        "id": "grp_cams",
        "title_ar": "السوفت كام والفيدات",
        "title_en": "Softcams & Feeds",
        "icon": "softcams.png",
        "sections": ["softcams", "feeds"],
    },
    {
        "id": "grp_media",
        "title_ar": "القنوات والميديا (IPTV)",
        "title_en": "Channels & Media (IPTV)",
        "icon": "media.png",
        "sections": ["channels", "media", "picons"],
    },
    {
        "id": "grp_skins",
        "title_ar": "السكينات والمظهر",
        "title_en": "Skins & Appearance",
        "icon": "skins.png",
        "sections": ["skins", "bootlogos", "spinners"],
    },
    {
        "id": "grp_images",
        "title_ar": "الصور والمالتي بوت",
        "title_en": "Images & Multiboot",
        "icon": "images.png",
        "sections": ["images", "backupimages", "multiboot"],
    },
    {
        "id": "grp_tools",
        "title_ar": "الصيانة والنسخ والحذف",
        "title_en": "Maintenance & Cleanup",
        "icon": "tools.png",
        "sections": ["tools", "system", "updated-dependencic", "backup", "restore", "remove"],
    },
]

SECTION_LABELS = {
    "online4tech_official": ("Online4Tech الرسمي", "Online4Tech Official"),
    "favourites": ("المفضلة المختارة", "Selected Favourites"),
    "updated-dependencic": ("تحديث الحزم والمكتبات", "Dependencies & Libraries"),
    "backupimages": ("باك أب الصور", "Backup Images"),
    "panels": ("لوحات التحكم (Panels)", "Control Panels"),
    "plugins": ("البلجنات (Plugins)", "Enigma2 Plugins"),
    "novaler": ("إضافات Novaler", "Novaler Addons"),
    "channels": ("ملفات القنوات", "Channel Lists & Bouquets"),
    "feeds": ("الفيدات (Feeds)", "Update Feeds"),
    "bootlogos": ("شاشات الإقلاع", "Bootlogos"),
    "spinners": ("أيقونات التحميل", "Loading Spinners"),
    "tools": ("أدوات الصيانة", "Maintenance Tools"),
    "system": ("إضافات النظام", "System Extensions"),
    "media": ("الميديا و IPTV", "Media & IPTV Players"),
    "ciefp": ("باقة Ciefp", "Ciefp Settings & Plugins"),
    "multiboot": ("المالتي بوت (Multiboot)", "Multiboot Managers"),
    "softcams": ("السوفت كام (Softcams)", "Softcams & Emulators"),
    "backup": ("النسخ الاحتياطي", "System Backup"),
    "restore": ("استعادة النسخ", "Restore Backups"),
    "skins": ("السكينات (Skins)", "FHD Skins"),
    "images": ("صور Enigma2 الخام", "Enigma2 Clean Images"),
    "picons": ("البيكونات (Picons)", "Channel Picons"),
    "remove": ("حذف الإضافات", "Uninstall & Cleanup"),
}

PACKAGE_TYPE_LABELS = {
    "online4tech_official": ("حزمة رسمية • Online4Tech", "Official Package • Online4Tech"),
    "favourites": ("إضافة مختارة • Enigma2", "Curated Addon • Enigma2"),
    "panels": ("لوحة تحكم وإضافات", "Control Panel & Downloader"),
    "plugins": ("بلجن إضافي • Enigma2", "Extension Plugin • Enigma2"),
    "channels": ("ملف قنوات وباقات", "Channel List & Bouquets"),
    "feeds": ("مصدر تحديثات (Feed)", "Package Repository Feed"),
    "bootlogos": ("شاشة إقلاع (Bootlogo)", "Bootlogo Screen"),
    "spinners": ("مؤشر تحميل (Spinner)", "UI Loading Spinner"),
    "tools": ("أداة صيانة وإصلاح", "System Utility Tool"),
    "system": ("إضافة نظام أساسية", "Core System Module"),
    "media": ("مشغل وسائط و IPTV", "Media & IPTV Streamer"),
    "softcams": ("محاكي شفرات (Softcam)", "Softcam Emulator"),
    "skins": ("واجهة عرض (FHD Skin)", "Full HD Skin"),
    "images": ("صورة نظام كاملة", "Full Firmware Image"),
    "picons": ("حزمة شعارات قنوات", "Channel Logo Pack"),
    "remove": ("أداة تنظيف وإزالة", "Cleanup & Removal Script"),
}

UI_STRINGS = {
    "store_title": ("متجر Online4Tech الرسمي", "Online4Tech Official Store"),
    "loading_db": ("جارٍ تحميل قاعدة البيانات...", "Loading store database..."),
    "connecting_db": ("جارٍ الاتصال بخادم Online4Tech...", "Connecting to Online4Tech server..."),
    "connected_summary": (
        "المتجر متصل  •  %d أقسام رئيسية  (%d حزمة)",
        "Store Connected  •  %d Main Categories  (%d Packages)",
    ),
    "conn_error": ("تعذّر الاتصال بالخادم", "Unable to reach server"),
    "conn_error_desc": (
        "تأكّد من اتصال الجهاز بالإنترنت ثم اضغط الزر الأزرق للتحديث.",
        "Please check your receiver's internet connection and press BLUE to refresh.",
    ),
    "cats_header": ("أقسام المتجر (8)", "Store Categories (8)"),
    "items_header": ("الحزم والإضافات", "Packages & Addons"),
    "active_badge": ("◀ نشط", "ACTIVE ▶"),
    "cats_badge": ("الأقسام", "Categories"),
    "items_badge": ("العناصر", "Items"),
    "zero_items": ("0 عنصر", "0 Items"),
    "page_badge": ("%d عنصر • صفحة %d / %d", "%d Items • Page %d / %d"),
    "ready_status": ("جاهز للاستعراض", "Ready to browse"),
    "empty_sec_status": ("لا توجد عناصر في هذا القسم", "No items in this section"),
    "empty_sec_desc": (
        "اختر قسماً آخر من القائمة اليمنى أو اضغط الزر الأزرق لتحديث البيانات.",
        "Select another category on the right or press BLUE to refresh the database.",
    ),
    "meta_cat_main": ("القسم: الرئيسية", "Category: Home"),
    "meta_type_default": ("النوع: متجر إضافات متكامل", "Type: All-in-One Addon Store"),
    "meta_src_default": ("المصدر: مستودع Online4Tech السحابي", "Source: Online4Tech Cloud Repo"),
    "meta_cat_fmt": ("القسم: %s", "Category: %s"),
    "meta_parent_fmt": ("القسم الرئيسي: %s", "Parent Category: %s"),
    "meta_type_fmt": ("النوع: %s", "Type: %s"),
    "meta_type_folder": ("النوع: مجلد أقسام فرعية", "Type: Sub-Categories Folder"),
    "meta_src_official": ("المصدر: Online4Tech Official", "Source: Online4Tech Official"),
    "meta_rem_yes": ("الإزالة التلقائية: مدعومة بالزر الأصفر", "Auto Uninstall: Supported (YELLOW)"),
    "meta_rem_no": ("الإزالة التلقائية: غير متوفرة", "Auto Uninstall: Not available"),
    "sub_folder_fmt": ("قسم فرعي  •  يحتوي على %d عنصر", "Sub-category  •  Contains %d items"),
    "sub_avail_fmt": ("قسم فرعي  •  %d عنصر متاح", "Sub-category  •  %d items available"),
    "folder_pill": ("مجلد ◀", "FOLDER"),
    "installed_pill": ("✓ مثبّت", "✓ INSTALLED"),
    "avail_pill": ("متاح", "AVAILABLE"),
    "status_installed": ("✓ مثبّتة على جهازك وجاهزة", "✓ Installed on your receiver"),
    "status_avail": ("متاحة للتثبيت المباشر", "Available for direct install"),
    "desc_intro": (
        "تنقّل بين الأقسام الثمانية على اليمين أو اضغط يسار للدخول إلى القائمة وتثبيت الإضافات.",
        "Browse the 8 main categories on the right or press LEFT to explore and install packages.",
    ),
    "desc_folder": (
        "اضغط زر موافق أو الزر الأخضر لفتح هذا القسم واستعراض جميع الإضافات بداخله.",
        "Press OK or the GREEN button to open this category and browse its packages.",
    ),
    "desc_pkg_with_ar": (
        "الوصف: %s\n\nاضغط زر موافق أو الزر الأخضر لبدء التحميل والتثبيت التلقائي على الجهاز.",
        "Description: %s\n\nPress OK or the GREEN button to download and install automatically.",
    ),
    "desc_pkg_default": (
        "حزمة جاهزة للتحميل والتثبيت المباشر من خوادم Online4Tech المتوافقة مع صورة جهازك.",
        "Ready for direct download and installation from Online4Tech servers for your image.",
    ),
    "cta_open_folder": ("فتح القسم الفرعي  •  OK", "Open Sub-Category  •  OK"),
    "cta_sub_folder": ("استعراض %d عنصر", "Browse %d items"),
    "cta_reinstall": ("إعادة التثبيت / التحديث  •  OK", "Reinstall / Update  •  OK"),
    "cta_install": ("تثبيت الآن  •  OK", "Install Now  •  OK"),
    "cta_sub_pkg": (
        "الأخضر: تثبيت  |  الأصفر: إزالة  |  MENU: الإعدادات",
        "GREEN: Install  |  YELLOW: Remove  |  MENU: Settings",
    ),
    "key_red": ("رجوع / إغلاق", "Back / Exit"),
    "key_green": ("تثبيت / فتح", "Install / Open"),
    "key_yellow": ("حذف / إزالة", "Uninstall"),
    "key_blue": ("تحديث المصدر", "Refresh Feed"),
    "key_menu": ("MENU • الإعدادات", "MENU • Settings"),
    "hint_cats": (
        "التركيز: الأقسام  |  يسار: العناصر  |  MENU: الخط واللغة",
        "Focus: Categories  |  LEFT: Items  |  MENU: Font & Language",
    ),
    "hint_items": (
        "التركيز: العناصر  |  OK: تثبيت  |  يمين: الأقسام  |  MENU: الإعدادات",
        "Focus: Items  |  OK: Install  |  RIGHT: Categories  |  MENU: Settings",
    ),
    "crumb_root": ("المتجر الرئيسي", "Main Store"),
    "crumb_short": ("المتجر", "Store"),
    "no_remove_msg": (
        "لا يوجد أمر إزالة تلقائية متاح لهذا العنصر.",
        "No automatic uninstall command is available for this item.",
    ),
}

_PIXMAP_CACHE = {}
_LOADED_FONT_MAP = {}


def load_prefs():
    prefs = dict(DEFAULT_PREFS)
    if os.path.isfile(PREFS_FILE):
        try:
            with io.open(PREFS_FILE, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    if data.get("lang") in ("ar", "en"):
                        prefs["lang"] = data["lang"]
                    if data.get("font_family") in ("Cairo", "Amiri", "System"):
                        prefs["font_family"] = data["font_family"]
                    if data.get("font_scale") in (-2, 0, 2, 4):
                        prefs["font_scale"] = int(data["font_scale"])
        except Exception:
            pass
    return prefs


def save_prefs(prefs):
    try:
        parent = os.path.dirname(PREFS_FILE)
        if not os.path.isdir(parent):
            os.makedirs(parent)
        with io.open(PREFS_FILE, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def tr(key, lang="ar"):
    pair = UI_STRINGS.get(key)
    if not pair:
        return key
    return pair[0] if lang == "ar" else pair[1]


def ensure_fonts_loaded():
    global _LOADED_FONT_MAP
    if _LOADED_FONT_MAP:
        return _LOADED_FONT_MAP

    mapping = {"System": "Regular"}
    font_specs = [
        ("Cairo", "O4TCairo", ["Cairo-Bold.ttf", "Cairo-Regular.ttf"]),
        ("Amiri", "O4TAmiri", ["Amiri-Bold.ttf", "Amiri-Regular.ttf"]),
    ]
    if os.path.isdir(FONTS_DIR):
        for fam, alias, files in font_specs:
            for fname in files:
                fpath = os.path.join(FONTS_DIR, fname)
                if os.path.isfile(fpath) and os.path.getsize(fpath) > 0:
                    try:
                        addFont(fpath, alias, 100, False)
                        mapping[fam] = alias
                        break
                    except Exception:
                        pass

    if "Cairo" not in mapping:
        mapping["Cairo"] = mapping.get("Amiri", "Regular")
    if "Amiri" not in mapping:
        mapping["Amiri"] = mapping.get("Cairo", "Regular")

    _LOADED_FONT_MAP = mapping
    return mapping


def resolve_font_name(family_key):
    fmap = ensure_fonts_loaded()
    return fmap.get(family_key, "Regular")


def _encode_png_rgba(w, h, rows):
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(tag, data):
        return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack("!IIBBBBB", w, h, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")


def _render_glass_button(filepath, w, h, radius, top_rgb, bot_rgb, border_rgb, fill_alpha=215):
    if os.path.isfile(filepath) and os.path.getsize(filepath) > 200:
        return
    try:
        parent = os.path.dirname(filepath)
        if not os.path.isdir(parent):
            os.makedirs(parent)

        b_px = bytes(bytearray((border_rgb[0], border_rgb[1], border_rgb[2], 245)))
        t_glare = bytes(bytearray((
            min(255, top_rgb[0] + 55),
            min(255, top_rgb[1] + 55),
            min(255, top_rgb[2] + 55),
            235,
        )))
        rows = []
        r = float(radius)

        for y in range(h):
            t = float(y) / max(1, h - 1)
            sheen = 28 if y < (h * 0.42) else 0
            cr = min(255, int(top_rgb[0] * (1.0 - t) + bot_rgb[0] * t) + sheen)
            cg = min(255, int(top_rgb[1] * (1.0 - t) + bot_rgb[1] * t) + sheen)
            cb = min(255, int(top_rgb[2] * (1.0 - t) + bot_rgb[2] * t) + sheen)
            f_px = bytes(bytearray((cr, cg, cb, fill_alpha)))

            if radius <= y < (h - radius):
                inner = t_glare if y == radius else f_px
                rows.append(b_px + (inner * (w - 2)) + b_px)
            else:
                cy = (r - 0.5) if y < radius else (h - r - 0.5)
                left_buf = bytearray()
                right_buf = bytearray()
                for x in range(radius):
                    cx = r - 0.5
                    dist = math.hypot(x - cx, y - cy)
                    if dist > r + 0.5:
                        left_buf.extend((0, 0, 0, 0))
                    elif dist > r - 1.3:
                        alpha = int(max(0, min(245, (r + 0.5 - dist) * 245)))
                        left_buf.extend((border_rgb[0], border_rgb[1], border_rgb[2], alpha))
                    else:
                        left_buf.extend(t_glare if y <= 2 else f_px)

                for x in range(w - radius, w):
                    cx = w - r - 0.5
                    dist = math.hypot(x - cx, y - cy)
                    if dist > r + 0.5:
                        right_buf.extend((0, 0, 0, 0))
                    elif dist > r - 1.3:
                        alpha = int(max(0, min(245, (r + 0.5 - dist) * 245)))
                        right_buf.extend((border_rgb[0], border_rgb[1], border_rgb[2], alpha))
                    else:
                        right_buf.extend(t_glare if y <= 2 else f_px)

                if y == 0 or y == h - 1:
                    mid_px = b_px
                elif y == 1 or y == 2:
                    mid_px = t_glare
                else:
                    mid_px = f_px
                rows.append(bytes(left_buf) + (mid_px * (w - 2 * radius)) + bytes(right_buf))

        with open(filepath, "wb") as f:
            f.write(_encode_png_rgba(w, h, rows))
    except Exception:
        pass


def ensure_glass_assets():
    _render_glass_button(
        os.path.join(ICONS_DIR, "btn_cta_gold.png"),
        574, 94, 16,
        top_rgb=(74, 60, 26),
        bot_rgb=(28, 24, 15),
        border_rgb=(243, 215, 120),
        fill_alpha=230,
    )
    _render_glass_button(
        os.path.join(ICONS_DIR, "btn_glass_menu.png"),
        235, 42, 11,
        top_rgb=(64, 52, 22),
        bot_rgb=(24, 20, 14),
        border_rgb=(212, 175, 55),
        fill_alpha=225,
    )
    buttons_spec = [
        ("btn_glass_red.png", (68, 24, 34), (26, 14, 22), (239, 68, 68)),
        ("btn_glass_green.png", (20, 64, 46), (13, 28, 24), (34, 197, 94)),
        ("btn_glass_yellow.png", (72, 56, 20), (28, 22, 13), (234, 179, 8)),
        ("btn_glass_blue.png", (22, 48, 82), (14, 22, 38), (56, 189, 248)),
    ]
    for fname, t_rgb, b_rgb, brd_rgb in buttons_spec:
        _render_glass_button(
            os.path.join(ICONS_DIR, fname),
            265, 42, 11,
            top_rgb=t_rgb,
            bot_rgb=b_rgb,
            border_rgb=brd_rgb,
            fill_alpha=225,
        )


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


def find_icon_path(icon_name, allow_brand=True):
    candidates = []
    if icon_name:
        candidates.append(os.path.join(ICONS_DIR, icon_name))
        candidates.append(os.path.join(PLUGIN_DIR, icon_name))
    if allow_brand:
        candidates.append(os.path.join(PLUGIN_DIR, "logo.png"))
        candidates.append(os.path.join(PLUGIN_DIR, "plugin.png"))
        candidates.append(os.path.join(PLUGIN_DIR, "icon.png"))
    for path in candidates:
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            return path
    return None


def get_cached_pixmap(icon_name):
    path = find_icon_path(icon_name, allow_brand=False)
    if not path:
        return None
    if path not in _PIXMAP_CACHE:
        try:
            _PIXMAP_CACHE[path] = LoadPixmap(path, cached=True)
        except Exception:
            _PIXMAP_CACHE[path] = None
    return _PIXMAP_CACHE[path]


class Online4TechMenuList(MenuList):
    def __init__(self, list_items, font_name="Regular", font_size=24, sub_size=19, item_height=66):
        MenuList.__init__(self, list_items, enableWrapAround=True, content=eListboxPythonMultiContent)
        self.l.setFont(0, gFont(font_name, font_size))
        self.l.setFont(1, gFont(font_name, sub_size))
        self.l.setItemHeight(item_height)

    def apply_font(self, font_name, font_size, sub_size, item_height=None):
        self.l.setFont(0, gFont(font_name, font_size))
        self.l.setFont(1, gFont(font_name, sub_size))
        if item_height:
            self.l.setItemHeight(item_height)


def build_category_entry(title, count_num, icon_name="", lang="ar"):
    display_title = truncate_text(title, 26)
    count_str = str(count_num) if count_num is not None else ""
    px = get_cached_pixmap(icon_name)
    align_flag = RT_HALIGN_RIGHT if lang == "ar" else RT_HALIGN_LEFT

    res = [(title, count_num, icon_name)]
    res.append(
        MultiContentEntryText(
            pos=(4, 5),
            size=(417, 76),
            font=0,
            flags=align_flag | RT_VALIGN_CENTER,
            text="",
            color=0xFFFFFF,
            color_sel=0xF3D778,
            backcolor=0x162238,
            backcolor_sel=0x332914,
        )
    )
    res.append(
        MultiContentEntryText(
            pos=(4, 5),
            size=(417, 2),
            font=0,
            flags=align_flag | RT_VALIGN_CENTER,
            text="",
            color=0xFFFFFF,
            color_sel=0xF3D778,
            backcolor=0x263552,
            backcolor_sel=0xD4AF37,
        )
    )
    res.append(
        MultiContentEntryText(
            pos=(362, 19),
            size=(48, 48),
            font=1,
            flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
            text="" if px else "◈",
            color=0xD4AF37,
            color_sel=0xF3D778,
            backcolor=0x0D1424,
            backcolor_sel=0x1F190C,
        )
    )
    if px:
        res.append(
            MultiContentEntryPixmapAlphaBlend(
                pos=(366, 23),
                size=(40, 40),
                png=px,
                flags=BT_SCALE,
            )
        )
    res.append(
        MultiContentEntryText(
            pos=(78, 16),
            size=(274, 54),
            font=0,
            flags=align_flag | RT_VALIGN_CENTER,
            text=display_title,
            color=0xE2E8F0,
            color_sel=0xF3D778,
        )
    )
    if count_str:
        res.append(
            MultiContentEntryText(
                pos=(12, 25),
                size=(58, 36),
                font=1,
                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                text=count_str,
                color=0x94A3B8,
                color_sel=0x0B0D14,
                backcolor=0x0D1424,
                backcolor_sel=0xF3D778,
            )
        )
    return res


def build_item_entry(title, subtitle, installed=False, icon_name="", is_folder=False, lang="ar"):
    display_title = truncate_text(title, 36)
    display_sub = truncate_text(subtitle, 44)
    px = get_cached_pixmap(icon_name)
    align_flag = RT_HALIGN_RIGHT if lang == "ar" else RT_HALIGN_LEFT

    if is_folder:
        status_txt = tr("folder_pill", lang)
        status_col = 0x38BDF8
        pill_bg = 0x0E2238
    elif installed:
        status_txt = tr("installed_pill", lang)
        status_col = 0x22C55E
        pill_bg = 0x0E2922
    else:
        status_txt = tr("avail_pill", lang)
        status_col = 0x94A3B8
        pill_bg = 0x0D1424

    res = [(title, subtitle, installed, icon_name)]
    res.append(
        MultiContentEntryText(
            pos=(4, 4),
            size=(692, 74),
            font=0,
            flags=align_flag | RT_VALIGN_CENTER,
            text="",
            color=0xFFFFFF,
            color_sel=0xF3D778,
            backcolor=0x162238,
            backcolor_sel=0x332914,
        )
    )
    res.append(
        MultiContentEntryText(
            pos=(4, 4),
            size=(692, 2),
            font=0,
            flags=align_flag | RT_VALIGN_CENTER,
            text="",
            color=0xFFFFFF,
            color_sel=0xF3D778,
            backcolor=0x263552,
            backcolor_sel=0xD4AF37,
        )
    )
    res.append(
        MultiContentEntryText(
            pos=(624, 12),
            size=(58, 58),
            font=0,
            flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
            text="" if px else "★",
            color=0xD4AF37,
            color_sel=0xF3D778,
            backcolor=0x0D1424,
            backcolor_sel=0x1F190C,
        )
    )
    if px:
        res.append(
            MultiContentEntryPixmapAlphaBlend(
                pos=(629, 17),
                size=(48, 48),
                png=px,
                flags=BT_SCALE,
            )
        )
    res.append(
        MultiContentEntryText(
            pos=(14, 21),
            size=(118, 40),
            font=1,
            flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
            text=status_txt,
            color=status_col,
            color_sel=0xF3D778 if not (installed or is_folder) else status_col,
            backcolor=pill_bg,
            backcolor_sel=0x1F190C,
        )
    )
    res.append(
        MultiContentEntryText(
            pos=(142, 8),
            size=(470, 36),
            font=0,
            flags=align_flag | RT_VALIGN_CENTER,
            text=display_title,
            color=0xF8FAFC,
            color_sel=0xF3D778,
        )
    )
    res.append(
        MultiContentEntryText(
            pos=(142, 42),
            size=(470, 30),
            font=1,
            flags=align_flag | RT_VALIGN_CENTER,
            text=display_sub,
            color=0x38BDF8,
            color_sel=0xE2E8F0,
        )
    )
    return res


def build_setting_entry(label_txt, value_txt, font_name="Regular", lang="ar"):
    res = [(label_txt, value_txt)]
    res.append(
        MultiContentEntryText(
            pos=(6, 6),
            size=(868, 76),
            font=0,
            flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
            text="",
            color=0xFFFFFF,
            color_sel=0xF3D778,
            backcolor=0x162238,
            backcolor_sel=0x332914,
        )
    )
    res.append(
        MultiContentEntryText(
            pos=(6, 6),
            size=(868, 2),
            font=0,
            flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
            text="",
            color=0xFFFFFF,
            color_sel=0xF3D778,
            backcolor=0x263552,
            backcolor_sel=0xF3D778,
        )
    )
    if lang == "ar":
        res.append(
            MultiContentEntryText(
                pos=(450, 14),
                size=(404, 60),
                font=0,
                flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER,
                text=label_txt,
                color=0xE2E8F0,
                color_sel=0xF3D778,
            )
        )
        res.append(
            MultiContentEntryText(
                pos=(24, 20),
                size=(410, 48),
                font=1,
                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                text="◀  %s  ▶" % value_txt,
                color=0x38BDF8,
                color_sel=0x080C14,
                backcolor=0x0D1424,
                backcolor_sel=0xF3D778,
            )
        )
    else:
        res.append(
            MultiContentEntryText(
                pos=(26, 14),
                size=(404, 60),
                font=0,
                flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                text=label_txt,
                color=0xE2E8F0,
                color_sel=0xF3D778,
            )
        )
        res.append(
            MultiContentEntryText(
                pos=(446, 20),
                size=(410, 48),
                font=1,
                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                text="◀  %s  ▶" % value_txt,
                color=0x38BDF8,
                color_sel=0x080C14,
                backcolor=0x0D1424,
                backcolor_sel=0xF3D778,
            )
        )
    return res


class Online4TechSettingsScreen(Screen):
    skin = """
    <screen name="Online4TechSettingsScreen" position="center,center" size="940,560" title="Online4Tech Settings" backgroundColor="#0c121e" flags="wfNoBorder">
        <!-- Outer Gold & Glass Border -->
        <eLabel position="0,0" size="940,560" backgroundColor="#d4af37" zPosition="-12" />
        <eLabel position="3,3" size="934,554" backgroundColor="#0c121e" zPosition="-11" />
        <eLabel position="18,18" size="904,96" backgroundColor="#141e33" zPosition="-9" />
        <eLabel position="18,18" size="904,2" backgroundColor="#f3d778" zPosition="-8" />

        <widget name="set_title" position="34,26" size="872,44" font="Regular;30" halign="center" foregroundColor="#f3d778" backgroundColor="#141e33" transparent="1" zPosition="5" />
        <widget name="set_subtitle" position="34,72" size="872,32" font="Regular;20" halign="center" foregroundColor="#94a3b8" backgroundColor="#141e33" transparent="1" zPosition="5" />

        <!-- Options List -->
        <widget name="settings_list" position="30,132" size="880,275" scrollbarMode="showNever" backgroundColor="#0c121e" backgroundColorSelected="#332914" foregroundColorSelected="#f3d778" transparent="1" zPosition="5" />

        <!-- Live Preview Box -->
        <eLabel position="30,418" size="880,54" backgroundColor="#141e33" zPosition="-8" />
        <widget name="hint_box" position="44,424" size="852,42" font="Regular;21" halign="center" valign="center" foregroundColor="#38bdf8" backgroundColor="#141e33" transparent="1" zPosition="5" />

        <!-- Bottom Glass Action Buttons -->
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/icons/btn_glass_green.png" position="560,492" size="265,42" alphatest="blend" zPosition="-6" />
        <eLabel text="●" position="785,494" size="30,38" font="Regular;22" halign="center" foregroundColor="#4ade80" backgroundColor="#10241d" transparent="1" zPosition="5" />
        <widget name="key_green" position="568,495" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#10241d" transparent="1" zPosition="5" />

        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/icons/btn_glass_red.png" position="115,492" size="265,42" alphatest="blend" zPosition="-6" />
        <eLabel text="●" position="340,494" size="30,38" font="Regular;22" halign="center" foregroundColor="#f87171" backgroundColor="#26121a" transparent="1" zPosition="5" />
        <widget name="key_red" position="123,495" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#26121a" transparent="1" zPosition="5" />
    </screen>
    """

    def __init__(self, session, prefs):
        Screen.__init__(self, session)
        self.session = session
        self.prefs = dict(prefs)

        self["set_title"] = Label("")
        self["set_subtitle"] = Label("")
        self["settings_list"] = Online4TechMenuList([], font_name="Regular", font_size=24, sub_size=21, item_height=88)
        self["hint_box"] = Label("")
        self["key_green"] = Label("")
        self["key_red"] = Label("")

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "ok": self.save_and_close,
                "green": self.save_and_close,
                "cancel": self.cancel_close,
                "red": self.cancel_close,
                "up": self.move_up,
                "down": self.move_down,
                "left": self.cycle_prev,
                "right": self.cycle_next,
            },
            -1,
        )

        self.onLayoutFinish.append(self.refresh_ui)

    def _get_family_idx(self):
        cur = self.prefs.get("font_family", "Cairo")
        for i, item in enumerate(FONT_FAMILIES):
            if item[0] == cur:
                return i
        return 0

    def _get_scale_idx(self):
        cur = self.prefs.get("font_scale", 0)
        for i, item in enumerate(FONT_SCALES):
            if item[0] == cur:
                return i
        return 1

    def refresh_ui(self):
        lang = self.prefs.get("lang", "ar")
        fam_idx = self._get_family_idx()
        sc_idx = self._get_scale_idx()
        font_name = resolve_font_name(FONT_FAMILIES[fam_idx][0])
        scale = FONT_SCALES[sc_idx][0]

        if lang == "ar":
            self["set_title"].setText("إعدادات المظهر واللغة  •  Online4Tech")
            self["set_subtitle"].setText("استخدم الأسهم يمين ويسار للتغيير، ثم اضغط موافق أو الأخضر للتطبيق")
            self["hint_box"].setText("معاينة مباشرة: خط %s  |  الحجم %s" % (FONT_FAMILIES[fam_idx][0], FONT_SCALES[sc_idx][1]))
            self["key_green"].setText("حفظ وتطبيق")
            self["key_red"].setText("إلغاء")

            rows = [
                build_setting_entry("لغة واجهة البانل", "العربية (Arabic)", font_name, "ar"),
                build_setting_entry("نوع الخط المستخدم", FONT_FAMILIES[fam_idx][1], font_name, "ar"),
                build_setting_entry("حجم الخط العام", FONT_SCALES[sc_idx][1], font_name, "ar"),
            ]
        else:
            self["set_title"].setText("Appearance & Language Settings")
            self["set_subtitle"].setText("Use LEFT / RIGHT arrows to adjust, then press OK or GREEN to apply")
            self["hint_box"].setText("Live Preview: %s Font  |  Size %s" % (FONT_FAMILIES[fam_idx][0], FONT_SCALES[sc_idx][2]))
            self["key_green"].setText("Save & Apply")
            self["key_red"].setText("Cancel")

            rows = [
                build_setting_entry("Interface Language", "English (الإنجليزية)", font_name, "en"),
                build_setting_entry("Font Family", FONT_FAMILIES[fam_idx][2], font_name, "en"),
                build_setting_entry("Global Font Size", FONT_SCALES[sc_idx][2], font_name, "en"),
            ]

        for wname, base_sz in [("set_title", 30), ("set_subtitle", 20), ("hint_box", 21), ("key_green", 21), ("key_red", 21)]:
            if self[wname].instance:
                try:
                    self[wname].instance.setFont(gFont(font_name, base_sz + scale))
                except Exception:
                    pass

        cur_sel = self["settings_list"].getSelectedIndex() or 0
        self["settings_list"].apply_font(font_name, 24 + scale, 21 + scale, item_height=88)
        self["settings_list"].setList(rows)
        self["settings_list"].moveToIndex(min(cur_sel, len(rows) - 1))

    def move_up(self):
        self["settings_list"].up()

    def move_down(self):
        self["settings_list"].down()

    def _step_option(self, delta):
        idx = self["settings_list"].getSelectedIndex() or 0
        if idx == 0:
            self.prefs["lang"] = "en" if self.prefs.get("lang", "ar") == "ar" else "ar"
        elif idx == 1:
            fi = (self._get_family_idx() + delta) % len(FONT_FAMILIES)
            self.prefs["font_family"] = FONT_FAMILIES[fi][0]
        elif idx == 2:
            si = (self._get_scale_idx() + delta) % len(FONT_SCALES)
            self.prefs["font_scale"] = FONT_SCALES[si][0]
        self.refresh_ui()

    def cycle_next(self):
        self._step_option(1)

    def cycle_prev(self):
        self._step_option(-1)

    def save_and_close(self):
        save_prefs(self.prefs)
        self.close(self.prefs)

    def cancel_close(self):
        self.close(None)


class Online4TechStoreScreen(Screen):
    skin = """
    <screen name="Online4TechStoreScreen" position="0,0" size="1920,1080" title="Online4Tech Store v7.5 Gold" backgroundColor="#080c14" flags="wfNoBorder">
        <!-- Top Glass Header Bar -->
        <eLabel position="28,18" size="1864,120" backgroundColor="#101726" zPosition="-10" />
        <eLabel position="28,18" size="1864,3" backgroundColor="#d4af37" zPosition="-5" />
        <eLabel position="28,136" size="1864,2" backgroundColor="#24324d" zPosition="-5" />

        <!-- Right Header: Brand & Glass Support Pill -->
        <widget name="brand_logo" position="1786,33" size="88,88" alphatest="blend" zPosition="5" />
        <eLabel text="ONLINE4TECH STORE" position="1385,28" size="385,42" font="Regular;31" halign="right" foregroundColor="#f3d778" backgroundColor="#101726" transparent="1" zPosition="5" />
        <eLabel text="VU+ • DREAMBOX • ENIGMA2 GOLD v7.5" position="1340,68" size="430,26" font="Regular;18" halign="right" foregroundColor="#38bdf8" backgroundColor="#101726" transparent="1" zPosition="5" />
        <eLabel position="1340,96" size="430,32" backgroundColor="#182236" zPosition="-6" />
        <eLabel position="1340,96" size="430,1" backgroundColor="#3b4d6e" zPosition="-5" />
        <widget name="brand_sub" position="1345,98" size="420,28" font="Regular;19" halign="center" noWrap="1" foregroundColor="#f3d778" backgroundColor="#182236" transparent="1" zPosition="5" />

        <!-- Center Header: Active Section Title & Breadcrumb -->
        <widget name="top_title" position="640,30" size="680,44" font="Regular;31" halign="center" foregroundColor="#f3d778" backgroundColor="#101726" transparent="1" zPosition="5" />
        <widget name="top_subtitle" position="640,82" size="680,36" font="Regular;20" halign="center" foregroundColor="#94a3b8" backgroundColor="#101726" transparent="1" zPosition="5" />

        <!-- Left Header Glass Card 1: Clock & Date -->
        <eLabel position="46,31" size="255,94" backgroundColor="#151f33" zPosition="-8" />
        <eLabel position="46,31" size="255,2" backgroundColor="#3b4d6e" zPosition="-5" />
        <widget name="clock_lbl" position="54,39" size="239,42" font="Regular;30" halign="center" foregroundColor="#ffffff" backgroundColor="#151f33" transparent="1" zPosition="5" />
        <widget name="date_lbl" position="54,84" size="239,30" font="Regular;19" halign="center" foregroundColor="#d4af37" backgroundColor="#151f33" transparent="1" zPosition="5" />

        <!-- Left Header Glass Card 2: Receiver & Python Info -->
        <eLabel position="315,31" size="305,94" backgroundColor="#151f33" zPosition="-8" />
        <eLabel position="315,31" size="305,2" backgroundColor="#3b4d6e" zPosition="-5" />
        <widget name="dev_info_top" position="325,41" size="285,36" font="Regular;23" halign="center" foregroundColor="#38bdf8" backgroundColor="#151f33" transparent="1" zPosition="5" />
        <widget name="dev_info_bot" position="325,82" size="285,32" font="Regular;19" halign="center" foregroundColor="#cbd5e1" backgroundColor="#151f33" transparent="1" zPosition="5" />

        <!-- Column 1 (Right): 8 Master Categories -->
        <eLabel position="1437,154" size="455,834" backgroundColor="#101726" zPosition="-10" />
        <widget name="cats_top_bar" position="1437,154" size="455,4" backgroundColor="#f3d778" zPosition="-5" />
        <widget name="cats_header" position="1560,168" size="313,44" font="Regular;28" halign="right" foregroundColor="#f3d778" backgroundColor="#101726" transparent="1" zPosition="5" />
        <widget name="cats_focus_pill" position="1455,172" size="100,34" font="Regular;18" halign="center" foregroundColor="#080c14" backgroundColor="#f3d778" zPosition="5" />
        <eLabel position="1455,220" size="418,2" backgroundColor="#24324d" zPosition="-5" />
        <widget name="cat_list" position="1452,238" size="425,710" scrollbarMode="showNever" backgroundColor="#101726" backgroundColorSelected="#332914" foregroundColorSelected="#f3d778" transparent="1" zPosition="5" />

        <!-- Column 2 (Center): Items & Sub-sections List -->
        <eLabel position="682,154" size="735,834" backgroundColor="#101726" zPosition="-10" />
        <widget name="items_top_bar" position="682,154" size="735,4" backgroundColor="#24324d" zPosition="-5" />
        <widget name="items_header" position="1035,168" size="360,44" font="Regular;27" halign="right" foregroundColor="#f8fafc" backgroundColor="#101726" transparent="1" zPosition="5" />
        <widget name="items_focus_pill" position="928,172" size="100,34" font="Regular;18" halign="center" foregroundColor="#94a3b8" backgroundColor="#162238" zPosition="5" />
        <widget name="page_info" position="702,172" size="218,36" font="Regular;20" halign="left" foregroundColor="#d4af37" backgroundColor="#101726" transparent="1" zPosition="5" />
        <eLabel position="702,220" size="695,2" backgroundColor="#24324d" zPosition="-5" />
        <widget name="item_list" position="698,232" size="700,738" scrollbarMode="showNever" backgroundColor="#101726" backgroundColorSelected="#332914" foregroundColorSelected="#f3d778" transparent="1" zPosition="5" />

        <!-- Column 3 (Left): Glass Preview & Details Card -->
        <eLabel position="28,154" size="634,834" backgroundColor="#101726" zPosition="-10" />
        <eLabel position="28,154" size="634,3" backgroundColor="#d4af37" zPosition="-5" />

        <!-- Top Status Dot Indicator -->
        <eLabel position="54,174" size="28,28" backgroundColor="#151f33" zPosition="-8" />
        <widget name="status_dot" position="54,172" size="28,30" font="Regular;22" halign="center" foregroundColor="#22c55e" backgroundColor="#151f33" transparent="1" zPosition="5" />

        <!-- Centered Glass Icon Frame -->
        <eLabel position="255,180" size="180,180" backgroundColor="#151f33" zPosition="-8" />
        <eLabel position="255,180" size="180,2" backgroundColor="#f3d778" zPosition="-5" />
        <eLabel position="255,358" size="180,2" backgroundColor="#2b3a59" zPosition="-5" />
        <widget name="preview_icon" position="275,200" size="140,140" alphatest="blend" zPosition="5" />

        <!-- Item Title & Install Status -->
        <widget name="detail_title" position="48,376" size="594,68" font="Regular;28" halign="center" foregroundColor="#ffffff" backgroundColor="#101726" transparent="1" zPosition="5" />
        <widget name="detail_status" position="48,448" size="594,36" font="Regular;22" halign="center" foregroundColor="#22c55e" backgroundColor="#101726" transparent="1" zPosition="5" />
        <eLabel position="58,494" size="574,2" backgroundColor="#24324d" zPosition="-5" />

        <!-- Structured Glass Details Box -->
        <eLabel position="52,508" size="586,155" backgroundColor="#151f33" zPosition="-8" />
        <eLabel position="52,508" size="586,2" backgroundColor="#2b3a59" zPosition="-5" />
        <widget name="meta_cat" position="68,518" size="554,36" font="Regular;22" halign="right" foregroundColor="#f3d778" backgroundColor="#151f33" transparent="1" zPosition="5" />
        <widget name="meta_type" position="68,564" size="554,36" font="Regular;22" halign="right" foregroundColor="#38bdf8" backgroundColor="#151f33" transparent="1" zPosition="5" />
        <widget name="meta_source" position="68,610" size="554,36" font="Regular;21" halign="right" foregroundColor="#cbd5e1" backgroundColor="#151f33" transparent="1" zPosition="5" />

        <!-- Item Description Area -->
        <widget name="detail_desc" position="58,680" size="574,160" font="Regular;23" halign="right" foregroundColor="#e2e8f0" backgroundColor="#101726" transparent="1" zPosition="5" />

        <!-- Glassy Gold CTA Button inside Preview Column -->
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/icons/btn_cta_gold.png" position="58,860" size="574,94" alphatest="blend" zPosition="-7" />
        <widget name="action_cta" position="72,872" size="546,40" font="Regular;27" halign="center" foregroundColor="#f3d778" backgroundColor="#2b2312" transparent="1" zPosition="5" />
        <widget name="action_sub" position="72,914" size="546,30" font="Regular;20" halign="center" foregroundColor="#e2e8f0" backgroundColor="#2b2312" transparent="1" zPosition="5" />

        <!-- Bottom Glass Color Buttons Bar -->
        <eLabel position="28,1004" size="1864,58" backgroundColor="#101726" zPosition="-10" />
        <eLabel position="28,1004" size="1864,2" backgroundColor="#24324d" zPosition="-5" />

        <!-- Red Glass Button -->
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/icons/btn_glass_red.png" position="1610,1012" size="265,42" alphatest="blend" zPosition="-6" />
        <eLabel text="●" position="1835,1014" size="30,38" font="Regular;22" halign="center" foregroundColor="#f87171" backgroundColor="#26121a" transparent="1" zPosition="5" />
        <widget name="key_red" position="1618,1015" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#26121a" transparent="1" zPosition="5" />

        <!-- Green Glass Button -->
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/icons/btn_glass_green.png" position="1325,1012" size="265,42" alphatest="blend" zPosition="-6" />
        <eLabel text="●" position="1550,1014" size="30,38" font="Regular;22" halign="center" foregroundColor="#4ade80" backgroundColor="#10241d" transparent="1" zPosition="5" />
        <widget name="key_green" position="1333,1015" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#10241d" transparent="1" zPosition="5" />

        <!-- Yellow Glass Button -->
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/icons/btn_glass_yellow.png" position="1040,1012" size="265,42" alphatest="blend" zPosition="-6" />
        <eLabel text="●" position="1265,1014" size="30,38" font="Regular;22" halign="center" foregroundColor="#facc15" backgroundColor="#261f10" transparent="1" zPosition="5" />
        <widget name="key_yellow" position="1048,1015" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#261f10" transparent="1" zPosition="5" />

        <!-- Blue Glass Button -->
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/icons/btn_glass_blue.png" position="755,1012" size="265,42" alphatest="blend" zPosition="-6" />
        <eLabel text="●" position="980,1014" size="30,38" font="Regular;22" halign="center" foregroundColor="#38bdf8" backgroundColor="#101f33" transparent="1" zPosition="5" />
        <widget name="key_blue" position="763,1015" size="215,36" font="Regular;21" halign="right" valign="center" foregroundColor="#f8fafc" backgroundColor="#101f33" transparent="1" zPosition="5" />

        <!-- Glass Menu Button Pill -->
        <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/icons/btn_glass_menu.png" position="48,1012" size="235,42" alphatest="blend" zPosition="-6" />
        <widget name="key_menu" position="56,1014" size="219,38" font="Regular;20" halign="center" valign="center" foregroundColor="#f3d778" backgroundColor="#241e12" transparent="1" zPosition="5" />

        <!-- Navigation Hint -->
        <widget name="footer_hint" position="295,1014" size="445,38" font="Regular;19" halign="left" valign="center" foregroundColor="#94a3b8" backgroundColor="#101726" transparent="1" zPosition="5" />
    </screen>
    """

    def __init__(self, session):
        ensure_glass_assets()
        Screen.__init__(self, session)
        self.session = session
        self.prefs = load_prefs()
        self.lang = self.prefs.get("lang", "ar")
        self.font_scale = self.prefs.get("font_scale", 0)
        self.ui_font = resolve_font_name(self.prefs.get("font_family", "Cairo"))

        self.db_data = {}
        self.master_groups = []
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
        self["top_title"] = Label(tr("store_title", self.lang))
        self["top_subtitle"] = Label(tr("loading_db", self.lang))

        self["clock_lbl"] = Label(clock_str)
        self["date_lbl"] = Label(date_str)
        self["dev_info_top"] = Label(img_name)
        self["dev_info_bot"] = Label("Py %s  •  IP: %s" % (py_ver, ip))

        self["cats_top_bar"] = Label("")
        self["cats_header"] = Label(tr("cats_header", self.lang))
        self["cats_focus_pill"] = Label(tr("active_badge", self.lang))
        self["cat_list"] = Online4TechMenuList(
            [],
            font_name=self.ui_font,
            font_size=23 + self.font_scale,
            sub_size=18 + self.font_scale,
            item_height=86,
        )

        self["items_top_bar"] = Label("")
        self["items_header"] = Label(tr("items_header", self.lang))
        self["items_focus_pill"] = Label(tr("items_badge", self.lang))
        self["page_info"] = Label(tr("zero_items", self.lang))
        self["item_list"] = Online4TechMenuList(
            [],
            font_name=self.ui_font,
            font_size=24 + self.font_scale,
            sub_size=19 + self.font_scale,
            item_height=82,
        )

        self["status_dot"] = Label("●")
        self["preview_icon"] = Pixmap()
        self["detail_title"] = Label("Online4Tech v7.5 Gold")
        self["detail_status"] = Label(tr("ready_status", self.lang))
        self["meta_cat"] = Label(tr("meta_cat_main", self.lang))
        self["meta_type"] = Label(tr("meta_type_default", self.lang))
        self["meta_source"] = Label(tr("meta_src_default", self.lang))
        self["detail_desc"] = Label(tr("desc_intro", self.lang))
        self["action_cta"] = Label(tr("cta_install", self.lang))
        self["action_sub"] = Label(tr("cta_sub_pkg", self.lang))

        self["key_red"] = Label(tr("key_red", self.lang))
        self["key_green"] = Label(tr("key_green", self.lang))
        self["key_yellow"] = Label(tr("key_yellow", self.lang))
        self["key_blue"] = Label(tr("key_blue", self.lang))
        self["key_menu"] = Label(tr("key_menu", self.lang))
        self["footer_hint"] = Label(tr("hint_cats", self.lang))

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions", "ChannelSelectBaseActions", "MenuActions"],
            {
                "ok": self.ok_pressed,
                "cancel": self.back_pressed,
                "red": self.back_pressed,
                "green": self.ok_pressed,
                "yellow": self.remove_pressed,
                "blue": self.refresh_db,
                "menu": self.open_settings,
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
        brand_img = find_icon_path("logo.png", allow_brand=True)
        if brand_img and self["brand_logo"].instance:
            try:
                self["brand_logo"].instance.setScale(1)
            except Exception:
                pass
            self["brand_logo"].instance.setPixmapFromFile(brand_img)
        self.apply_visual_theme()
        self.load_database(force=False)

    def open_settings(self):
        self.session.openWithCallback(self.on_settings_closed, Online4TechSettingsScreen, self.prefs)

    def on_settings_closed(self, new_prefs):
        if not new_prefs:
            return
        self.prefs = new_prefs
        self.lang = self.prefs.get("lang", "ar")
        self.font_scale = self.prefs.get("font_scale", 0)
        self.ui_font = resolve_font_name(self.prefs.get("font_family", "Cairo"))

        self.apply_visual_theme()
        self.build_master_groups()
        self.populate_categories(keep_idx=self.current_cat_idx)
        if self.master_groups and 0 <= self.current_cat_idx < len(self.master_groups):
            self.open_master_group(self.master_groups[self.current_cat_idx], push_history=False)

    def apply_visual_theme(self):
        sc = self.font_scale
        fn = self.ui_font
        lg = self.lang

        font_widgets = [
            ("brand_sub", 19),
            ("top_title", 31),
            ("top_subtitle", 20),
            ("cats_header", 28),
            ("cats_focus_pill", 18),
            ("items_header", 27),
            ("items_focus_pill", 18),
            ("page_info", 20),
            ("detail_title", 28),
            ("detail_status", 22),
            ("meta_cat", 22),
            ("meta_type", 22),
            ("meta_source", 21),
            ("detail_desc", 23),
            ("action_cta", 27),
            ("action_sub", 20),
            ("key_red", 21),
            ("key_green", 21),
            ("key_yellow", 21),
            ("key_blue", 21),
            ("key_menu", 20),
            ("footer_hint", 19),
        ]
        for wname, base_sz in font_widgets:
            if self[wname].instance:
                try:
                    self[wname].instance.setFont(gFont(fn, max(15, base_sz + sc)))
                except Exception:
                    pass

        self["cat_list"].apply_font(fn, max(17, 23 + sc), max(15, 18 + sc), item_height=86)
        self["item_list"].apply_font(fn, max(18, 24 + sc), max(15, 19 + sc), item_height=82)

        self["cats_header"].setText(tr("cats_header", lg))
        self["key_red"].setText(tr("key_red", lg))
        self["key_green"].setText(tr("key_green", lg))
        self["key_yellow"].setText(tr("key_yellow", lg))
        self["key_blue"].setText(tr("key_blue", lg))
        self["key_menu"].setText(tr("key_menu", lg))
        self["footer_hint"].setText(tr("hint_cats" if self.focus_pane == "cats" else "hint_items", lg))
        self.update_focus_visuals()

    def update_focus_visuals(self):
        try:
            gold = gRGB(0xF3D778)
            dim = gRGB(0x24324D)
            dark_txt = gRGB(0x080C14)
            muted_txt = gRGB(0x94A3B8)
            pill_inactive = gRGB(0x162238)

            if self.focus_pane == "cats":
                if self["cats_top_bar"].instance:
                    self["cats_top_bar"].instance.setBackgroundColor(gold)
                if self["items_top_bar"].instance:
                    self["items_top_bar"].instance.setBackgroundColor(dim)
                self["cats_focus_pill"].setText(tr("active_badge", self.lang))
                self["items_focus_pill"].setText(tr("items_badge", self.lang))
                if self["cats_focus_pill"].instance:
                    self["cats_focus_pill"].instance.setBackgroundColor(gold)
                    self["cats_focus_pill"].instance.setForegroundColor(dark_txt)
                if self["items_focus_pill"].instance:
                    self["items_focus_pill"].instance.setBackgroundColor(pill_inactive)
                    self["items_focus_pill"].instance.setForegroundColor(muted_txt)
            else:
                if self["cats_top_bar"].instance:
                    self["cats_top_bar"].instance.setBackgroundColor(dim)
                if self["items_top_bar"].instance:
                    self["items_top_bar"].instance.setBackgroundColor(gold)
                self["cats_focus_pill"].setText(tr("cats_badge", self.lang))
                self["items_focus_pill"].setText(tr("active_badge", self.lang))
                if self["items_focus_pill"].instance:
                    self["items_focus_pill"].instance.setBackgroundColor(gold)
                    self["items_focus_pill"].instance.setForegroundColor(dark_txt)
                if self["cats_focus_pill"].instance:
                    self["cats_focus_pill"].instance.setBackgroundColor(pill_inactive)
                    self["cats_focus_pill"].instance.setForegroundColor(muted_txt)
        except Exception:
            pass

    def get_section_title(self, sec_key, fallback=""):
        pair = SECTION_LABELS.get(sec_key)
        if pair:
            return pair[0] if self.lang == "ar" else pair[1]
        raw_t = clean_text(fallback or sec_key)
        title_clean, ar_sub = parse_item_name(raw_t)
        if self.lang == "ar" and ar_sub:
            return ar_sub
        return title_clean

    def build_master_groups(self):
        known_sections = set()
        groups = []
        for g in MASTER_CATEGORIES:
            secs = list(g["sections"])
            for s in secs:
                known_sections.add(s)
            groups.append({
                "id": g["id"],
                "title": g["title_ar"] if self.lang == "ar" else g["title_en"],
                "icon": g["icon"],
                "sections": secs,
            })

        for sec_obj in self.db_data.get("main", []):
            sk = sec_obj.get("section", "")
            if sk and sk not in known_sections:
                groups[-1]["sections"].append(sk)
                known_sections.add(sk)

        self.master_groups = groups[:8]

    def load_database(self, force=False):
        try:
            if force or not os.path.exists(CACHE_DB) or os.path.getsize(CACHE_DB) == 0:
                self["top_subtitle"].setText(tr("connecting_db", self.lang))
                req = Request(DB_URL, headers={"User-Agent": "Online4Tech-Enigma2-v7.5"})
                ctx = ssl._create_unverified_context() if hasattr(ssl, "_create_unverified_context") else None
                resp = urlopen(req, timeout=20, context=ctx) if ctx else urlopen(req, timeout=20)
                raw = resp.read().decode("utf-8", errors="ignore")
                with io.open(CACHE_DB, "w", encoding="utf-8") as f:
                    f.write(raw)

            with io.open(CACHE_DB, "r", encoding="utf-8", errors="ignore") as f:
                self.db_data = json.load(f)

            self.build_master_groups()
            self.nav_stack = []
            self.current_cat_idx = 0
            self.populate_categories(keep_idx=0)

            total_pkgs = sum(len(v) for k, v in self.db_data.items() if k != "main" and isinstance(v, list))
            if self.master_groups:
                self.open_master_group(self.master_groups[0], push_history=False)
            self["top_subtitle"].setText(tr("connected_summary", self.lang) % (len(self.master_groups), total_pkgs))
        except Exception as e:
            self["top_subtitle"].setText(tr("conn_error", self.lang))
            self["detail_desc"].setText("%s\n%s" % (tr("conn_error_desc", self.lang), clean_text(str(e))))

    def refresh_db(self):
        self.load_database(force=True)

    def populate_categories(self, keep_idx=0):
        entries = []
        for grp in self.master_groups:
            total_cnt = 0
            for sk in grp["sections"]:
                items = self.db_data.get(sk, [])
                if isinstance(items, list):
                    total_cnt += len(items)
            entries.append(build_category_entry(grp["title"], total_cnt, grp["icon"], lang=self.lang))
        self["cat_list"].setList(entries)
        if entries:
            self["cat_list"].moveToIndex(min(keep_idx, len(entries) - 1))

    def _format_crumb(self, parts):
        sep = "  ◀  " if self.lang == "ar" else "  ▶  "
        return sep.join(parts)

    def open_master_group(self, grp, push_history=False):
        secs = grp["sections"]
        if len(secs) == 1:
            sk = secs[0]
            self.open_section(sk, grp["title"], icon_name=grp["icon"], push_history=push_history)
            self["top_subtitle"].setText(self._format_crumb([tr("crumb_root", self.lang), grp["title"]]))
            return

        if push_history and self.current_section_key:
            self.nav_stack.append((
                self.current_section_key,
                self.current_section_title,
                self.current_section_icon,
                list(self.current_items),
                self["item_list"].getSelectedIndex() or 0,
            ))

        self.current_section_key = grp["id"]
        self.current_section_title = grp["title"]
        self.current_section_icon = grp["icon"]

        virtual_items = []
        for sk in secs:
            sub_list = self.db_data.get(sk, [])
            if isinstance(sub_list, list):
                virtual_items.append({
                    "section": sk,
                    "title": self.get_section_title(sk),
                    "icon": sk + ".png",
                })

        self.current_items = virtual_items
        self["top_title"].setText(grp["title"])
        self["top_subtitle"].setText(self._format_crumb([tr("crumb_root", self.lang), grp["title"]]))
        self["items_header"].setText(grp["title"])

        list_entries = []
        for it in virtual_items:
            sub_key = it["section"]
            sub_count = len(self.db_data.get(sub_key, []))
            list_entries.append(
                build_item_entry(
                    it["title"],
                    tr("sub_folder_fmt", self.lang) % sub_count,
                    False,
                    it["icon"],
                    is_folder=True,
                    lang=self.lang,
                )
            )

        self["item_list"].setList(list_entries)
        if list_entries:
            self["item_list"].moveToIndex(0)
        self.update_page_badge()
        self.update_preview(icon_override=grp["icon"])

    def update_page_badge(self):
        total = len(self.current_items)
        if total == 0:
            self["page_info"].setText(tr("zero_items", self.lang))
            return
        idx = self["item_list"].getSelectedIndex() or 0
        total_pages = max(1, int(math.ceil(float(total) / ITEMS_PER_PAGE)))
        cur_page = min(total_pages, (idx // ITEMS_PER_PAGE) + 1)
        self["page_info"].setText(tr("page_badge", self.lang) % (total, cur_page, total_pages))

    def open_section(self, section_key, title, icon_name="", push_history=True):
        if push_history and self.current_section_key:
            self.nav_stack.append((
                self.current_section_key,
                self.current_section_title,
                self.current_section_icon,
                list(self.current_items),
                self["item_list"].getSelectedIndex() or 0,
            ))

        sec_icon = icon_name or (section_key + ".png")
        parent_title = self.current_section_title if push_history else ""
        self.current_section_key = section_key
        self.current_section_title = title
        self.current_section_icon = sec_icon
        raw_items = self.db_data.get(section_key, [])
        self.current_items = raw_items if isinstance(raw_items, list) else []

        self["top_title"].setText(title or "Online4Tech Store")
        if parent_title and parent_title != title:
            self["top_subtitle"].setText(self._format_crumb([tr("crumb_short", self.lang), parent_title, title]))
        else:
            self["top_subtitle"].setText(self._format_crumb([tr("crumb_root", self.lang), title]))
        self["items_header"].setText(title or tr("items_header", self.lang))

        list_entries = []
        for it in self.current_items:
            if "section" in it:
                sub_key = it.get("section", "")
                sub_title = self.get_section_title(sub_key, it.get("title", ""))
                sub_count = len(self.db_data.get(sub_key, []))
                sub_icon = it.get("icon") or (sub_key + ".png") or sec_icon
                list_entries.append(
                    build_item_entry(
                        sub_title,
                        tr("sub_folder_fmt", self.lang) % sub_count,
                        False,
                        sub_icon,
                        is_folder=True,
                        lang=self.lang,
                    )
                )
            else:
                clean_title, ar_desc = parse_item_name(it.get("name", "Package"))
                path = it.get("path", "")
                installed = bool(path and os.path.exists(path))
                if self.lang == "ar" and ar_desc:
                    sub_txt = ar_desc
                else:
                    sub_txt = tr("meta_cat_fmt", self.lang) % title
                item_icon = it.get("icon") or sec_icon
                list_entries.append(
                    build_item_entry(clean_title, sub_txt, installed, item_icon, is_folder=False, lang=self.lang)
                )

        self["item_list"].setList(list_entries)
        if list_entries:
            self["item_list"].moveToIndex(0)
        self.update_page_badge()
        self.update_preview(icon_override=sec_icon)

    def update_preview(self, icon_override=""):
        self.update_page_badge()
        lg = self.lang
        idx = self["item_list"].getSelectedIndex()
        if idx is None or idx < 0 or idx >= len(self.current_items):
            self["detail_title"].setText(self.current_section_title or "Online4Tech")
            self["detail_status"].setText(tr("empty_sec_status", lg))
            self["meta_cat"].setText(tr("meta_cat_fmt", lg) % (self.current_section_title or "-"))
            self["meta_type"].setText(tr("meta_type_default", lg))
            self["meta_source"].setText(tr("meta_src_default", lg))
            self["detail_desc"].setText(tr("empty_sec_desc", lg))
            return

        item = self.current_items[idx]
        type_pair = PACKAGE_TYPE_LABELS.get(self.current_section_key)
        pkg_type = (type_pair[0] if lg == "ar" else type_pair[1]) if type_pair else (
            "حزمة إضافية • Enigma2" if lg == "ar" else "Extension Package • Enigma2"
        )

        if "section" in item:
            sub_key = item.get("section", "")
            title = self.get_section_title(sub_key, item.get("title", ""))
            cnt = len(self.db_data.get(sub_key, []))
            self["detail_title"].setText(truncate_text(title, 34))
            self["detail_status"].setText(tr("sub_avail_fmt", lg) % cnt)
            self["meta_cat"].setText(tr("meta_parent_fmt", lg) % self.current_section_title)
            self["meta_type"].setText(tr("meta_type_folder", lg))
            self["meta_source"].setText(tr("meta_src_official", lg))
            self["detail_desc"].setText(tr("desc_folder", lg))
            self["action_cta"].setText(tr("cta_open_folder", lg))
            self["action_sub"].setText(tr("cta_sub_folder", lg) % cnt)
            cand_icon = item.get("icon") or (sub_key + ".png") or icon_override or self.current_section_icon
            icon_file = find_icon_path(cand_icon, allow_brand=True)
        else:
            clean_title, ar_desc = parse_item_name(item.get("name", "Package"))
            path = item.get("path", "")
            installed = bool(path and os.path.exists(path))
            has_remove = bool(item.get("remove_cmd"))

            self["detail_title"].setText(truncate_text(clean_title, 34))
            self["detail_status"].setText(tr("status_installed" if installed else "status_avail", lg))
            self["meta_cat"].setText(tr("meta_cat_fmt", lg) % self.current_section_title)
            self["meta_type"].setText(tr("meta_type_fmt", lg) % pkg_type)
            self["meta_source"].setText(tr("meta_rem_yes" if has_remove else "meta_rem_no", lg))

            if lg == "ar" and ar_desc:
                desc_body = tr("desc_pkg_with_ar", lg) % ar_desc
            else:
                desc_body = tr("desc_pkg_default", lg)
            self["detail_desc"].setText(desc_body)
            self["action_cta"].setText(tr("cta_reinstall" if installed else "cta_install", lg))
            self["action_sub"].setText(tr("cta_sub_pkg", lg))
            cand_icon = item.get("icon") or icon_override or self.current_section_icon
            icon_file = find_icon_path(cand_icon, allow_brand=True)

        if icon_file and self["preview_icon"].instance:
            try:
                self["preview_icon"].instance.setScale(1)
            except Exception:
                pass
            self["preview_icon"].instance.setPixmapFromFile(icon_file)

    def move_up(self):
        if self.focus_pane == "cats":
            self["cat_list"].up()
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.master_groups):
                self.current_cat_idx = idx
                self.open_master_group(self.master_groups[idx], push_history=False)
        else:
            self["item_list"].up()
            self.update_preview()

    def move_down(self):
        if self.focus_pane == "cats":
            self["cat_list"].down()
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.master_groups):
                self.current_cat_idx = idx
                self.open_master_group(self.master_groups[idx], push_history=False)
        else:
            self["item_list"].down()
            self.update_preview()

    def page_up(self):
        if self.focus_pane == "cats":
            self["cat_list"].pageUp()
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.master_groups):
                self.current_cat_idx = idx
                self.open_master_group(self.master_groups[idx], push_history=False)
        else:
            self["item_list"].pageUp()
            self.update_preview()

    def page_down(self):
        if self.focus_pane == "cats":
            self["cat_list"].pageDown()
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.master_groups):
                self.current_cat_idx = idx
                self.open_master_group(self.master_groups[idx], push_history=False)
        else:
            self["item_list"].pageDown()
            self.update_preview()

    def focus_cats_pane(self):
        self.focus_pane = "cats"
        self.update_focus_visuals()
        self["footer_hint"].setText(tr("hint_cats", self.lang))

    def focus_items_pane(self):
        self.focus_pane = "items"
        self.update_focus_visuals()
        self["footer_hint"].setText(tr("hint_items", self.lang))

    def ok_pressed(self):
        if self.focus_pane == "cats":
            idx = self["cat_list"].getSelectedIndex()
            if idx is not None and 0 <= idx < len(self.master_groups):
                self.current_cat_idx = idx
                self.open_master_group(self.master_groups[idx], push_history=False)
                self.focus_items_pane()
            return

        idx = self["item_list"].getSelectedIndex()
        if idx is None or idx < 0 or idx >= len(self.current_items):
            return
        item = self.current_items[idx]
        if "section" in item:
            sub_key = item.get("section", "")
            sub_title = self.get_section_title(sub_key, item.get("title", ""))
            sub_icon = item.get("icon") or (sub_key + ".png")
            self.open_section(sub_key, sub_title, icon_name=sub_icon, push_history=True)
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
            self.session.open(MessageBox, tr("no_remove_msg", self.lang), MessageBox.TYPE_INFO, timeout=3)

    def back_pressed(self):
        if self.nav_stack:
            prev_key, prev_title, prev_icon, prev_items, prev_idx = self.nav_stack.pop()
            self.current_section_key = prev_key
            self.current_section_title = prev_title
            self.current_section_icon = prev_icon
            self.current_items = prev_items
            self["top_title"].setText(prev_title or "Online4Tech Store")
            self["top_subtitle"].setText(self._format_crumb([tr("crumb_root", self.lang), prev_title]))
            self["items_header"].setText(prev_title or tr("items_header", self.lang))

            entries = []
            for it in prev_items:
                if "section" in it:
                    sk = it.get("section", "")
                    sub_t = self.get_section_title(sk, it.get("title", ""))
                    cnt = len(self.db_data.get(sk, []))
                    sub_ic = it.get("icon") or (sk + ".png") or prev_icon
                    entries.append(
                        build_item_entry(
                            sub_t,
                            tr("sub_folder_fmt", self.lang) % cnt,
                            False,
                            sub_ic,
                            is_folder=True,
                            lang=self.lang,
                        )
                    )
                else:
                    nm, ar_d = parse_item_name(it.get("name", "Package"))
                    pth = it.get("path", "")
                    inst = bool(pth and os.path.exists(pth))
                    sub_txt = ar_d if (self.lang == "ar" and ar_d) else (tr("meta_cat_fmt", self.lang) % prev_title)
                    entries.append(
                        build_item_entry(nm, sub_txt, inst, it.get("icon") or prev_icon, is_folder=False, lang=self.lang)
                    )

            self["item_list"].setList(entries)
            if entries:
                self["item_list"].moveToIndex(min(prev_idx, len(entries) - 1))
            self.update_preview(icon_override=prev_icon)
        else:
            self.close()