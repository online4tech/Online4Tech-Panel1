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

PY3 = sys.version_info[0] >= 3
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
