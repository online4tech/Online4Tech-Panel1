#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge the Online4Tech JSON sources into one panel catalog (catalog.json, schema 2).

Sources (all in the online4tech GitHub account):
  * Online4Tech-Panel1/o4t_database.json      sections -> name / cmd / path / remove_cmd
  * online4Tech/data/enigma2-plugins.json     plugins with installCommand
  * online4Tech/data/plugins.json             plugins with telnetCommands (fills gaps)
  * online4Tech/data/enigma2-community-catalog.json   .ipk files hosted in the repo

    python3 tools/build_catalog.py                 # fetch sources from GitHub
    python3 tools/build_catalog.py --local DIR     # use local copies
    python3 tools/build_catalog.py --include-softcam
"""
import argparse
import collections
import datetime
import json
import os
import re
import shutil
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugin", "usr", "lib", "enigma2", "python", "Plugins", "Extensions")
sys.path.insert(0, PLUGIN)
from Online4TechPanel.utils import cmd_hosts, safe_cmd, safe_remove  # noqa: E402

SOURCES = {
    "o4t_database.json": "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/o4t_database.json",
    "enigma2-plugins.json": "https://raw.githubusercontent.com/online4tech/online4Tech/main/data/enigma2-plugins.json",
    "plugins.json": "https://raw.githubusercontent.com/online4tech/online4Tech/main/data/plugins.json",
    "enigma2-community-catalog.json": "https://raw.githubusercontent.com/online4tech/online4Tech/main/data/enigma2-community-catalog.json",
}

# o4t_database.json section -> (type, category)
DB_MAP = collections.OrderedDict([
    ("panels", ("plugin", "Panels")),
    ("online4tech_official", ("plugin", "Panels")),
    ("plugins", ("plugin", "Plugins")),
    ("media", ("plugin", "Media")),
    ("tools", ("plugin", "Tools")),
    ("system", ("plugin", "System")),
    ("novaler", ("plugin", "Novaler")),
    ("ciefp", ("plugin", "Ciefp")),
    ("multiboot", ("plugin", "Multiboot")),
    ("updated-dependencic", ("plugin", "Dependencies")),
    ("openatv_skins", ("skin", "OpenATV")),
    ("teamnitro_skins", ("skin", "TeamNitro")),
    ("openbh_skins", ("skin", "OpenBH")),
    ("egami_skins", ("skin", "Egami")),
    ("openpli_py3_skins", ("skin", "OpenPLi Py3")),
    ("openpli_py2_skins", ("skin", "OpenPLi Py2")),
    ("openspa_skins", ("skin", "OpenSPA")),
    ("openvix_skins", ("skin", "OpenVIX")),
    ("pure2_skins", ("skin", "PurE2")),
    ("display_skins", ("skin", "Display (LCD)")),
    ("plugin-xtreamity_skins", ("skin", "XStreamity")),
    ("bootlogos", ("skin", "Bootlogos")),
    ("spinners", ("skin", "Spinners")),
    ("picons", ("skin", "Picons")),
    ("other_channels", ("channels", "Online4Tech & Others")),
    ("ciefp_channels", ("channels", "Ciefp")),
    ("morph883_channels", ("channels", "Morph883")),
    ("vaninbal_channels", ("channels", "Vaninbal")),
])
# Not imported: favourites (duplicates), feeds, images, backup*, restore, remove, softcams
E2P_MAP = {"IPTV": "IPTV", "Audio": "Audio", "Tools": "Tools", "Translation": "Translation",
           "Panels": "Panels", "Other": "Plugins", "Settings": "Settings"}
PJ_MAP = {"EPG": "EPG", "EPG Plugins": "EPG", "IPTV": "IPTV", "IPTV Plugins": "IPTV",
          "Media": "Media", "Media Players": "Media", "Streaming": "Media",
          "Network": "Tools", "Developer Tools": "Tools", "File Managers": "Tools",
          "Utilities": "Tools", "System Tools": "System", "System Plugins": "System",
          "Backup Tools": "System", "Weather": "Plugins", "Settings": "Settings"}
SOFTCAM_RE = re.compile(r"softcam|oscam|ncam|cccam|\bemu\b|emulator|dcw|biss|mgcamd|gcam|reader|"
                        r"freeserver|free server|\bservers?\b|\bkeys?\b|gosatplus", re.I)

stats = collections.Counter()
dropped = collections.defaultdict(list)


def norm(name):
    name = re.sub(r"\(.*?\)", "", name)
    return re.sub(r"[^a-z0-9\u0600-\u06ff]", "", name.lower())


def infer_py(it):
    """Python generation an item needs ('py2' / 'py3' / '') from its category, name and command."""
    if it["category"].endswith("Py3"):
        return "py3"
    if it["category"].endswith("Py2"):
        return "py2"
    text = " ".join([it["name"], it.get("cmd", ""), it.get("url", "")]).lower()
    t3 = re.search(r"py(thon)?[-_ ]?3|python3\b", text)
    t2 = re.search(r"py(thon)?[-_ ]?2\b|python2\b", text)
    if t3 and not t2:
        return "py3"
    if t2 and not t3:
        return "py2"
    return ""


def split_name(raw):
    m = re.match(r"^(.*?)\s*\((.+)\)\s*$", raw.strip())
    return (m.group(1).strip(), m.group(2).strip()) if m else (raw.strip(), "")


def load(local):
    out = {}
    for fn, url in SOURCES.items():
        if local and os.path.exists(os.path.join(local, fn)):
            raw = open(os.path.join(local, fn), "rb").read()
        else:
            with urllib.request.urlopen(url, timeout=60) as r:
                raw = r.read()
        out[fn] = json.loads(raw.decode("utf-8"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local")
    ap.add_argument("--include-softcam", action="store_true")
    ap.add_argument("-o", "--out", default=os.path.join(ROOT, "catalog.json"))
    a = ap.parse_args()
    src = load(a.local)

    items, seen = [], set()

    def add(it, key):
        if key in seen:
            stats["duplicate"] += 1
            return
        if not a.include_softcam and it["source"] != "custom" and \
                SOFTCAM_RE.search(it["name"] + " " + it.get("cmd", "")):
            stats["excluded_softcam"] += 1
            dropped["softcam"].append(it["name"])
            return
        if it["method"] == "cmd" and not safe_cmd(it["cmd"]):
            stats["untrusted_cmd"] += 1
            dropped["untrusted"].append("%s -> %s" % (it["name"], it["cmd"][:90]))
            return
        if it.get("remove") and not safe_remove(it["remove"]):
            stats["remove_dropped"] += 1
            it.pop("remove")
        py = infer_py(it)
        if py:
            it["py"] = py
        seen.add(key)
        items.append(it)
        stats["added_" + it["source"]] += 1

    # 0) custom.json: items added by hand (highest priority, keyword filter not applied)
    try:
        with open(os.path.join(ROOT, "custom.json"), encoding="utf-8") as fh:
            custom = json.load(fh)
    except FileNotFoundError:
        custom = {}
    except ValueError as exc:
        print("::error file=custom.json::invalid JSON - %s" % exc)
        custom = {}
    for raw in custom.get("items", []):
        name, cmd = str(raw.get("name", "")).strip(), str(raw.get("cmd", "")).strip()
        if not name or not cmd:
            print("::warning file=custom.json::item skipped, 'name' and 'cmd' are required: %r" % raw)
            continue
        typ = raw.get("type", "plugin")
        cat = raw.get("category") or ("Community Skins" if typ == "skin" else "Plugins")
        it = {"type": typ, "category": cat, "name": name, "method": "cmd", "cmd": cmd,
              "source": "custom"}
        for k_src, k_dst in (("desc", "desc"), ("path", "path"), ("remove", "remove"),
                             ("py", "py"), ("images", "images")):
            if raw.get(k_src):
                it[k_dst] = raw[k_src]
        before = len(items)
        add(it, (typ, cat, norm(name)) if typ in ("skin", "channels") else (typ, norm(name)))
        if len(items) == before:
            print("::warning file=custom.json::'%s' was NOT added (host not in TRUSTED_HOSTS, "
                  "duplicate name, or invalid type)" % name)

    # 1) Online4Tech database (has path + remove command)
    db = src["o4t_database.json"]
    for section, (typ, cat) in DB_MAP.items():
        for raw in db.get(section, []):
            if "cmd" not in raw:
                continue
            name, desc = split_name(raw["name"])
            it = {"type": typ, "category": cat, "name": name, "method": "cmd",
                  "cmd": raw["cmd"], "source": "o4t-db"}
            if desc:
                it["desc"] = desc
            if raw.get("path"):
                it["path"] = raw["path"]
            if raw.get("remove_cmd"):
                it["remove"] = raw["remove_cmd"]
            key = (typ, cat, norm(name)) if typ in ("skin", "channels") else (typ, norm(name))
            add(it, key)

    # 2) enigma2-plugins.json
    for p in src["enigma2-plugins.json"]["plugins"]:
        cat = p.get("category", "Other")
        if cat == "Softcam" or not p.get("installCommand"):
            stats["skipped_no_cmd_or_softcam"] += 1
            continue
        typ, c = ("skin", "Community Skins") if cat == "Skins" else \
                 ("skin", "Picons") if cat == "Picons" else ("plugin", E2P_MAP.get(cat, "Plugins"))
        it = {"type": typ, "category": c, "name": p["name"], "method": "cmd",
              "cmd": p["installCommand"], "source": "e2-plugins"}
        if p.get("description"):
            it["desc"] = p["description"]
        imgs = (p.get("compatibility") or {}).get("images")
        if imgs:
            it["images"] = imgs
        key = (typ, c, norm(p["name"])) if typ == "skin" else (typ, norm(p["name"]))
        add(it, key)

    # 3) plugins.json (telnet commands fill what is still missing)
    for p in src["plugins.json"]["plugins"]:
        cmds = [c.get("command", "") for c in p.get("telnetCommands") or []]
        cmds = [c for c in cmds if c.strip().startswith(("wget", "opkg", "curl"))]
        cat = p.get("category", "")
        if not cmds or cat in ("Softcam",):
            continue
        typ, c = ("skin", "Picons") if cat == "Picons" else \
                 ("skin", "Community Skins") if cat == "Skins" else ("plugin", PJ_MAP.get(cat, "Plugins"))
        it = {"type": typ, "category": c, "name": p["name"], "method": "cmd", "cmd": cmds[0],
              "source": "plugins-json"}
        if p.get("arabicDescription") or p.get("description"):
            it["desc"] = p.get("arabicDescription") or p["description"]
        if p.get("version") and p["version"] not in ("متعدد", ""):
            it["version"] = p["version"]
        if p.get("supportedImages"):
            it["images"] = p["supportedImages"]
        key = (typ, c, norm(p["name"])) if typ == "skin" else (typ, norm(p["name"]))
        add(it, key)

    # 4) community .ipk files hosted in the repo (latest version of each package only)
    ipks = {}
    for i in src["enigma2-community-catalog.json"]["items"]:
        if i.get("format") != "ipk":
            continue
        base = re.sub(r"[_-]v?\d[\w.+]*(_all)?\.ipk$", "", i["name"]).replace(".ipk", "")
        base = re.sub(r"_all$", "", base)
        prev = ipks.get(base)
        ver = [int(x) for x in re.findall(r"\d+", i["name"])]
        if prev is None or ver > prev[0]:
            ipks[base] = (ver, i)
    for base, (ver, i) in sorted(ipks.items()):
        typ = i["type"]
        name = re.sub(r"^enigma2-(plugin-)?(extensions-|skins-)?", "", base).replace("-", " ").strip().title()
        it = {"type": typ, "category": "Community Skins" if typ == "skin" else "Community",
              "name": name or base, "method": "ipk", "url": i["sourceUrl"], "source": "community"}
        if i.get("bytes"):
            it["size"] = i["bytes"]
        if "display" in base or "lcdskin" in base:
            it["category"] = "Display (LCD)"
        add(it, ("ipk", norm(base)) if "display" not in base else (typ, it["category"], norm(base)))

    # skin groups that already exist in the DB make community display skins redundant: keep unique only
    cats = collections.Counter((i["type"], i["category"]) for i in items)
    updated = datetime.date.today().isoformat()
    try:  # keep the old date when nothing changed (avoids a commit per day)
        with open(a.out, encoding="utf-8") as fh:
            old = json.load(fh)
        if old.get("items") == items:
            updated = old.get("updated", updated)
    except Exception:
        pass
    out = {"schema": 2, "updated": updated,
           "note": "Generated by tools/build_catalog.py - do not edit by hand.",
           "items": items}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    bundled = os.path.join(PLUGIN, "Online4TechPanel", "data", "catalog.json")
    os.makedirs(os.path.dirname(bundled), exist_ok=True)
    shutil.copyfile(a.out, bundled)
    print("items:", len(items), " size: %d KB" % (os.path.getsize(a.out) // 1024))
    for (t, c), n in sorted(cats.items()):
        print("  %-7s %-18s %d" % (t, c, n))
    print("stats:", dict(stats))
    for k, v in dropped.items():
        print("dropped[%s] %d: %s" % (k, len(v), v[:12]))


if __name__ == "__main__":
    main()
