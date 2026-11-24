# -*- coding: utf-8 -*-
"""'What's new' message: which catalog items appeared since the panel last looked, and where."""
from __future__ import absolute_import

from . import catalog
from .i18n import T
from .utils import load_json, save_json

SEEN_FILE = "/etc/enigma2/o4t_seen.json"
MAX_LINES = 12
KIND = {"plugin": "nw_plugin", "skin": "nw_skin", "channels": "nw_channels"}


def _current():
    data = catalog._load(catalog.TMP_CATALOG) or catalog._load(catalog.BUNDLED) or {"items": []}
    out = []
    for raw in data["items"]:
        it = catalog._clean(raw)
        if it:
            out.append(it)
    return out


def _where(it):
    return "%s > %s" % (T(KIND.get(it["type"], "nw_plugin")), it["category"])


def check():
    """Text describing the new items (None when nothing is new).

    The first run only remembers what exists. The 'seen' list never shrinks, so an
    offline start (built-in catalog) can't make old items look new later."""
    items = _current()
    ids = [i["id"] for i in items]
    seen = load_json(SEEN_FILE, None)
    if not isinstance(seen, list):
        save_json(SEEN_FILE, ids)
        return None
    known = set(seen)
    new = [i for i in items if i["id"] not in known]
    if not new:
        return None
    save_json(SEEN_FILE, seen + [i for i in ids if i not in known])
    lines = [T("nw_head") % len(new), ""]
    if len(new) <= MAX_LINES:
        for it in new:
            lines.append("+ %s   [%s]" % (it["name"], _where(it)))
    else:
        counts = {}
        for it in new:
            counts[_where(it)] = counts.get(_where(it), 0) + 1
        shown = sorted(counts.items())
        for where, n in shown[:MAX_LINES]:
            lines.append("+ %s:  %d" % (where, n))
        if len(shown) > MAX_LINES:
            lines.append(T("nw_more") % (len(shown) - MAX_LINES))
    return "\n".join(lines)
