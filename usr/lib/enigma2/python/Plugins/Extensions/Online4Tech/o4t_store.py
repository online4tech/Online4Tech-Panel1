# -*- coding: utf-8 -*-
import json
import os
import re
import ssl
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request

from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label

DB_URL = "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/o4t_database.json"
CACHE_DB = "/tmp/o4t_database.json"

def clean_text(txt):
    if not txt:
        return ""
    txt = re.sub(r'\([^)]*[^\x00-\x7F]+[^)]*\)', '', txt)
    txt = re.sub(r'[^\x00-\x7F]+', '', txt)
    return " ".join(txt.split()).strip()

class Online4TechStoreScreen(Screen):
    skin = """
    <screen name="Online4TechStoreScreen" position="center,center" size="1100,650" title="Online4Tech Store - All-in-One Manager">
        <widget name="header" position="20,15" size="1060,45" font="Regular;28" halign="center" valign="center" foregroundColor="#00d2ff" />
        <widget name="list" position="30,75" size="1040,490" itemHeight="38" font="Regular;24" scrollbarMode="showOnDemand" />
        <widget name="key_red" position="30,585" size="240,45" font="Regular;22" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" />
        <widget name="key_green" position="295,585" size="240,45" font="Regular;22" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" />
        <widget name="key_yellow" position="560,585" size="240,45" font="Regular;22" halign="center" valign="center" backgroundColor="#a08500" foregroundColor="#ffffff" />
        <widget name="key_blue" position="825,585" size="240,45" font="Regular;22" halign="center" valign="center" backgroundColor="#18188b" foregroundColor="#ffffff" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.db_data = {}
        self.history = []
        self.current_items = []
        self.mode = "main"

        self["header"] = Label("Online4Tech Store - Loading Database...")
        self["list"] = MenuList([])
        self["key_red"] = Label("Back / Exit")
        self["key_green"] = Label("Install / Open")
        self["key_yellow"] = Label("Uninstall")
        self["key_blue"] = Label("Refresh Server")

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {
            "ok": self.ok_pressed,
            "cancel": self.back_pressed,
            "red": self.back_pressed,
            "green": self.ok_pressed,
            "yellow": self.remove_pressed,
            "blue": self.refresh_db,
        }, -1)

        self.onLayoutFinish.append(self.load_database)

    def load_database(self, force=False):
        try:
            if force or not os.path.exists(CACHE_DB) or os.path.getsize(CACHE_DB) == 0:
                ctx = ssl._create_unverified_context()
                req = Request(DB_URL, headers={"User-Agent": "Online4Tech-Enigma2"})
                resp = urlopen(req, timeout=15, context=ctx)
                raw = resp.read().decode("utf-8")
                with open(CACHE_DB, "w", encoding="utf-8") as f:
                    f.write(raw)
            with open(CACHE_DB, "r", encoding="utf-8") as f:
                self.db_data = json.load(f)
            self.show_main_sections()
        except Exception as e:
            self["header"].setText("Error: %s" % str(e)[:50])

    def refresh_db(self):
        self["header"].setText("Refreshing Online4Tech Store...")
        self.load_database(force=True)

    def show_main_sections(self):
        self.mode = "main"
        self.history = []
        sections = self.db_data.get("main", [])
        self.current_items = sections
        menu_entries = []
        for idx, sec in enumerate(sections, 1):
            title = clean_text(sec.get("title", sec.get("section", "")))
            menu_entries.append("[%02d]  %s" % (idx, title))
        self["header"].setText("Online4Tech Store - Main Categories (%d)" % len(sections))
        self["list"].setList(menu_entries)

    def show_section(self, section_key, title):
        items = self.db_data.get(section_key, [])
        if items and isinstance(items[0], dict) and "section" in items[0]:
            self.mode = "sub"
            self.current_items = items
            menu_entries = []
            for idx, sub in enumerate(items, 1):
                sub_t = clean_text(sub.get("title", sub.get("section", "")))
                menu_entries.append("[%02d]  %s" % (idx, sub_t))
            self["header"].setText("Online4Tech - %s" % title)
            self["list"].setList(menu_entries)
        else:
            self.mode = "items"
            self.current_items = items
            menu_entries = []
            for idx, item in enumerate(items, 1):
                name = clean_text(item.get("name", "Unknown"))
                mark = "[*] " if item.get("path") and os.path.exists(item.get("path")) else ""
                menu_entries.append("[%03d]  %s%s" % (idx, mark, name))
            self["header"].setText("%s (%d Items)" % (title, len(items)))
            self["list"].setList(menu_entries)

    def ok_pressed(self):
        idx = self["list"].getSelectedIndex()
        if idx is None or idx < 0 or idx >= len(self.current_items):
            return
        selected = self.current_items[idx]

        if self.mode in ("main", "sub"):
            sec_key = selected.get("section")
            title = clean_text(selected.get("title", sec_key))
            self.history.append((self.mode, self.current_items, self["header"].getText()))
            self.show_section(sec_key, title)
        elif self.mode == "items":
            name = clean_text(selected.get("name", "Package"))
            cmd = selected.get("cmd", "")
            if cmd:
                self.session.open(Console, title="Online4Tech Installing: %s" % name, cmdlist=[cmd], closeOnSuccess=False)

    def remove_pressed(self):
        if self.mode != "items":
            return
        idx = self["list"].getSelectedIndex()
        if idx is None or idx < 0 or idx >= len(self.current_items):
            return
        selected = self.current_items[idx]
        rem_cmd = selected.get("remove_cmd", "")
        name = clean_text(selected.get("name", "Package"))
        if rem_cmd:
            self.session.open(Console, title="Online4Tech Removing: %s" % name, cmdlist=[rem_cmd], closeOnSuccess=False)
        else:
            self.session.open(MessageBox, "No remove command for this item.", MessageBox.TYPE_INFO, timeout=3)

    def back_pressed(self):
        if self.history:
            prev_mode, prev_items, prev_header = self.history.pop()
            self.mode = prev_mode
            self.current_items = prev_items
            self["header"].setText(prev_header)
            entries = []
            for idx, it in enumerate(prev_items, 1):
                t = clean_text(it.get("title", it.get("name", "")))
                entries.append("[%02d]  %s" % (idx, t))
            self["list"].setList(entries)
        else:
            self.close()