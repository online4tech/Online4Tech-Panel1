# -*- coding: utf-8 -*-
"""Online4Tech picks: a small curated list kept in catalog.json on GitHub."""
from __future__ import absolute_import
import io
import json
import os

from .utils import txt, valid_pkg, valid_url
from .version import PLUGIN_DIR, CATALOG_URL, TMP_CATALOG

BUNDLED = os.path.join(PLUGIN_DIR, "data", "catalog.json")


def _load(path):
    try:
        with io.open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _clean(item):
    """Validate one catalog entry; return None when it is unsafe/invalid."""
    try:
        install = item.get("install") or {}
        method = txt(install.get("method"))
        out = {
            "type": txt(item.get("type", "plugin")),
            "name": txt(item.get("name", "")).strip(),
            "version": txt(item.get("version", "")),
            "desc": txt(item.get("desc", "")),
            "method": method,
            "pkg": txt(install.get("pkg", "")),
            "url": txt(install.get("url", "")),
        }
        if not out["name"] or out["type"] not in ("plugin", "skin"):
            return None
        if method == "feed":
            if not valid_pkg(out["pkg"]):
                return None
        elif method in ("ipk", "tar"):
            if not valid_url(out["url"]):
                return None
        else:
            return None
        return out
    except Exception:
        return None


def items_for(kind):
    data = _load(TMP_CATALOG) or _load(BUNDLED) or {}
    out = []
    for raw in data.get("items", []):
        it = _clean(raw)
        if it and it["type"] == kind:
            out.append(it)
    return out


def refresh(console, callback):
    """Download catalog.json from GitHub (non-blocking). callback(ok: bool)."""
    cmd = ("wget -q -T 10 -t 1 --no-check-certificate -O %s.part '%s' && "
           "mv -f %s.part %s" % (TMP_CATALOG, CATALOG_URL, TMP_CATALOG, TMP_CATALOG))

    def done(data, retval, extra=None):
        ok = (retval == 0) and _load(TMP_CATALOG) is not None
        if not ok:
            try:
                os.remove(TMP_CATALOG)
            except Exception:
                pass
        callback(ok)

    console.ePopen(cmd, done)
