# -*- coding: utf-8 -*-
"""Small Python 2/3 compatibility helpers."""
from __future__ import absolute_import, print_function
import hashlib
import io
import json
import os
import re
import sys
import time

try:
    from shlex import quote as shquote
except ImportError:  # Python 2
    from pipes import quote as shquote

try:
    from urllib.parse import urlparse
except ImportError:  # Python 2
    from urlparse import urlparse

PY3 = sys.version_info[0] >= 3

# Install commands may only download from these hosts (defence in depth: the
# catalog is fetched from the internet and its commands run as root).
TRUSTED_HOSTS = frozenset([
    "raw.githubusercontent.com", "github.com", "codeload.github.com",
    "objects.githubusercontent.com", "gitlab.com", "dreambox4u.com",
    "www.dreambox4u.com", "xfayez95.github.io", "download.blue-panel.com",
    "feeds2.mynonpublic.com", "updates.mynonpublic.com",
    "events.r108.me",
])
_URL_RE = re.compile(r"https?://[^\s\"'|;&<>()]+")
_PM = r"(opkg|apt-get) (install|remove|update|upgrade)( [A-Za-z0-9._+-]+)*"
_OPKG_RE = re.compile(r"^" + _PM + r"( && " + _PM + r")?$")
_RM_RE = re.compile(r"^rm -(rf|f|r) ((\'/[^\']+\'|/[^\s;|&<>$`]+) ?)+( && opkg update)?$")
_PKG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+_-]*$")


def txt(s):
    """Return a native `str` (bytes on py2, text on py3) for any input."""
    if s is None:
        return ""
    if PY3:
        if isinstance(s, bytes):
            return s.decode("utf-8", "replace")
        return s
    if isinstance(s, type(u"")):
        return s.encode("utf-8")
    return s


def read_file(path, default=""):
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
            return txt(fh.read())
    except Exception:
        return default


def valid_pkg(name):
    return bool(name) and bool(_PKG_RE.match(name))


def valid_url(url):
    return bool(url) and (url.startswith("http://") or url.startswith("https://")) \
        and not re.search(r"[\s'\"`$;|&<>]", url)


def version_tuple(v):
    nums = re.findall(r"\d+", v or "")
    return tuple(int(n) for n in nums) or (0,)


def pretty_name(pkg):
    for p in ("enigma2-plugin-extensions-", "enigma2-plugin-skins-",
              "enigma2-plugin-systemplugins-", "enigma2-plugin-"):
        if pkg.startswith(p):
            pkg = pkg[len(p):]
            break
    return pkg.replace("-", " ").replace("_", " ").strip().title() or pkg


def parse_opkg_list(text):
    """`opkg list` / `list-installed`: 'pkg - version - description'."""
    out = []
    for line in text.splitlines():
        parts = line.split(" - ", 2)
        if len(parts) >= 2 and valid_pkg(parts[0].strip()):
            out.append({"pkg": parts[0].strip(), "version": parts[1].strip(),
                        "desc": parts[2].strip() if len(parts) > 2 else ""})
    return out


def cmd_hosts(cmd):
    return set(urlparse(u).netloc.lower() for u in _URL_RE.findall(cmd or ""))


def safe_cmd(cmd):
    """An install command is accepted when it only talks to trusted hosts."""
    if not cmd or len(cmd) > 3000 or "\n" in cmd or "\x00" in cmd:
        return False
    hosts = cmd_hosts(cmd)
    if not hosts:
        return bool(_OPKG_RE.match(cmd)) or cmd == "rm -rf /var/cache/opkg/* && opkg update"
    return all(h in TRUSTED_HOSTS for h in hosts)


def safe_remove(cmd):
    """Only plain `rm` of absolute, non-shallow paths (or `opkg remove`)."""
    if not cmd or len(cmd) > 1500 or "\n" in cmd:
        return False
    if _OPKG_RE.match(cmd):
        return True
    if not _RM_RE.match(cmd):
        return False
    for path in re.findall(r"\'(/[^\']+)\'|(?<![\w'])(/[^\s;|&<>$`']+)", cmd.split(" && ")[0]):
        p = path[0] or path[1]
        if len([c for c in p.split("/") if c]) < 3 or ".." in p:
            return False
    return True


VU = {"duo4k": "Duo 4K", "duo4kse": "Duo 4K SE", "uno4k": "Uno 4K", "uno4kse": "Uno 4K SE",
      "ultimo4k": "Ultimo 4K", "solo4k": "Solo 4K", "zero4k": "Zero 4K", "duo2": "Duo2",
      "solo2": "Solo2", "solose": "Solo SE", "solose v2": "Solo SE V2", "ultimo": "Ultimo",
      "uno": "Uno", "zero": "Zero", "duo": "Duo", "solo": "Solo"}
OTHER = {"dm900": "Dreambox DM900", "dm920": "Dreambox DM920", "dreamone": "Dreambox One",
         "dreamtwo": "Dreambox Two", "dm525": "Dreambox DM525", "hd51": "AX HD51",
         "h7": "Zgemma H7", "h9": "Zgemma H9", "gbquad4k": "GigaBlue Quad 4K",
         "gbue4k": "GigaBlue UE 4K", "osmio4k": "Edision OSmio4K", "osmio4kplus": "Edision OSmio4K Plus"}


def _device_name_from_proc():
    """Receiver name guessed from /proc and the hostname, e.g. 'Vu+ Duo 4K' (best effort)."""
    def first(*paths):
        for path in paths:
            val = read_file(path).strip()
            if val:
                return val
        return ""
    vu = first("/proc/stb/info/vumodel").lower()
    raw = first("/proc/stb/info/boxtype", "/proc/stb/info/model", "/proc/stb/info/hwmodel")
    host = read_file("/etc/hostname").strip().lower()
    for key in (vu, raw.lower(), host):
        k = key.replace("vu+", "").replace("vu", "", 1) if key.startswith("vu") else key
        if key.startswith("vu") and k in VU:
            return "Vu+ " + VU[k]
        if key in VU and (vu or host.startswith("vu")):
            return "Vu+ " + VU[key]
        if key in OTHER:
            return OTHER[key]
    return (first("/proc/stb/info/model") or raw or host or "-").upper() if (raw or host) else "-"


BRANDS = ("Vu+", "Dreambox", "Zgemma", "AX", "GigaBlue", "Edision", "Octagon", "Mutant", "Formuler",
          "Xtrend", "Technomate", "Amiko", "Medialink", "Openbox", "Golden Interstar", "WeTek")


def receiver_model():
    """(brand, full name, model code) e.g. ('Vu+', 'Vu+ Duo 4K', 'vuduo4k').

    The image's own branding data is used first (it knows the marketing name), then Enigma2's
    HardwareInfo, then the /proc based guess."""
    brand = name = code = ""
    try:
        from boxbranding import getMachineBrand, getMachineName
        brand, name = getMachineBrand(), getMachineName()
    except Exception:
        pass
    try:
        from boxbranding import getMachineBuild
        code = getMachineBuild()
    except Exception:
        pass
    if not name:
        try:
            from Components.SystemInfo import BoxInfo
            brand = BoxInfo.getItem("displaybrand") or BoxInfo.getItem("brand") or ""
            name = BoxInfo.getItem("displaymodel") or BoxInfo.getItem("model") or ""
            code = code or BoxInfo.getItem("machinebuild") or ""
        except Exception:
            pass
    if not code:
        for path in ("/proc/stb/info/boxtype", "/proc/stb/info/model", "/proc/stb/info/vumodel"):
            code = read_file(path).strip()
            if code:
                break
    brand, name = (brand or "").strip(), (name or "").strip()
    if name:
        full = name if (not brand or name.lower().startswith(brand.lower())) else "%s %s" % (brand, name)
    else:
        full = _device_name_from_proc()
        if not brand:
            for b in BRANDS:
                if full.lower().startswith(b.lower() + " "):
                    brand = b
                    break
    return brand or "-", full or "-", code or "-"


def device_name():
    """Human readable receiver name, e.g. 'Vu+ Duo 4K'."""
    return receiver_model()[1]


def chipset_name():
    for path in ("/proc/stb/info/chipset", "/proc/stb/info/soc", "/proc/stb/info/socfamily"):
        v = read_file(path).strip()
        if v:
            return v.upper()
    return "-"


def cpu_summary():
    """e.g. 'ARMv7 Processor rev 1 (v7l)  x 4 cores  1.5 GHz'."""
    names, cores = "", 0
    for line in read_file("/proc/cpuinfo").splitlines():
        k, _sep, v = line.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "processor":
            cores += 1
        elif k in ("model name", "cpu model", "hardware", "system type") and not names:
            names = v
    out = names or "-"
    if cores > 1:
        out += "  x %d" % cores
    try:
        mhz = float(read_file("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq").strip()) / 1000.0
        out += "  %.1f GHz" % (mhz / 1000.0)
    except Exception:
        pass
    return out


def tuner_summary():
    """e.g. '2 x DVB-S2, 1 x DVB-T2' from /proc/bus/nim_sockets."""
    counts, order = {}, []
    for line in read_file("/proc/bus/nim_sockets").splitlines():
        line = line.strip()
        if line.startswith("Type:"):
            t = line.split(":", 1)[1].strip()
            if t not in counts:
                order.append(t)
            counts[t] = counts.get(t, 0) + 1
    return ", ".join("%d x %s" % (counts[t], t) for t in order) if order else "-"


def fmt_size(mb):
    return "%.1f GB" % (mb / 1024.0) if mb >= 1024 else "%d MB" % mb


def usage(used_mb, total_mb):
    """('412 MB / 1.8 GB  (23%)', 23)"""
    pct = int(round(100.0 * used_mb / total_mb)) if total_mb else 0
    return "%s / %s  (%d%%)" % (fmt_size(used_mb), fmt_size(total_mb), pct), pct


def ram_usage():
    mem = {}
    for line in read_file("/proc/meminfo").splitlines():
        p = line.replace(":", " ").split()
        if len(p) >= 2 and p[1].isdigit():
            mem[p[0]] = int(p[1])
    total = mem.get("MemTotal", 0) // 1024
    free = mem.get("MemAvailable", mem.get("MemFree", 0)) // 1024
    return max(0, total - free), total


def disk_usage(path):
    try:
        st = os.statvfs(path)
        total = st.f_blocks * st.f_frsize // 1048576
        free = st.f_bavail * st.f_frsize // 1048576
        return max(0, total - free), total
    except Exception:
        return 0, 0


def storage_device():
    """(label, mount point) of the main external drive, or ('', '')."""
    for label, mp in (("HDD", "/media/hdd"), ("USB", "/media/usb"), ("USB", "/media/usb1"),
                      ("MMC", "/media/mmc")):
        if os.path.ismount(mp):
            return label, mp
    for line in read_file("/proc/mounts").splitlines():
        p = line.split()
        if len(p) > 1 and p[0].startswith("/dev/") and p[1].startswith("/media/"):
            return os.path.basename(p[1]).upper(), p[1]
    return "", ""


def format_uptime(seconds):
    d, rest = divmod(int(seconds), 86400)
    h, rest = divmod(rest, 3600)
    m = rest // 60
    return ("%dd " % d if d else "") + "%dh %02dm" % (h, m)


def receiver_temp():
    for path, div in (("/proc/stb/fp/temp_sensor_avs", 1.0), ("/proc/stb/fp/temp_sensor", 1.0),
                      ("/sys/class/thermal/thermal_zone0/temp", 1000.0),
                      ("/proc/stb/sensors/temp0/value", 1.0)):
        try:
            t = float(read_file(path).strip()) / div
            if 0 < t < 150:
                return int(round(t))
        except Exception:
            continue
    return None


def mac_address():
    base = "/sys/class/net"
    try:
        names = sorted(n for n in os.listdir(base) if n != "lo")
    except Exception:
        return "-"
    for pick_up in (True, False):
        for n in names:
            if pick_up and read_file("%s/%s/operstate" % (base, n)).strip() != "up":
                continue
            mac = read_file("%s/%s/address" % (base, n)).strip()
            if mac and mac != "00:00:00:00:00:00":
                return mac.upper()
    return "-"


def image_build_date():
    for line in read_file("/etc/image-version").splitlines():
        k, _sep, v = line.partition("=")
        if k.strip().lower() in ("date", "builddate", "build_date") and v.strip():
            d = v.strip()
            return "%s-%s-%s" % (d[:4], d[4:6], d[6:8]) if d.isdigit() and len(d) >= 8 else d
    return "-"


def image_info():
    """(name, version) of the running image, e.g. ('EGAMI', '11.0 (build 123)')."""
    name = ver = ""
    try:
        from boxbranding import getImageDistro, getImageVersion, getImageBuild
        name, ver = getImageDistro(), getImageVersion()
        b = getImageBuild()
        if b and b not in ("", "0"):
            ver = "%s.%s" % (ver, b)
    except Exception:
        pass
    if not name:
        data = {}
        for path in ("/etc/image-version", "/etc/os-release"):
            for line in read_file(path).splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    data.setdefault(k.strip().lower(), v.strip().strip('"'))
        name = data.get("distro") or data.get("creator") or data.get("name") or data.get("id") or ""
        ver = data.get("imageversion") or data.get("version") or data.get("version_id") or ""
        if not ver and data.get("build"):
            ver = data["build"]
    return (name or "-"), (ver or "-")


def local_ip():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))     # no packet is sent; just picks the route
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "-"


def detect_image_group():
    """Skin category that best matches this receiver's image."""
    blob = (read_file("/etc/image-version") + read_file("/etc/issue") +
            read_file("/etc/os-release")).lower()
    for key, cat in (("openatv", "OpenATV"), ("openbh", "OpenBH"), ("egami", "Egami"),
                     ("openspa", "OpenSPA"), ("openvix", "OpenVIX"), ("pure2", "PurE2"),
                     ("nitro", "TeamNitro")):
        if key in blob:
            return cat
    if "openpli" in blob or "pli" in blob:
        return "OpenPLi Py3" if PY3 else "OpenPLi Py2"
    return ""


# ---------------------------------------------------------------- settings
SETTINGS_FILE = "/etc/enigma2/o4t_settings.json"
FAV_FILE = "/etc/enigma2/o4t_favorites.json"
LOG_FILE = "/tmp/o4t_panel.log"
THEMES = ["cyan", "violet", "green", "orange", "pink"]
LANGS = ["auto", "ar", "en"]


def _native(o):
    """json on py2 gives unicode: convert to native str recursively."""
    if isinstance(o, dict):
        return dict((_native(k), _native(v)) for k, v in o.items())
    if isinstance(o, list):
        return [_native(v) for v in o]
    return txt(o) if not isinstance(o, (int, float, bool, type(None))) else o


def load_json(path, default):
    try:
        with io.open(path, "r", encoding="utf-8") as fh:
            return _native(json.load(fh))
    except Exception:
        return default


def save_json(path, data):
    try:
        tmp = path + ".tmp"
        with io.open(tmp, "w", encoding="utf-8") as fh:
            fh.write(type(u"")(json.dumps(data, ensure_ascii=True)))
        os.rename(tmp, path)
        return True
    except Exception:
        return False


def get_setting(key, default):
    data = load_json(SETTINGS_FILE, {})
    return data.get(key, default) if isinstance(data, dict) else default


def web_port():
    """Port of the web control page: 9095 by default (the old 8080 default is migrated)."""
    from .version import WEB_PORT
    try:
        port = int(get_setting("web_port", WEB_PORT))
    except (TypeError, ValueError):
        return WEB_PORT
    if port == 8080 or not 1 <= port <= 65535:
        return WEB_PORT
    return port


def set_setting(key, value):
    data = load_json(SETTINGS_FILE, {})
    if not isinstance(data, dict):
        data = {}
    data[key] = value
    return save_json(SETTINGS_FILE, data)


def cycle_setting(key, values, default):
    cur = get_setting(key, default)
    nxt = values[(values.index(cur) + 1) % len(values)] if cur in values else values[0]
    set_setting(key, nxt)
    return nxt


# ---------------------------------------------------------------- favourites
def item_key(it):
    return "%s|%s|%s" % (it.get("type", ""), it.get("category", ""), it.get("name", ""))


def load_favs():
    data = load_json(FAV_FILE, [])
    return set(k for k in data if isinstance(k, str)) if isinstance(data, list) else set()


def save_favs(favs):
    return save_json(FAV_FILE, sorted(favs))


# ---------------------------------------------------------------- misc
def compatible(it):
    """False when the item needs the other Python generation."""
    py = it.get("py")
    if py == "py3" and not PY3:
        return False
    if py == "py2" and PY3:
        return False
    return True


def log(msg):
    """Append a line to /tmp/o4t_panel.log (kept small)."""
    try:
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 200000:
            os.remove(LOG_FILE)
        with io.open(LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(type(u"")("%s  %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), txt(msg))))
    except Exception:
        pass


def short_id(text):
    """Stable 12-char id for a native string (works on py2 and py3)."""
    raw = text.encode("utf-8") if PY3 else text
    return hashlib.sha1(raw).hexdigest()[:12]
