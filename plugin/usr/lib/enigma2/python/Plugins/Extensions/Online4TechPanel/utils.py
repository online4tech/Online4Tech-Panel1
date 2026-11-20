# -*- coding: utf-8 -*-
"""Small Python 2/3 compatibility helpers."""
from __future__ import absolute_import, print_function
import io
import re
import sys

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
