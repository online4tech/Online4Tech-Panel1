# -*- coding: utf-8 -*-
"""All UI screens of Online4Tech Panel (Python 2 / 3 compatible)."""
from __future__ import absolute_import, print_function
import os
import sys

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
from .skin import MAIN_POS, metrics, skin_list, skin_main, skin_text
from .utils import (parse_opkg_list, pretty_name, read_file, shquote, txt,
                    valid_pkg, valid_url, version_tuple)
from .version import (HOME_URL, INSTALL_URL, SLOGAN, TMP_VERSION, VERSION,
                      VERSION_URL)

OPKG_INSTALLED = "opkg list-installed 2>/dev/null | grep '^enigma2-plugin-'"
FEED_FILTER = "grep -Ev '^[^ ]+-(src|dbg|dev|po|meta) '"
FEED_PREFIX = {"plugin": "enigma2-plugin-extensions-", "skin": "enigma2-plugin-skins-"}


def _run(console, cmd, cb):
    def done(data, retval, extra=None):
        cb(txt(data), retval)
    console.ePopen(cmd, done)


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
class O4TMain(Screen):
    MENU = ["plugins", "skins", "updates", "installed", "tools", "info", "selfupdate", "about"]

    def __init__(self, session):
        self.skin = skin_main()
        Screen.__init__(self, session)
        self.console = Console()
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
class O4TListBase(Screen):
    TITLE = "m_plugins"

    def __init__(self, session):
        self.skin = skin_list(self.__class__.__name__)
        Screen.__init__(self, session)
        self.console = Console()
        self.items = []
        self["title"] = Label(T(self.TITLE))
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
            {"ok": self.key_green, "cancel": self.close, "red": self.close,
             "green": self.key_green, "yellow": self.key_yellow, "blue": self.key_blue,
             "menu": self.key_menu,
             "up": self["list"].up, "down": self["list"].down,
             "left": self["list"].pageUp, "right": self["list"].pageDown}, -1)
        self["list"].onSelectionChanged.append(self.sel_changed)
        self.onLayoutFinish.append(self.reload)

    # -- to override
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

    def set_items(self, items, empty_text=None):
        self.items = items
        self["list"].setList([self.label_for(i) for i in items])
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
class O4TPackages(O4TListBase):
    def __init__(self, session, kind):
        self.kind = kind
        self.TITLE = "m_plugins" if kind == "plugin" else "m_skins"
        self.mode = "feed"
        self.filter = ""
        self.all_items = []
        self.installed = {}
        O4TListBase.__init__(self, session)
        self["key_green"].setText(T("k_install"))
        self["key_yellow"].setText(T("k_featured"))
        self["key_blue"].setText(T("k_refresh"))

    def reload(self):
        self.set_items([])
        self.set_status(T("loading"))
        cmd = "%s; echo '@@FEED@@'; " % OPKG_INSTALLED
        if self.mode == "feed":
            cmd += "opkg list 2>/dev/null | grep '^%s' | %s" % (FEED_PREFIX[self.kind], FEED_FILTER)
        self.run(cmd, self.loaded)

    def loaded(self, data, retval):
        head, _sep, tail = data.partition("@@FEED@@")
        self.installed = dict((p["pkg"], p["version"]) for p in parse_opkg_list(head))
        items = []
        if self.mode == "feed":
            for p in parse_opkg_list(tail):
                p["name"] = pretty_name(p["pkg"])
                p["method"] = "feed"
                p["source"] = "src_feed"
                items.append(p)
            items.sort(key=lambda i: i["name"].lower())
        else:
            for p in catalog.items_for(self.kind):
                p["source"] = "src_picks"
                items.append(p)
        self.all_items = items
        self.apply_filter()
        if not items:
            self.set_status(T("empty_feed") if self.mode == "feed" else T("empty"))

    def apply_filter(self):
        f = self.filter.lower()
        items = [i for i in self.all_items
                 if not f or f in i["name"].lower() or f in i.get("pkg", "").lower()
                 or f in i.get("desc", "").lower()]
        self.set_items(items)

    def label_for(self, item):
        mark = "* " if item.get("pkg") in self.installed else "   "
        return mark + item["name"]

    def detail_for(self, item):
        pkg = item.get("pkg", "")
        state = T("installed_yes") if pkg in self.installed else T("installed_no")
        lines = [item["name"], "",
                 "%s: %s" % (T("status"), state),
                 "%s: %s" % (T("version"), item.get("version") or "-"),
                 "%s: %s" % (T("source"), T(item.get("source", "src_feed")))]
        if pkg:
            lines.append("%s: %s" % (T("package"), pkg))
        if item.get("desc"):
            lines += ["", item["desc"]]
        return "\n".join(lines)

    def key_yellow(self):
        self.mode = "picks" if self.mode == "feed" else "feed"
        self["key_yellow"].setText(T("k_featured") if self.mode == "feed" else T("k_feed"))
        self.reload()

    def key_blue(self):
        self.session.openWithCallback(lambda *a: self.reload(), ConsoleScreen,
                                      title="opkg update", cmdlist=["opkg update"])

    def key_menu(self):
        self.session.openWithCallback(self.got_filter, VirtualKeyBoard,
                                      title=T("search"), text=self.filter)

    def got_filter(self, text=None):
        if text is not None:
            self.filter = text
            self.apply_filter()

    def key_green(self):
        item = self.current()
        if not item:
            return
        method = item.get("method")
        if method == "feed" and valid_pkg(item.get("pkg", "")):
            cmds = ["opkg install %s" % shquote(item["pkg"])]
        elif method == "ipk" and valid_url(item.get("url", "")):
            tmp = "/tmp/o4t_pkg.ipk"
            cmds = ["wget -q --no-check-certificate -O %s %s && opkg install --force-reinstall "
                    "--force-overwrite %s; rm -f %s" % (tmp, shquote(item["url"]), tmp, tmp)]
        elif method == "tar" and valid_url(item.get("url", "")):
            tmp = "/tmp/o4t_pkg.tar.gz"
            cmds = ["wget -q --no-check-certificate -O %s %s && tar -xzf %s -C /; rm -f %s"
                    % (tmp, shquote(item["url"]), tmp, tmp)]
        else:
            return
        self.session.openWithCallback(self.after_install, ConsoleScreen,
                                      title=item["name"], cmdlist=cmds)

    def after_install(self, *args):
        self.reload()
        _ask_restart(self)


# =====================================================================
# Updates
# =====================================================================
class O4TUpdates(O4TListBase):
    TITLE = "m_updates"

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
class O4TInstalled(O4TListBase):
    TITLE = "m_installed"

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
class O4TTools(O4TListBase):
    TITLE = "m_tools"

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
        ])

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

    def finished(self, data, retval):
        self.session.open(MessageBox, T("done"), MessageBox.TYPE_INFO, timeout=3)


# =====================================================================
# Text screens
# =====================================================================
class O4TTextBase(Screen):
    TITLE = "m_info"

    def __init__(self, session):
        self.skin = skin_text(self.__class__.__name__)
        Screen.__init__(self, session)
        self.console = Console()
        self["title"] = Label(T(self.TITLE))
        self["slogan"] = Label(SLOGAN)
        self["ver"] = Label("v" + VERSION)
        self["detail"] = ScrollLabel("")
        for c in ("red", "green", "yellow", "blue"):
            self["key_" + c] = Label("")
        self["key_red"].setText(T("k_back"))
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {"ok": self.close, "cancel": self.close, "red": self.close,
             "green": self.key_green,
             "up": self["detail"].pageUp, "down": self["detail"].pageDown,
             "left": self["detail"].pageUp, "right": self["detail"].pageDown}, -1)
        self.onLayoutFinish.append(self.start)

    def start(self):
        pass

    def key_green(self):
        pass


class O4TInfo(O4TTextBase):
    TITLE = "m_info"

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


class O4TAbout(O4TTextBase):
    TITLE = "m_about"

    def start(self):
        self["detail"].setText(T("about_text") + "\n\n" + SLOGAN + "\n" + HOME_URL +
                               "\nv" + VERSION)


class O4TSelfUpdate(O4TTextBase):
    TITLE = "m_selfupdate"

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
        cmd = "wget -q --no-check-certificate -O - %s | sh" % shquote(INSTALL_URL)
        self.session.openWithCallback(self.after, ConsoleScreen, title="Online4Tech Panel",
                                      cmdlist=[cmd])

    def after(self, *args):
        _ask_restart(self)
