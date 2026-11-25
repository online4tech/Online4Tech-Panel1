# -*- coding: utf-8 -*-
"""Sidebar grouping for the store: every catalog item lands in exactly one group.

Plugins are sorted by what they do (rule based, first match wins) so no list gets huge.
Anything that matches no rule falls back to its catalog category, and finally to "other",
so nothing is ever hidden.
"""
from __future__ import absolute_import
import re

# ordered by importance (this is the order in the sidebar)
PLUGIN_ORDER = ["o4t", "panels", "players", "iptv", "cams", "subs", "epg", "sat", "maint",
                "backup", "look", "fun"]

# Only plugins Online4Tech builds/brands itself (exact lower-case names); never add third-party ones
O4T_NAMES = frozenset([
    "online4tech panel & store v7.5 gold", "online4tech web panel", "almoaddin online4tech",
    "multi-iptv-adder_by-online4tech", "multicamadder_by-online4tech",
    "screen-recorder-by-online4tech", "setpicon - online4tech",
    "iptosat_v1.9-modded-by-online4tech", "xtream2audio-by-online4tech",
    "super 17 plugins", "ahmed romeh channels",
])

SKIN_GROUPS = [
    ("skins", ["OpenATV", "OpenBH", "Egami", "OpenSPA", "OpenVIX", "PurE2", "TeamNitro"]),
    ("pli", ["OpenPLi Py3", "OpenPLi Py2"]),
    ("lcd", ["Display (LCD)"]),
    ("graphics", ["Bootlogos", "Spinners", "Picons"]),
    ("community", ["Community Skins", "XStreamity"]),
]
SKIN_ORDER = [g for g, _c in SKIN_GROUPS]

# Rules are checked in order on the lower-case NAME; the first keyword that matches wins.
# Every group is kept between 24 and 35 plugins for the current catalog (see tools/check_groups.py).
RULES = [
    ("panels", ["panel", "aio", "store", "gp4", "dreamarabia", "ajpanel", "enigmaplay", "addons",
                "dreamosat", "s4a", "levi45-addonsmanager", "ciefpplugins", "ciefpeasysetup",
                "ciefpsettingsdownloader"]),
    ("maint", ["opkg tools", "curl", "wget", "set_time_ntp", "audiomerge", "audioselection", "audioshift"]),
    ("fun", ["match", "football", "foot", "sports", "bundesliga", "horoscope", "youre", "holiday",
             "astronomy", "apod", "athan", "azkar", "hisn", "prayer", "mawaqit", "muaddhin",
             "moaddin", "shia", "alajre", "calculator", "weather", "msn", "quran", "kareem",
             "karem", "clock", "ciefpvibes", "arabicsavior", "webcam", "disk_and_cpu", "hardwareinfo", "devicemanager",
             "الأجر", "قرآن", "مواقيت"]),
    ("cams", ["cam", "keyadder", "ip2sat", "iptosat", "airnet", "beengo", "suptv", "total90",
              "silentrunner", "ipsat", "dns ", "wifi", "wireguard", "ip_checker", "net usage",
              "speedtest", "3gmodem", "crond"]),
    ("subs", ["sub", "translat", "tmdb", "tmbd", "xtraevent", "titlovi", "ssupport", "aisubtitles",
              "ترجمة", "مترجم", "mytranslator"]),
    ("epg", ["epg", "autotimer", "seriesplugin", "tvprogram", "tvtoday", "mojtv", "jedi",
             "bouquet", "channel", "chmanager", "numberzap", "duplicate", "m3ubouquet",
             "streamrelay", "whitelist", "e2editor", "e2converter", "iptvbouquets",
             "ciefpepg", "emil channels"]),
    ("sat", ["satellit", "sat editor", "ts-sat", "xmlupdate", "servicescan", "signalfinder",
             "quicksignal", "evgquick", "raedquick", "ciefpking", "ciefpparabola", "abertis",
             "motor", "astra sm", "astra-sm", "ciefp —", "morpheus883", "vhannibal", "ciefpsettings", "ciefpselect",
             "اقمار", "قمر"]),
    ("iptv", ["iptv", "xtream", "stalker", "m3u", "xklass", "xport", "tivimate", "vavoo",
              "freearhey", "hasbahca", "audio", "ipaudio", "radio", "e2player hosts"]),
    ("players", ["player", "tube", "pluto", "rakuten", "samsung", "filmxy", "mystreamer",
                 "ipstreamer", "movies", "transmission", "tsiplayer", "myhits", "quarter",
                 "livefeed", "satelliweb", "chromium", "nova", "xstreamity", "e2-tube", "xtreamity",
                 "dreamxtream", "e2iplayer", "iptvdream", "ciefpvideo", "ciefppicture",
                 "opendirectories", "ultra", "orange", "estalker"]),
    ("backup", ["backup", "flash", "boot", "neoboot", "multiboot", "format", "inodes", "mount",
                "devicemanager", "imagesdownloader", "disk", "arabic-language", "update enigma2",
                "فهارس", "ترقية", "dependenc", "opkg", "software",
                "updater", "downloader"]),
    ("look", ["skin", "spinner", "pluginbrowser", "menusort", "logo", "picon", "screen",
              "coloring", "keyboard", "infobar", "pluginmover", "pluginskin", "bitrate",
              "crashlogo", "ozeta", "atilehd", "theme", "ciefpbootlogo", "zoom", "quadpip"]),
    ("maint", ["fix", "uninstall", "remove", "cache", "explorer", "zip2", "script", "password",
               "passwd", "openwebif", "hardware", "gemini", "cuts", "acherone", "gioppy",
               "history", "volume", "patcher", "filecommander", "super", "levi45", "team",
               "wifi", "adjust"]),
]
CAT_DEFAULT = {        # used when no keyword rule matched
    "Media": "players", "Audio": "iptv", "IPTV": "iptv", "Novaler": "players", "Ciefp": "epg",
    "EPG": "epg", "Settings": "sat", "Tools": "maint", "Plugins": "maint", "Panels": "panels",
    "System": "maint", "Multiboot": "backup", "Dependencies": "backup", "Translation": "subs",
    "Community": "maint",
}


def _text(item):
    return ("%s %s" % (item.get("name", ""), item.get("desc", ""))).lower()


# any plugin whose name has the word "online..." or "o4t" is ours ("FlashOnline" is not: no word start)
O4T_WORD = re.compile(r"(?<![a-z])(online|o4t)")


def plugin_group(item):
    name = (item.get("name", "") or "").lower()
    if name in O4T_NAMES or O4T_WORD.search(name):
        return "o4t"
    for gid, words in RULES:
        for w in words:
            if w in name:
                return gid
    return CAT_DEFAULT.get(item.get("category", ""), "other")


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
