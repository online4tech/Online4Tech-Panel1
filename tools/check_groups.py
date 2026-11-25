#!/usr/bin/env python3
"""Print how many catalog items land in each store section (plugins 24-35 per section)."""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "plugin", "usr", "lib", "enigma2", "python",
                                "Plugins", "Extensions", "Online4TechPanel"))
import importlib.util
spec = importlib.util.spec_from_file_location("groups", os.path.join(
    HERE, "..", "plugin", "usr", "lib", "enigma2", "python", "Plugins", "Extensions",
    "Online4TechPanel", "groups.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
items = json.load(open(os.path.join(HERE, "..", "catalog.json"), encoding="utf-8"))["items"]
for kind in ("plugin", "skin"):
    c = collections.defaultdict(list)
    for it in items:
        if it["type"] == kind:
            c[g.group_of(kind, it)].append(it["name"])
    print("==", kind, sum(len(v) for v in c.values()))
    for gid in g.order(kind):
        print("  %-9s %3d" % (gid, len(c.get(gid, []))))
    if "-v" in sys.argv:
        for gid, v in c.items():
            print(gid, ":", " | ".join(sorted(v)))
