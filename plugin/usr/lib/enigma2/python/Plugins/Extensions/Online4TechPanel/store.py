# -*- coding: utf-8 -*-
"""Card-grid browser for plugins / skins: categories | cards | details."""
from __future__ import absolute_import, print_function
import os

from enigma import ePoint
from Components.ActionMap import NumberActionMap
from Components.Console import Console
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.LoadPixmap import LoadPixmap

from .groups import group_of, order as group_order
from . import catalog
from .i18n import T
from .screens import (_start_clock, mark_opening, mark_shown, ConsoleScreen, FEED_FILTER, FEED_PREFIX, OPKG_INSTALLED, _ask_restart,
                      _guard, _run, _watch_close)
from .skin import is_flat, metrics, skin_store, store_geometry, uses_rows
from .utils import (compatible, item_key, load_favs, log, parse_opkg_list, pretty_name,
                    save_favs)

FEED, FAV, LATEST = "__feed__", "__fav__", "__new__"
MAX_LATEST = 40

# Sidebar groups live in groups.py (items are sorted by what they do)

ICON_RULES = (
    ("iptv", "tv"), ("xtream", "tv"), ("epg", "calendar"), ("media", "play"), ("video", "play"),
    ("player", "play"), ("audio", "speaker"), ("sound", "speaker"), ("panel", "grid"),
    ("translat", "globe"), ("language", "globe"), ("picon", "image"), ("channel", "antenna"),
    ("ciefp", "antenna"), ("novaler", "antenna"), ("morph", "antenna"), ("vaninbal", "antenna"),
    ("system", "gear"), ("tool", "gear"), ("setting", "gear"), ("backup", "download"),
    ("restore", "download"), ("feed", "cloud"), ("skin", "palette"),
)


def icon_key(kind, category):
    cat = (category or "").lower()
    if cat == FAV:
        return "star"
    for word, key in ICON_RULES:
        if word in cat:
            return key
    return "palette" if kind == "skin" else "plug"


def clip(text, n):
    """Shorten text to n characters (counted as characters, also for UTF-8 Arabic on Python 2)."""
    text = text or ""
    py2_bytes = isinstance(text, bytes) and str is bytes
    if py2_bytes:
        text = text.decode("utf-8", "replace")
    text = u" ".join(text.split())
    if len(text) > n:
        text = text[:n - 1].rstrip() + u"..."
    return text.encode("utf-8") if py2_bytes else text


def guard_all(cls):
    for name, fn in list(cls.__dict__.items()):
        if callable(fn) and name != "__init__" and not name.startswith("__"):
            setattr(cls, name, _guard(fn))
    return cls


@guard_all
class O4TStore(Screen):
    def __init__(self, session, kind):
        self.kind = kind
        mark_opening("store-" + kind)
        self.cols, self.per, self.xy, self.off = store_geometry()
        self.flat = is_flat()
        self.rowsmode = uses_rows()
        self.skin = skin_store("O4TStore")
        Screen.__init__(self, session)
        self.console = Console()
        _watch_close(self)
        self.favs = load_favs()
        self.installed = {}
        self.show_all = False
        self.o4_query = ""
        self.cat_keys = []        # parallel to the sidebar list
        self.cat_idx = 0
        self.rows = []            # items of the selected category
        self.o4_page = 0
        self.o4_pos = 0              # card index on the page
        self.o4_focus = "side"
        self.o4_loading = False
        self["cats"] = MenuList([])
        self["title"] = Label("")
        self["search"] = Label(T("search_hint"))
        self["status"] = Label("")
        self["pager"] = Label("")
        box = Label if self.flat else Pixmap     # flat designs draw boxes as coloured labels
        self["sel"] = box()
        for i in range(self.per):
            self["cbg%d" % i] = box()
            self["ci%d" % i] = Pixmap()
            self["cn%d" % i] = Label("")
            self["cd%d" % i] = Label("")
            self["cv%d" % i] = Label("")
            self["cp%d" % i] = box()
            self["cl%d" % i] = Label("")
        self["di"] = Pixmap()
        for nm in ("dn", "dd", "dpt", "dp", "dct", "dc", "drt", "dr", "db0", "db1"):
            self[nm] = Label("")
        self["key_red"] = Label(T("k_back"))
        self["key_green"] = Label(T("k_install"))
        self["key_yellow"] = Label(T("k_remove"))
        self["key_blue"] = Label(T("k_sync"))
        self["contact"] = Label(T("contact"))
        self["clock"] = Label("")
        _start_clock(self)
        from .version import VERSION
        self["ver"] = Label("v" + VERSION)
        actions = {
            "ok": self.do_ok, "cancel": self.do_back, "red": self.do_back,
            "green": self.do_install, "yellow": self.do_remove, "blue": self.do_sync,
            "menu": self.do_search,
            "left": self.go_left, "right": self.go_right, "up": self.go_up, "down": self.go_down,
            "2": self.do_compat, "7": self.page_prev, "9": self.page_next,
        }
        self["actions"] = NumberActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions",
             "NumberActions"], actions, -1)
        self["cats"].onSelectionChanged.append(self.side_changed)
        self.onLayoutFinish.append(self.layout_done)

    # ------------------------------------------------------------ setup
    def layout_done(self):
        mark_shown()
        self.build_cats()
        self.set_focus("side")
        _run(self.console, OPKG_INSTALLED, self.got_installed)

    def got_installed(self, data, retval):
        self.installed = dict((p["pkg"], p["version"]) for p in parse_opkg_list(data))
        self.draw_page()

    def visible(self):
        items = catalog.items(self.kind)
        return items if self.show_all else [i for i in items if compatible(i)]

    def build_cats(self):
        entries = self.cat_entries()
        self.cat_keys = [e[0] for e in entries]
        self["cats"].setList([e[1] for e in entries])
        start = 1 if len(entries) > 1 else 0
        self.cat_idx = start
        try:
            self["cats"].moveToIndex(start)
        except Exception:
            pass
        self.load_category()

    def latest_rows(self):
        rows = []
        for it in catalog.latest(MAX_LATEST, None if self.show_all else compatible):
            c = dict(it)
            c["where"] = "%s > %s" % (T("nw_skin" if it["type"] == "skin" else "nw_plugin"), it["category"])
            rows.append(c)
        return rows

    def gname(self, g):
        return T("g_pcomm" if (g == "community" and self.kind == "plugin") else "g_" + g)

    def cat_entries(self):
        counts = {}
        for it in self.visible():
            g = group_of(self.kind, it)
            counts[g] = counts.get(g, 0) + 1
        order = group_order(self.kind)
        entries = [(FEED, T("cat_feed"))]
        if self.kind == "plugin":                      # "Latest additions": newest plugins, skins and tools
            n = len(self.latest_rows())
            if n:
                entries.append((LATEST, "%s (%d)" % (T("cat_new"), n)))
        entries += [(g, "%s (%d)" % (self.gname(g), counts[g])) for g in order if counts.get(g)]
        return entries

    # ------------------------------------------------------------ data
    def side_changed(self):
        try:
            idx = self["cats"].getSelectionIndex()
        except Exception:
            return
        if idx != self.cat_idx and self.cat_keys:
            self.cat_idx = idx
            self.o4_query = ""
            self.load_category()

    def current_cat(self):
        if self.o4_query:
            return None
        return self.cat_keys[self.cat_idx] if self.cat_keys else None

    def load_category(self):
        cat = self.current_cat()
        self.o4_page, self.o4_pos = 0, 0
        if self.o4_query:
            q = self.o4_query.lower()
            self.rows = [i for i in self.visible() if q in i["name"].lower()
                         or q in i.get("desc", "").lower() or q in i.get("pkg", "").lower()]
        elif cat == LATEST:
            self.rows = self.latest_rows()
        elif cat == FEED:
            self.rows = []
            self.o4_loading = True
            self["status"].setText(T("loading"))
            cmd = "opkg list 2>/dev/null | grep '^%s' | %s" % (FEED_PREFIX[self.kind], FEED_FILTER)
            _run(self.console, cmd, self.got_feed)
            self.draw_page()
            return
        else:
            self.rows = [i for i in self.visible() if group_of(self.kind, i) == cat]
        self.o4_loading = False
        self.draw_page()

    def got_feed(self, data, retval):
        if self.current_cat() != FEED:
            return
        rows = []
        for p in parse_opkg_list(data):
            p.update({"name": pretty_name(p["pkg"]), "method": "feed",
                      "category": T("cat_feed"), "type": self.kind})
            rows.append(p)
        rows.sort(key=lambda i: i["name"].lower())
        self.rows = rows
        self.o4_loading = False
        self.draw_page()

    def is_installed(self, it):
        if it.get("pkg") and it["pkg"] in self.installed:
            return True
        return bool(it.get("path")) and os.path.exists(it["path"])

    # ------------------------------------------------------------ drawing
    def pages(self):
        return max(1, (len(self.rows) + self.per - 1) // self.per)

    def page_items(self):
        return self.rows[self.o4_page * self.per:(self.o4_page + 1) * self.per]

    def px(self, name, size=None):
        try:
            m = metrics()
            return LoadPixmap(m.icon(name, size) if size else m.pix(name))
        except Exception:
            return None

    def draw_page(self):
        items = self.page_items()
        if self.o4_pos >= len(items):
            self.o4_pos = max(0, len(items) - 1)
        cat = self.current_cat()
        base = T("m_plugins") if self.kind == "plugin" else T("m_skins")
        if self.o4_query:
            self["title"].setText("%s - %s" % (base, T("search_all")))
            self["search"].setText(self.o4_query)
        else:
            name = T("cat_feed") if cat == FEED else (T("cat_new") if cat == LATEST else (self.gname(cat) if cat else ""))
            self["title"].setText(base if (not name or name == base) else "%s - %s" % (base, name))
            self["search"].setText(T("search_hint"))
        for i in range(self.per):
            has = i < len(items)
            for nm in ("cbg", "ci", "cp"):
                w = self["%s%d" % (nm, i)]
                try:
                    (w.show if has else w.hide)()
                except Exception:
                    pass
            if not has:
                for nm in ("cn", "cd", "cl", "cv"):
                    self["%s%d" % (nm, i)].setText("")
                continue
            it = items[i]
            self["cn%d" % i].setText(clip(it["name"], 24 if self.rowsmode else 18))
            self["cd%d" % i].setText(clip(it.get("desc") or it.get("category", ""),
                                          30 if self.rowsmode else 26))
            self["cv%d" % i].setText(clip(str(it.get("version") or ""), 9) if self.rowsmode else "")
            self["cl%d" % i].setText(T("k_reinstall") if self.is_installed(it) else T("k_install"))
            if not self.flat:
                try:
                    self["ci%d" % i].instance.setPixmap(
                        self.px("ci_" + icon_key(it.get("type") or self.kind, it.get("category", "")),
                                52 if self.rowsmode else 72))
                except Exception:
                    pass
        self["status"].setText("" if (items or self.o4_loading) else T("empty"))
        self["pager"].setText(T("pager") % (self.o4_page + 1, self.pages(), len(self.rows)))
        self.draw_detail()
        self.draw_sel()

    def draw_sel(self):
        try:
            if self.o4_focus == "grid" and self.page_items():
                x, y = self.xy(self.o4_pos)
                m = metrics()
                self["sel"].instance.move(ePoint(m.S(x + self.off[0]), m.S(y + self.off[1])))
                self["sel"].show()
            else:
                self["sel"].hide()
        except Exception:
            pass

    def current(self):
        items = self.page_items()
        return items[self.o4_pos] if items and self.o4_pos < len(items) else None

    def draw_detail(self):
        it = self.current()
        if not it:
            for nm in ("dn", "dd", "dpt", "dp", "dct", "dc", "drt", "dr", "db0", "db1"):
                self[nm].setText("")
            return
        self["dn"].setText(clip(it["name"], 26))
        self["dd"].setText(clip(it.get("desc", ""), 90 if self.rowsmode else 150))
        self["dpt"].setText(T("s_path"))
        path = it.get("path") or "-"
        self["dp"].setText(path if len(path) <= 44 else "..." + path[-41:])
        self["dct"].setText(T("category"))
        self["dc"].setText(clip(it.get("where") or it.get("category", "") or "-", 30))
        self["drt"].setText(T("version"))
        self["dr"].setText(clip(str(it.get("version") or "-"), 30))
        self["db0"].setText(T("k_reinstall") if self.is_installed(it) else T("k_install_now"))
        self["db1"].setText(T("k_remove"))
        if not self.flat:
            try:
                self["di"].instance.setPixmap(self.px("ci_" + icon_key(it.get("type") or self.kind, it.get("category", ""))))
            except Exception:
                pass

    # ------------------------------------------------------------ focus / keys
    def set_focus(self, where):
        self.o4_focus = where
        self.draw_sel()

    def go_left(self):
        if self.o4_focus == "side":
            return
        if self.o4_pos % self.cols == 0:
            self.set_focus("side")
        else:
            self.o4_pos -= 1
            self.after_move()

    def go_right(self):
        if self.o4_focus == "side":
            if self.page_items():
                self.set_focus("grid")
                self.draw_detail()
            return
        n = len(self.page_items())
        if self.o4_pos % self.cols < self.cols - 1 and self.o4_pos + 1 < n:
            self.o4_pos += 1
            self.after_move()

    def go_up(self):
        if self.o4_focus == "side":
            self["cats"].up()
            return
        if self.o4_pos >= self.cols:
            self.o4_pos -= self.cols
            self.after_move()
        elif self.o4_page > 0:
            self.o4_page -= 1
            self.o4_pos = min(len(self.page_items()) - 1, self.o4_pos + self.per - self.cols)
            self.draw_page()

    def go_down(self):
        if self.o4_focus == "side":
            self["cats"].down()
            return
        n = len(self.page_items())
        if self.o4_pos + self.cols < n:
            self.o4_pos += self.cols
            self.after_move()
        elif (self.o4_page + 1) * self.per < len(self.rows):
            self.o4_page += 1
            self.o4_pos = min(self.o4_pos % self.cols, len(self.page_items()) - 1)
            self.draw_page()

    def after_move(self):
        self.draw_detail()
        self.draw_sel()

    def page_prev(self):
        if self.o4_page > 0:
            self.o4_page -= 1
            self.o4_pos = 0
            self.draw_page()

    def page_next(self):
        if (self.o4_page + 1) * self.per < len(self.rows):
            self.o4_page += 1
            self.o4_pos = 0
            self.draw_page()

    def do_back(self):
        if self.o4_focus == "grid":
            self.set_focus("side")
        elif self.o4_query:
            self.o4_query = ""
            self.load_category()
        else:
            self.close()

    def do_ok(self):
        if self.o4_focus == "side":
            self.go_right()
        else:
            self.do_install()

    # ------------------------------------------------------------ actions
    def do_install(self):
        if self.o4_focus == "side":
            return self.go_right()
        it = self.current()
        cmd = catalog.install_cmd(it) if it else None
        if not cmd:
            return
        log("install: %s | %s" % (it["name"], cmd))
        self.session.openWithCallback(self.after_change, ConsoleScreen, title=it["name"],
                                      cmdlist=[cmd])

    def do_remove(self):
        it = self.current()
        cmd = catalog.remove_cmd(it) if it else None
        if not cmd:
            return

        def go(answer):
            if answer:
                log("remove: %s | %s" % (it["name"], cmd))
                self.session.openWithCallback(self.after_change, ConsoleScreen,
                                              title=it["name"], cmdlist=[cmd])
        self.session.openWithCallback(go, MessageBox, "%s\n\n%s" % (T("confirm_remove"), it["name"]),
                                      MessageBox.TYPE_YESNO)

    def after_change(self, *args):
        _run(self.console, OPKG_INSTALLED, self.got_installed)
        _ask_restart(self)

    def build_labels_only(self):
        keep = self.cat_idx
        entries = self.cat_entries()
        self["cats"].setList([e[1] for e in entries])
        try:
            self["cats"].moveToIndex(keep)
        except Exception:
            pass
        self.cat_idx = keep
        self.draw_page()

    def do_compat(self):
        self.show_all = not self.show_all
        self.session.open(MessageBox, T("compat_shown") if self.show_all else T("compat_hidden"),
                          MessageBox.TYPE_INFO, timeout=2)
        self.build_cats()

    def do_sync(self):
        def done(ok):
            self.session.open(MessageBox, T("synced") if ok else T("sync_failed"),
                              MessageBox.TYPE_INFO if ok else MessageBox.TYPE_WARNING, timeout=4)
            self.build_cats()
        catalog.refresh(self.console, done)

    def do_search(self):
        self.session.openWithCallback(self.got_search, VirtualKeyBoard, title=T("search"),
                                      text=self.o4_query)

    def got_search(self, text=None):
        if text is None:
            return
        self.o4_query = text.strip()
        self.load_category()
        if self.rows:
            self.set_focus("grid")
            self.draw_detail()
