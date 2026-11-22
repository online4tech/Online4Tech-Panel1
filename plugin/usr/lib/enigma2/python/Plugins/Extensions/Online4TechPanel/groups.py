# -*- coding: utf-8 -*-
"""Sidebar grouping for the store: every catalog item lands in exactly one group.

Plugins are sorted by what they do (rule based, first match wins) so no list gets huge.
Anything that matches no rule falls back to its catalog category, and finally to "other",
so nothing is ever hidden.
"""
from __future__ import absolute_import

# ordered by importance (this is the order in the sidebar)
PLUGIN_ORDER = ["panels", "iptv", "media", "cams", "epg", "ciefp", "islamic", "info",
                "translation", "look", "tools", "network", "system", "community"]

SKIN_GROUPS = [
    ("skins", ["OpenATV", "OpenBH", "Egami", "OpenSPA", "OpenVIX", "PurE2", "TeamNitro"]),
    ("pli", ["OpenPLi Py3", "OpenPLi Py2"]),
    ("lcd", ["Display (LCD)"]),
    ("graphics", ["Bootlogos", "Spinners", "Picons"]),
    ("community", ["Community Skins", "XStreamity"]),
]
SKIN_ORDER = [g for g, _c in SKIN_GROUPS]

CAT_FIXED = {          # whole categories that always map to one group
    "Panels": "panels", "Community": "community", "Translation": "translation",
    "System": "system", "Multiboot": "system", "Dependencies": "system", "Ciefp": "ciefp",
}
CAT_DEFAULT = {        # used when no keyword rule matched
    "Media": "media", "Audio": "media", "IPTV": "iptv", "Novaler": "iptv",
    "EPG": "epg", "Settings": "epg", "Tools": "tools", "Plugins": "tools",
}

RULES = [
    ("network", ["dns ", "wifi", "الواي فاي", "ntp", "wireguard", "transmission", "ip_checker",
                 "net usage", "internet-speedtest", "speedtest"]),
    ("system", ["arabic-language", "opkg", "wget", "curl", "فهارس", "ترقية", "update enigma2",
                "format_hdd", "repair-inodes", "password", "fix-", "filecommander", "openwebif",
                "chromium", "hardwareinfo", "temperature", "حرارة", "bitrate",
                "معدل البث", "backupflash", "script package", "super script"]),
    ("islamic", ["مواقيت", "قرآن", "قرأن", "اذكار", "أذكار", "المؤذن", "الأجر", "أنصت", "حصن", "ادعية",
                 "athan", "azkar", "quran", "prayer", "hisn", "mawaqit", "muaddhin", "moaddin",
                 "shiavoice", "kareem", "karem", "ansite", "alajre"]),
    ("translation", ["ترجمة", "مترجم", "subs", "subtitle", "translator", "tmdb", "tmbd",
                     "معلومات الفيلم", "youre"]),
    ("info", ["weather", "الطقس", "webcam", "worldcam", "كاميرات", "foreca"]),
    ("media", ["filmon"]),
    ("media", ["audio", "radio", "صوتيات", "راديو", "اغاني", "youtube", "e2-tube", "اليوتيوب",
               "timeshift", "تايم شفت", "movie", "افلام", "الافلام", "ipaudio"]),
    ("cams", ["cccam", "ciplus", "keyadder", "mycam", "multicam", "satcam", "camm", "كام", "ايميو",
              "شفرات", "zoom", "سيرفرات", "abertis", "ابيرنس", "novacam", "ultracam",
              "cam-"]),
    ("iptv", ["iptv", "stalker", "portal", "بورتل", "xtream", "xstream", "m3u", "xklass", "xport",
              "tivimate", "ipsat", "iptosat", "ip2sat", "bouquetmaker", "jedi", "playlists",
              "beengo", "airnet", "total90", "novaler"]),
    ("epg", ["epg", "دليل", "channel", "القنوات", "قنوات", "bouquet", "signal", "إشارة", "اشارة",
             "zap", "servicescan", "xmlupdate", "ترددات", "فيد", "feed", "satellites", "quadpip",
             "tvmanager"]),
    ("tools", ["mover", "backup", "uninstall", "remove", "crash", "cache", "كاش", "crond", "flash",
               "zip2", "script", "سكريبت", "حذف", "نسخ", "نقل", "كراش", "imagesdownloader",
               "تحميل الصور", "تحميل الإضافات", "عمل باكاج", "downloader", "updater", "screen-shot",
               "screen-recorder", "لقطة", "تسجيل الشاشة", "explorer", "تصفح الملفات"]),
    ("look", ["picon", "بيكون", "logo", "لوجو", "الشعار", "bootlogo", "spinner", "الدوار", "theme",
              "ثيم", "skin", "screennames", "اسم الشاشة", "keyboard", "كيبورد", "pluginbrowser",
              "menusort", "ترتيب القائمة", "infobar", "انفوبار", "xtraevent", "atilehd"]),
    ("info", ["calendar", "التقويم", "calculator", "الحاسبة", "clock", "ساعة", "horoscope",
              "الأبراج", "الأعياد", "holiday", "apod", "astronomy", "كوكب", "الكواكب", "sport",
              "رياضة", "مباريات", "livematch", "footonsat", "speedtest", "الإنترنت", "ip_checker"]),
]


def _text(item):
    return ("%s %s" % (item.get("name", ""), item.get("desc", ""))).lower()


def plugin_group(item):
    cat = item.get("category", "")
    if cat in CAT_FIXED:
        return CAT_FIXED[cat]
    t = _text(item)
    for gid, words in RULES:
        for w in words:
            if w in t:
                return gid
    return CAT_DEFAULT.get(cat, "other")


def skin_group(item):
    cat = item.get("category", "")
    for gid, cats in SKIN_GROUPS:
        if cat in cats:
            return gid
    return "other"


def group_of(kind, item):
    return skin_group(item) if kind == "skin" else plugin_group(item)


def order(kind):
    return list(SKIN_ORDER if kind == "skin" else PLUGIN_ORDER) + ["other"]
