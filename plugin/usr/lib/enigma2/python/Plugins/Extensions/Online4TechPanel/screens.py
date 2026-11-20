# -*- coding: utf-8 -*-
"""All UI screens of Online4Tech Panel (Python 2 / 3 compatible)."""
from __future__ import absolute_import, print_function
import os
import sys
import traceback

from enigma import ePoint
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Console import Console
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ScrollLabel import ScrollLabel
from Screens.Console import Console as ConsoleScreen
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.LoadPixmap import LoadPixmap

from . import catalog
from .i18n import T
from .skin import MAIN_POS, metrics, skin_list, skin_main, skin_text, theme
from .utils import (LANGS, THEMES, LOG_FILE, PY3, compatible, cmd_hosts, cycle_setting,
                    detect_image_group, get_setting, item_key, load_favs, log, parse_opkg_list,
                    pretty_name, read_file, save_favs, shquote, txt, valid_pkg, valid_url,
                    version_tuple)
from .version import (HOME_URL, INSTALL_URL, SLOGAN, TMP_VERSION, VERSION,
                      VERSION_URL)

OPKG_INSTALLED = "opkg list-installed 2>/dev/null | grep '^enigma2-plugin-'"
FEED_FILTER = "grep -Ev '^[^ ]+-(src|dbg|dev|po|meta) '"
FEED_PREFIX = {"plugin": "enigma2-plugin-extensions-", "skin": "enigma2-plugin-skins-"}


GUARDED = ("layout_done", "open_current", "sync_catalog", "reload", "got_installed", "got_feed",
           "refresh_view", "loaded", "apply", "finished", "start", "build", "show_info",
           "got_version", "after", "after_change", "got_filter", "key_green", "key_yellow",
           "key_blue", "key_menu", "toggle_fav", "toggle_compat", "install_favs", "show_cats",
           "show_items", "load_feed", "go_back", "child_closed", "render_info", "key_yellow", "key_blue", "sel_changed", "move", "pick")


def _guard(fn):
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except Exception:
            tb = traceback.format_exc()
            log("ERROR in %s:\n%s" % (fn.__name__, tb))
            try:
                self.session.open(MessageBox, "Online4Tech Panel error in %s:\n%s\n\n"
                                  "Details: /tmp/o4t_panel.log" % (fn.__name__, tb.strip().splitlines()[-1]),
                                  MessageBox.TYPE_ERROR, timeout=12)
            except Exception:
                pass
    wrapper.__name__ = fn.__name__
    return wrapper


def guarded(cls):
    for name in GUARDED:
        fn = cls.__dict__.get(name)
        if fn is not None and callable(fn):
            setattr(cls, name, _guard(fn))
    return cls


def _run(console, cmd, cb):
    def done(data, retval, extra=None):
        if getattr(console, "_o4t_dead", False):   # screen already closed
            return
        cb(txt(data), retval)
    console.ePopen(cmd, done)


def _watch_close(screen):
    """Stop late console callbacks from touching a screen that has been closed."""
    def cleanup():
        screen.console._o4t_dead = True
        try:
            screen.console.killAll()
        except Exception:
            pass
    screen.onClose.append(cleanup)


def _ask_restart(screen):
    def answer(yes):
        if yes:
            screen.session.open(TryQuitMainloop, 3)
    screen.session.openWithCallback(answer, MessageBox, T("restart_q"), MessageBox.TYPE_YESNO)


def _confirm(screen, text, fn):
    def answer(yes):
        if yes:
            fn()
    screen.session.openWithCallback(answer, MessageBox, text, MessageBox.TYPE_YESNO)


# =====================================================================
# Main menu
# =====================================================================
@guarded
class O4TMain(Screen):
    MENU = ["plugins", "skins", "updates", "installed", "tools", "info", "selfupdate", "about"]

    def __init__(self, session):
        self.skin = skin_main()
        Screen.__init__(self, session)
        self.console = Console()
        _watch_close(self)
        self.idx = 0
        self["title"] = Label("Online4Tech Panel")
        self["slogan"] = Label(SLOGAN)
        self["ver"] = Label("v" + VERSION)
        self["hint"] = Label("")
        self["sel"] = Pixmap()
        for i, key in enumerate(self.MENU):
            self["ic%d" % i] = Pixmap()
            self["tt%d" % i] = Label(T("m_" + key))
            self["ts%d" % i] = Label(T("s_" + key))
        self["key_red"] = Label(T("k_exit"))
        self["key_green"] = Label(T("k_open"))
        self["key_yellow"] = Label(T("k_catalog"))
        self["key_blue"] = Label(T("k_about"))
        actions = {
            "ok": self.open_current, "cancel": self.close, "red": self.close,
            "green": self.open_current, "yellow": self.sync_catalog,
            "blue": lambda: self.session.open(O4TAbout),
            "left": lambda: self.move(-1), "right": lambda: self.move(1),
            "up": lambda: self.move(-4), "down": lambda: self.move(4),
        }
        for n in range(1, 9):
            actions[str(n)] = (lambda n=n: self.pick(n - 1))
        self["actions"] = NumberActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions", "NumberActions"], actions, -1)
        self.onLayoutFinish.append(self.layout_done)

    def layout_done(self):
        m = metrics()
        for i in range(len(self.MENU)):
            try:
                self["ic%d" % i].instance.setPixmap(LoadPixmap(m.pix("ic%d" % i)))
            except Exception:
                pass
        self.update_sel()
        catalog.refresh(self.console, lambda ok: None)  # silent background sync

    def update_sel(self):
        m = metrics()
        x, y = MAIN_POS[self.idx]
        try:
            self["sel"].instance.move(ePoint(m.S(x - 16), m.S(y - 16)))
        except Exception:
            pass
        self["hint"].setText(T("h_" + self.MENU[self.idx]))

    def move(self, step):
        self.idx = (self.idx + step) % len(self.MENU)
        self.update_sel()

    def pick(self, i):
        self.idx = i
        self.update_sel()
        self.open_current()

    def sync_catalog(self):
        def done(ok):
            self.session.open(MessageBox, T("synced") if ok else T("sync_failed"),
                              MessageBox.TYPE_INFO if ok else MessageBox.TYPE_WARNING, timeout=4)
        catalog.refresh(self.console, done)

    def open_current(self):
        key = self.MENU[self.idx]
        if key == "plugins":
            self.session.open(O4TPackages, "plugin")
        elif key == "skins":
            self.session.open(O4TPackages, "skin")
        elif key == "updates":
            self.session.open(O4TUpdates)
        elif key == "installed":
            self.session.open(O4TInstalled)
        elif key == "tools":
            self.session.open(O4TTools)
        elif key == "info":
            self.session.open(O4TInfo)
        elif key == "selfupdate":
            self.session.open(O4TSelfUpdate)
        else:
            self.session.open(O4TAbout)


# =====================================================================
# Generic list screen (list on the left, details on the right)
# =====================================================================
@guarded
class O4TListBase(Screen):
    MENU_TITLE = "m_plugins"

    def __init__(self, session):
        self.skin = skin_list(self.__class__.__name__)
        Screen.__init__(self, session)
        self.console = Console()
        _watch_close(self)
        self.items = []
        self["title"] = Label(T(self.MENU_TITLE))
        self["slogan"] = Label(SLOGAN)
        self["ver"] = Label("v" + VERSION)
        self["list"] = MenuList([])
        self["status"] = Label("")
        self["detail"] = ScrollLabel("")
        for c in ("red", "green", "yellow", "blue"):
            self["key_" + c] = Label("")
        self["key_red"].setText(T("k_back"))
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions"],
            {"ok": self.key_green, "cancel": self.go_back, "red": self.go_back,
             "green": self.key_green, "yellow": self.key_yellow, "blue": self.key_blue,
             "menu": self.key_menu,
             "up": self["list"].up, "down": self["list"].down,
             "left": self["list"].pageUp, "right": self["list"].pageDown}, -1)
        self["list"].onSelectionChanged.append(self.sel_changed)
        self.onLayoutFinish.append(self.reload)

    # -- to override
    def go_back(self):
        self.close()

    def reload(self):
        pass

    def label_for(self, item):
        return item.get("name", "")

    def detail_for(self, item):
        return item.get("name", "")

    def key_green(self):
        pass

    def key_yellow(self):
        pass

    def key_blue(self):
        pass

    def key_menu(self):
        pass

    # -- helpers
    def run(self, cmd, cb):
        _run(self.console, cmd, cb)

    def set_status(self, text):
        self["status"].setText(text)

    def set_items(self, items, empty_text=None, keep=False):
        idx = 0
        if keep:
            try:
                idx = self["list"].getSelectionIndex()
            except Exception:
                idx = 0
        self.items = items
        self["list"].setList([self.label_for(i) for i in items])
        if keep and items:
            try:
                self["list"].moveToIndex(min(idx, len(items) - 1))
            except Exception:
                pass
        self.set_status("" if items else (empty_text or T("empty")))
        self.sel_changed()

    def current(self):
        if not self.items:
            return None
        try:
            idx = self["list"].getSelectionIndex()
            return self.items[idx]
        except Exception:
            return None

    def sel_changed(self):
        item = self.current()
        self["detail"].setText(self.detail_for(item) if item else "")


# =====================================================================
# Plugins / Skins browser
# =====================================================================
@guarded
class O4TPackages(O4TListBase):
    """Category list -> item list (plugins or skins) with favourites and compat filter."""
    FEED = "__feed__"
    FAV = "__fav__"

    def __init__(self, session, kind, cat=None, flt=""):
        self.kind = kind
        self.MENU_TITLE = "m_plugins" if kind == "plugin" else "m_skins"
        # Root screen shows the categories; opening one pushes a NEW screen so that
        # "back" is a plain close() (re-filling one list in place crashed some images).
        self.root = cat is None and not flt
        self.cat = cat           # None (non-root) = search across all categories
        self.filter = flt
        self.start_filter = flt
        self.show_all = False    # show items for the other Python generation too
        self.installed = {}
        self.favs = load_favs()
        self.recommended = detect_image_group() if kind == "skin" else ""
        O4TListBase.__init__(self, session)
        self["nums"] = NumberActionMap(
            ["NumberActions"],
            {"1": lambda *a: self.toggle_fav(), "2": lambda *a: self.toggle_compat(),
             "3": lambda *a: self.install_favs()}, -1)
        self["key_blue"].setText(T("k_sync"))
        self.set_keys()

    # ---- state helpers
    def in_cats(self):
        return self.root

    def set_keys(self):
        self["key_green"].setText(T("k_open_cat") if self.in_cats() else T("k_install"))
        self["key_yellow"].setText("" if self.in_cats() else T("k_remove"))
        self["title"].setText(self.title_text())

    def title_text(self):
        base = T(self.MENU_TITLE)
        if self.filter and self.cat is None:
            return "%s - %s" % (base, T("search_all"))
        if self.cat == self.FEED:
            return "%s - %s" % (base, T("cat_feed"))
        if self.cat == self.FAV:
            return "%s - %s" % (base, T("cat_fav"))
        return "%s - %s" % (base, self.cat) if self.cat else base

    def go_back(self):
        if not self.root and self.filter != self.start_filter:
            self.filter = self.start_filter
            self.refresh_view()
        else:
            self.close()

    # ---- loading
    def reload(self):
        self.set_status(T("loading"))
        self.run(OPKG_INSTALLED, self.got_installed)

    def got_installed(self, data, retval):
        self.installed = dict((p["pkg"], p["version"]) for p in parse_opkg_list(data))
        self.refresh_view()

    def visible(self):
        items = catalog.items(self.kind)
        return items if self.show_all else [i for i in items if compatible(i)]

    def refresh_view(self, keep=False):
        self.set_keys()
        if self.cat == self.FEED:
            self.load_feed()
        elif self.in_cats():
            self.show_cats(keep)
        else:
            self.show_items(keep)

    def show_cats(self, keep=False):
        cats = catalog.categories(self.kind, self.visible())
        if self.recommended:
            cats.sort(key=lambda c: 0 if c[0] == self.recommended else 1)
        entries = [{"_cat": self.FEED, "name": T("cat_feed"), "count": None}]
        favs = self.fav_items()
        if favs:
            entries.append({"_cat": self.FAV, "name": T("cat_fav"), "count": len(favs)})
        entries += [{"_cat": c, "name": c, "count": n} for c, n in cats]
        self.set_items(entries, keep=keep)

    def match(self, it):
        f = self.filter.lower()
        return not f or f in it["name"].lower() or f in it.get("desc", "").lower() \
            or f in it.get("pkg", "").lower()

    def fav_items(self):
        return [i for i in catalog.items(self.kind) if item_key(i) in self.favs]

    def show_items(self, keep=False):
        if self.cat == self.FAV:
            out = [i for i in self.fav_items() if self.match(i)]
            self.set_items(out, T("fav_empty"), keep=keep)
            return
        out = [i for i in self.visible()
               if (self.cat is None or i["category"] == self.cat) and self.match(i)]
        self.set_items(out, keep=keep)

    def load_feed(self):
        self.set_items([])
        self.set_status(T("loading"))
        cmd = "opkg list 2>/dev/null | grep '^%s' | %s" % (FEED_PREFIX[self.kind], FEED_FILTER)
        self.run(cmd, self.got_feed)

    def got_feed(self, data, retval):
        items = []
        for p in parse_opkg_list(data):
            p.update({"name": pretty_name(p["pkg"]), "method": "feed", "category": T("cat_feed"),
                      "type": self.kind})
            items.append(p)
        items.sort(key=lambda i: i["name"].lower())
        self.set_items([i for i in items if self.match(i)], T("empty_feed"))

    # ---- rendering
    def is_installed(self, it):
        if it.get("pkg") and it["pkg"] in self.installed:
            return True
        return bool(it.get("path")) and os.path.exists(it["path"])

    def label_for(self, it):
        if "_cat" in it:
            label = it["name"] if it["count"] is None else "%s   (%d)" % (it["name"], it["count"])
            if self.recommended and it["_cat"] == self.recommended:
                label += "   - " + T("recommended")
            return label
        return ("*" if self.is_installed(it) else " ") + ("+" if item_key(it) in self.favs else " ") \
            + " " + it["name"]

    def detail_for(self, it):
        if "_cat" in it:
            if it["_cat"] == self.FEED:
                return "%s\n\n%s" % (it["name"], T("feed_hint"))
            if it["_cat"] == self.FAV:
                return "%s\n\n%d %s\n\n%s" % (it["name"], it["count"], T("n_items"), T("fav_hint"))
            lines = [it["name"], "", "%d %s" % (it["count"], T("n_items")), "", T("cat_hint")]
            if self.recommended and it["_cat"] == self.recommended:
                lines += ["", T("recommended")]
            return "\n".join(lines)
        lines = [it["name"], "",
                 "%s: %s" % (T("status"), T("installed_yes") if self.is_installed(it)
                             else T("installed_no")),
                 "%s: %s" % (T("category"), it.get("category", ""))]
        if item_key(it) in self.favs:
            lines.append("+ " + T("is_fav"))
        if not compatible(it):
            lines.append("! " + T("not_compat"))
        if it.get("version"):
            lines.append("%s: %s" % (T("version"), it["version"]))
        if it.get("pkg"):
            lines.append("%s: %s" % (T("package"), it["pkg"]))
        hosts = sorted(cmd_hosts(it.get("url") or it.get("cmd") or ""))
        if hosts:
            lines.append("%s: %s" % (T("dl_from"), ", ".join(hosts)))
        if it.get("images"):
            lines.append("%s: %s" % (T("images"), ", ".join(it["images"])))
        if it.get("desc"):
            lines += ["", it["desc"]]
        lines += ["", T("hint_items")]
        return "\n".join(lines)

    # ---- favourites / compat (number keys)
    def toggle_fav(self):
        it = self.current()
        if not it or "_cat" in it or "method" not in it or it.get("method") == "feed":
            return
        key = item_key(it)
        if key in self.favs:
            self.favs.discard(key)
            msg = T("fav_removed")
        else:
            self.favs.add(key)
            msg = T("fav_added")
        save_favs(self.favs)
        self.session.open(MessageBox, "%s\n%s" % (msg, it["name"]), MessageBox.TYPE_INFO,
                          timeout=1)
        self.refresh_view(keep=True)

    def toggle_compat(self):
        self.show_all = not self.show_all
        self.session.open(MessageBox, T("compat_shown") if self.show_all else T("compat_hidden"),
                          MessageBox.TYPE_INFO, timeout=2)
        self.refresh_view(keep=True)

    def install_favs(self):
        cmds = []
        for it in self.fav_items():
            c = self.install_cmd(it)
            if c:
                cmds.append(c)
        if not cmds:
            self.session.open(MessageBox, T("fav_empty"), MessageBox.TYPE_INFO, timeout=3)
            return

        def go():
            log("install favourites: %d items" % len(cmds))
            self.session.openWithCallback(self.after_change, ConsoleScreen,
                                          title=T("cat_fav"), cmdlist=cmds)
        _confirm(self, T("confirm_fav_all"), go)

    # ---- actions
    def key_green(self):
        it = self.current()
        if not it:
            return
        if "_cat" in it:
            self.session.openWithCallback(self.child_closed, O4TPackages, self.kind, it["_cat"])
            return
        cmd = self.install_cmd(it)
        if cmd:
            log("install: %s | %s" % (it["name"], cmd))
            self.session.openWithCallback(self.after_change, ConsoleScreen, title=it["name"],
                                          cmdlist=[cmd])

    def install_cmd(self, it):
        return catalog.install_cmd(it)

    def key_yellow(self):
        it = self.current()
        if not it or "_cat" in it:
            return
        if it.get("remove"):
            cmd = it["remove"]
        elif it.get("method") == "feed" and valid_pkg(it.get("pkg", "")):
            cmd = "opkg remove %s" % shquote(it["pkg"])
        else:
            return

        def go():
            log("remove: %s | %s" % (it["name"], cmd))
            self.session.openWithCallback(self.after_change, ConsoleScreen, title=it["name"],
                                          cmdlist=[cmd])
        _confirm(self, "%s\n\n%s" % (T("confirm_remove"), it["name"]), go)

    def key_blue(self):
        if self.cat == self.FEED:
            self.session.openWithCallback(lambda *a: self.refresh_view(), ConsoleScreen,
                                          title="opkg update", cmdlist=["opkg update"])
            return

        def done(ok):
            self.session.open(MessageBox, T("synced") if ok else T("sync_failed"),
                              MessageBox.TYPE_INFO if ok else MessageBox.TYPE_WARNING, timeout=4)
            self.refresh_view()
        catalog.refresh(self.console, done)

    def key_menu(self):
        self.session.openWithCallback(self.got_filter, VirtualKeyBoard,
                                      title=T("search"), text=self.filter)

    def got_filter(self, text=None):
        if text is None:
            return
        text = text.strip()
        if self.root and text:
            self.session.openWithCallback(self.child_closed, O4TPackages, self.kind, None, text)
        elif not self.root:
            self.filter = text
            self.refresh_view()

    def child_closed(self, *args):
        self.favs = load_favs()
        self.refresh_view(True)

    def after_change(self, *args):
        self.reload()
        _ask_restart(self)


# =====================================================================
# Updates
# =====================================================================
@guarded
class O4TUpdates(O4TListBase):
    MENU_TITLE = "m_updates"

    def __init__(self, session):
        self.only_plugins = True
        self.all_items = []
        O4TListBase.__init__(self, session)
        self["key_green"].setText(T("k_upgrade"))
        self["key_yellow"].setText(T("only_plugins"))
        self["key_blue"].setText(T("k_upgrade_all"))

    def reload(self):
        self.set_items([])
        self.set_status(T("loading"))
        self.run("opkg update >/dev/null 2>&1; opkg list-upgradable 2>/dev/null", self.loaded)

    def loaded(self, data, retval):
        items = []
        for line in data.splitlines():
            p = line.split(" - ")
            if len(p) >= 3 and valid_pkg(p[0].strip()):
                items.append({"pkg": p[0].strip(), "old": p[1].strip(), "new": p[2].strip(),
                              "name": pretty_name(p[0].strip())})
        self.all_items = items
        self.apply()

    def apply(self):
        items = [i for i in self.all_items
                 if not self.only_plugins or i["pkg"].startswith("enigma2-plugin-")]
        self.set_items(items, T("up_to_date"))

    def label_for(self, item):
        return item["name"]

    def detail_for(self, item):
        return "\n".join([item["name"], "", "%s: %s" % (T("package"), item["pkg"]),
                          "%s: %s" % (T("version"), item["old"]),
                          "%s: %s" % (T("new_version"), item["new"])])

    def key_yellow(self):
        self.only_plugins = not self.only_plugins
        self["key_yellow"].setText(T("only_plugins") if self.only_plugins else T("all_pkgs"))
        self.apply()

    def key_green(self):
        item = self.current()
        if item:
            self.session.openWithCallback(self.after, ConsoleScreen, title=item["name"],
                                          cmdlist=["opkg upgrade %s" % shquote(item["pkg"])])

    def key_blue(self):
        _confirm(self, T("confirm_upgrade_all"), lambda: self.session.openWithCallback(
            self.after, ConsoleScreen, title="opkg upgrade", cmdlist=["opkg upgrade"]))

    def after(self, *args):
        self.reload()
        _ask_restart(self)


# =====================================================================
# Installed packages
# =====================================================================
@guarded
class O4TInstalled(O4TListBase):
    MENU_TITLE = "m_installed"

    def __init__(self, session):
        self.fmode = 0  # 0 all, 1 plugins, 2 skins
        self.filter = ""
        self.all_items = []
        O4TListBase.__init__(self, session)
        self["key_green"].setText(T("k_remove"))
        self["key_yellow"].setText(T("f_all"))
        self["key_blue"].setText(T("k_refresh"))

    def reload(self):
        self.set_items([])
        self.set_status(T("loading"))
        self.run(OPKG_INSTALLED, self.loaded)

    def loaded(self, data, retval):
        items = parse_opkg_list(data)
        for p in items:
            p["name"] = pretty_name(p["pkg"])
        items.sort(key=lambda i: i["name"].lower())
        self.all_items = items
        self.apply()

    def apply(self):
        f = self.filter.lower()
        out = []
        for i in self.all_items:
            if self.fmode == 1 and "-skins-" in i["pkg"]:
                continue
            if self.fmode == 2 and "-skins-" not in i["pkg"]:
                continue
            if f and f not in i["name"].lower() and f not in i["pkg"].lower():
                continue
            out.append(i)
        self.set_items(out)

    def detail_for(self, item):
        return "\n".join([item["name"], "", "%s: %s" % (T("version"), item["version"]),
                          "%s: %s" % (T("package"), item["pkg"])] +
                         (["", item["desc"]] if item.get("desc") else []))

    def key_yellow(self):
        self.fmode = (self.fmode + 1) % 3
        self["key_yellow"].setText(T(("f_all", "f_plugins", "f_skins")[self.fmode]))
        self.apply()

    def key_blue(self):
        self.reload()

    def key_menu(self):
        self.session.openWithCallback(self.got_filter, VirtualKeyBoard,
                                      title=T("search"), text=self.filter)

    def got_filter(self, text=None):
        if text is not None:
            self.filter = text
            self.apply()

    def key_green(self):
        item = self.current()
        if item:
            _confirm(self, "%s\n\n%s" % (T("confirm_remove"), item["name"]),
                     lambda: self.session.openWithCallback(
                         self.after, ConsoleScreen, title=item["name"],
                         cmdlist=["opkg remove %s" % shquote(item["pkg"])]))

    def after(self, *args):
        self.reload()
        _ask_restart(self)


# =====================================================================
# Tools
# =====================================================================
@guarded
class O4TTools(O4TListBase):
    MENU_TITLE = "m_tools"

    def __init__(self, session):
        O4TListBase.__init__(self, session)
        self["key_green"].setText(T("k_run"))

    def reload(self):
        self.set_items([
            {"id": "restart_gui", "name": T("t_restart_gui"), "desc": T("d_restart_gui")},
            {"id": "reboot", "name": T("t_reboot"), "desc": T("d_reboot")},
            {"id": "standby", "name": T("t_standby"), "desc": T("d_standby")},
            {"id": "ram", "name": T("t_ram"), "desc": T("d_ram")},
            {"id": "tmp", "name": T("t_tmp"), "desc": T("d_tmp")},
            {"id": "feed", "name": T("t_feed"), "desc": T("d_feed")},
            {"id": "df", "name": T("t_df"), "desc": T("d_df")},
            {"id": "theme", "name": "%s: %s" % (T("t_theme"), T("th_" + theme())),
             "desc": T("d_theme")},
            {"id": "lang", "name": "%s: %s" % (T("t_lang"), T("v_" + get_setting("lang", "auto"))),
             "desc": T("d_lang")},
            {"id": "web", "name": T("t_web"), "desc": T("d_web")},
            {"id": "diag", "name": T("t_diag"), "desc": T("d_diag")},
        ], keep=True)

    def detail_for(self, item):
        return "%s\n\n%s" % (item["name"], item["desc"])

    def key_green(self):
        item = self.current()
        if not item:
            return
        k = item["id"]
        if k in ("restart_gui", "reboot", "standby"):
            mode = {"restart_gui": 3, "reboot": 2, "standby": 1}[k]
            _confirm(self, "%s\n\n%s" % (T("confirm"), item["name"]),
                     lambda: self.session.open(TryQuitMainloop, mode))
        elif k == "ram":
            self.run("sync; echo 3 > /proc/sys/vm/drop_caches", self.finished)
        elif k == "tmp":
            self.run("rm -f /tmp/*.ipk /tmp/*.tar.gz /tmp/o4t_* 2>/dev/null", self.finished)
        elif k == "feed":
            self.session.open(ConsoleScreen, title="opkg update", cmdlist=["opkg update"])
        elif k == "df":
            self.session.open(ConsoleScreen, title=item["name"], cmdlist=["df -h"])
        elif k == "theme":
            cycle_setting("theme", THEMES, "cyan")
            self.reload()
            self.session.open(MessageBox, T("reopen"), MessageBox.TYPE_INFO, timeout=3)
        elif k == "lang":
            cycle_setting("lang", LANGS, "auto")
            self.reload()
            self.session.open(MessageBox, T("reopen"), MessageBox.TYPE_INFO, timeout=3)
        elif k == "web":
            self.session.open(O4TWeb)
        elif k == "diag":
            self.session.open(O4TDiag)

    def finished(self, data, retval):
        self.session.open(MessageBox, T("done"), MessageBox.TYPE_INFO, timeout=3)


# =====================================================================
# Text screens
# =====================================================================
@guarded
class O4TTextBase(Screen):
    MENU_TITLE = "m_info"

    def __init__(self, session):
        self.skin = skin_text(self.__class__.__name__)
        Screen.__init__(self, session)
        self.console = Console()
        _watch_close(self)
        self["title"] = Label(T(self.MENU_TITLE))
        self["slogan"] = Label(SLOGAN)
        self["ver"] = Label("v" + VERSION)
        self["detail"] = ScrollLabel("")
        for c in ("red", "green", "yellow", "blue"):
            self["key_" + c] = Label("")
        self["key_red"].setText(T("k_back"))
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {"ok": self.close, "cancel": self.close, "red": self.close,
             "green": self.key_green, "yellow": self.key_yellow, "blue": self.key_blue,
             "up": self["detail"].pageUp, "down": self["detail"].pageDown,
             "left": self["detail"].pageUp, "right": self["detail"].pageDown}, -1)
        self.onLayoutFinish.append(self.start)

    def start(self):
        pass

    def key_green(self):
        pass

    def key_yellow(self):
        pass

    def key_blue(self):
        pass


@guarded
class O4TInfo(O4TTextBase):
    MENU_TITLE = "m_info"

    def start(self):
        self["detail"].setText(T("loading"))
        cmd = ("echo '## IP'; ip -o -4 addr show 2>/dev/null | awk '{print $2\": \"$4}'; "
               "echo; echo '## Storage'; df -h / /tmp /media/hdd /media/usb 2>/dev/null")
        _run(self.console, cmd, self.show_info)

    def show_info(self, data, retval):
        mem = {}
        for line in read_file("/proc/meminfo").splitlines():
            p = line.replace(":", " ").split()
            if len(p) >= 2:
                mem[p[0]] = p[1]
        try:
            ram = "%d MB total / %d MB free" % (int(mem["MemTotal"]) // 1024,
                                                int(mem.get("MemAvailable", mem["MemFree"])) // 1024)
        except Exception:
            ram = "-"
        model = read_file("/proc/stb/info/model").strip() or \
            read_file("/proc/stb/info/boxtype").strip() or "-"
        image = [l for l in read_file("/etc/image-version").splitlines() if l.strip()][:8]
        try:
            import platform
            kernel = platform.release()
        except Exception:
            kernel = "-"
        lines = ["## Receiver", "Model: " + model, "RAM: " + ram, "Kernel: " + kernel,
                 "Python: " + sys.version.split()[0], "Panel: v" + VERSION, "",
                 "## Image"] + image + ["", data.strip()]
        self["detail"].setText("\n".join(lines))


@guarded
class O4TWeb(O4TTextBase):
    """Web control settings: address, password, enable/disable, web shell."""
    MENU_TITLE = "t_web"

    def start(self):
        self["key_green"].setText(T("w_auth"))
        self["key_yellow"].setText(T("w_shell"))
        self["key_blue"].setText(T("w_toggle"))
        self.render_info()

    def render_info(self, ip="-"):
        from . import webserver
        port = get_setting("web_port", 8080)
        on = get_setting("web_enabled", True)
        shell = get_setting("web_shell", False)
        ips = []
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("192.0.2.1", 9))
            ips.append(s.getsockname()[0])
            s.close()
        except Exception:
            pass
        url = "http://%s:%s" % (ips[0] if ips else "<receiver-ip>", port)
        auth = get_setting("web_auth", False)
        lines = ["%s: %s" % (T("w_state"), T("w_on") if on and webserver.is_running() else T("w_off")),
                 "URL: " + url, "%s: %s" % (T("w_auth"), T("w_on") if auth else T("w_off"))]
        if auth:
            lines += ["User: admin", "Password: " + webserver.password()]
        lines += ["", "%s: %s" % (T("w_shell"), T("w_on") if shell else T("w_off")), "", T("w_help")]
        self["detail"].setText("\n".join(lines))

    def key_green(self):
        from . import webserver
        from .utils import set_setting
        set_setting("web_auth", not get_setting("web_auth", False))
        if get_setting("web_auth", False):
            webserver.password()
        self.render_info()

    def key_yellow(self):
        from .utils import set_setting
        set_setting("web_shell", not get_setting("web_shell", False))
        self.render_info()

    def key_blue(self):
        from . import webserver
        from .utils import set_setting
        on = not get_setting("web_enabled", True)
        set_setting("web_enabled", on)
        if on:
            webserver.start()
        else:
            webserver.stop()
        self.render_info()


@guarded
class O4TDiag(O4TTextBase):
    """Support report: everything needed to debug a problem on a real receiver."""
    MENU_TITLE = "t_diag"

    def start(self):
        self["detail"].setText(T("loading"))
        cmd = ("df -h / /tmp 2>/dev/null; echo '@@CRASH@@'; "
               "ls -t /home/root/logs/enigma2_crash_*.log /media/hdd/enigma2_crash_*.log 2>/dev/null | head -n 3")
        _run(self.console, cmd, self.build)

    def build(self, data, retval):
        m = metrics()
        src, updated, total = catalog.info()
        disk, _s, crash = data.partition("@@CRASH@@")
        counts = []
        for kind in ("plugin", "skin"):
            allv = catalog.items(kind)
            counts.append("%s: %d (%d compatible)" % (kind, len(allv),
                                                      len([i for i in allv if compatible(i)])))
        image = [l for l in read_file("/etc/image-version").splitlines() if l.strip()][:6]
        log_tail = read_file(LOG_FILE).splitlines()[-25:]
        lines = ["## Panel", "Version: v" + VERSION, "Python: %s (%s)" % (sys.version.split()[0],
                                                                         "py3" if PY3 else "py2"),
                 "Screen: %dx%d  assets: %s" % (m.W, m.H, m.assets),
                 "Theme: %s   Language: %s" % (theme(), get_setting("lang", "auto")),
                 "Favourites: %d" % len(load_favs()),
                 "", "## Catalog", "Source: %s  updated: %s  items: %d" % (src, updated, total)] + counts + \
                ["Detected image group: %s" % (detect_image_group() or "-"), "", "## Image"] + image + \
                ["", "## Disk", disk.strip(), "", "## Crash logs"] + (crash.split() or ["-"]) + \
                ["", "## Panel log (last lines)"] + (log_tail or ["-"]) + \
                ["", "Saved to /tmp/o4t_report.txt"]
        text = "\n".join(lines)
        self["detail"].setText(text)
        try:
            with open("/tmp/o4t_report.txt", "w") as fh:
                fh.write(text if not PY3 else text)
        except Exception:
            pass


@guarded
class O4TAbout(O4TTextBase):
    MENU_TITLE = "m_about"

    def start(self):
        self["detail"].setText(T("about_text") + "\n\n" + SLOGAN + "\n" + HOME_URL +
                               "\nv" + VERSION)


@guarded
class O4TSelfUpdate(O4TTextBase):
    MENU_TITLE = "m_selfupdate"

    def __init__(self, session):
        O4TTextBase.__init__(self, session)
        self["key_green"].setText(T("k_update"))

    def start(self):
        self["detail"].setText(T("su_checking"))
        cmd = "wget -q -T 10 -t 1 --no-check-certificate -O %s %s" % (TMP_VERSION, shquote(VERSION_URL))
        _run(self.console, cmd, self.got_version)

    def got_version(self, data, retval):
        latest = read_file(TMP_VERSION).strip().splitlines()
        latest = latest[0].strip() if latest else ""
        if retval != 0 or not latest:
            self["detail"].setText("%s: v%s\n\n%s" % (T("su_installed"), VERSION, T("su_unreachable")))
            return
        newer = version_tuple(latest) > version_tuple(VERSION)
        self["detail"].setText("%s: v%s\n%s: v%s\n\n%s" % (
            T("su_installed"), VERSION, T("su_latest"), latest,
            T("su_newer") if newer else T("su_same")))

    def key_green(self):
        cmd = "wget -q --no-check-certificate -O - %s | O4T_NO_RESTART=1 /bin/sh" % shquote(INSTALL_URL)
        self.session.openWithCallback(self.after, ConsoleScreen, title="Online4Tech Panel",
                                      cmdlist=[cmd])

    def after(self, *args):
        _ask_restart(self)
