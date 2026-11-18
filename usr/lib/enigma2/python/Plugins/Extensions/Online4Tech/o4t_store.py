# -*- coding: utf-8 -*-
import os, json, urllib.request, ssl
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER

PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech"
DB_URL = "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/o4t_database.json"
CACHE_FILE = "/tmp/o4t_database.json"

class O4TModernList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont("Regular", 23))
        self.l.setFont(1, gFont("Regular", 19))
        self.l.setItemHeight(46)

def build_entry(idx_str, title, badge, item_data):
    res = [item_data]
    # خلفية البطاقة العادية والمحددة
    res.append((eListboxPythonMultiContent.TYPE_TEXT, 12, 4, 70, 38, 1, RT_HALIGN_LEFT | RT_VALIGN_CENTER, idx_str, 0x0000d2ff, 0x00ffffff))
    res.append((eListboxPythonMultiContent.TYPE_TEXT, 85, 4, 580, 38, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, title, 0x00f1f5f9, 0x00ffffff))
    res.append((eListboxPythonMultiContent.TYPE_TEXT, 670, 4, 110, 38, 1, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, badge, 0x0038bdf8, 0x00e0f2fe))
    return res

class Online4TechStoreScreen(Screen):
    skin = """
    <screen name="Online4TechStoreScreen" position="center,center" size="1260,760" title="Online4Tech Store" flags="wfNoBorder" backgroundColor="#070d19">
        <!-- الإطار الخارجي النيون -->
        <eLabel position="0,0" size="1260,3" backgroundColor="#00d2ff" />
        <eLabel position="0,757" size="1260,3" backgroundColor="#00d2ff" />
        <eLabel position="0,0" size="3,760" backgroundColor="#00d2ff" />
        <eLabel position="1257,0" size="3,760" backgroundColor="#00d2ff" />

        <!-- البانر العلوي -->
        <widget name="logo" position="20,16" size="1220,95" alphatest="blend" />

        <!-- شريط المسار والحالة -->
        <eLabel position="20,122" size="1220,42" backgroundColor="#0d192e" />
        <widget name="header_path" position="35,122" size="850,42" font="Regular;22" foregroundColor="#00e1ff" backgroundColor="#0d192e" transparent="1" valign="center" />
        <widget name="counter_lbl" position="900,122" size="325,42" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0d192e" transparent="1" halign="right" valign="center" />

        <!-- القائمة الرئيسية (يمين/وسط) -->
        <eLabel position="20,175" size="810,500" backgroundColor="#0a1222" />
        <widget name="list" position="28,183" size="794,484" backgroundColor="#0a1222" backgroundColorSelected="#005f99" foregroundColorSelected="#ffffff" scrollbarMode="showOnDemand" enableWrapAround="1" />

        <!-- لوحة التفاصيل ومعلومات النظام (الجانب الأيمن) -->
        <eLabel position="845,175" size="395,500" backgroundColor="#0d172a" />
        <eLabel position="845,175" size="395,3" backgroundColor="#0077b6" />
        <eLabel text="ITEM DETAILS &amp; INFO" position="860,188" size="365,32" font="Regular;20" foregroundColor="#00d2ff" backgroundColor="#0d172a" transparent="1" />
        <eLabel position="860,224" size="365,1" backgroundColor="#1e293b" />
        <widget name="detail_title" position="860,235" size="365,75" font="Regular;22" foregroundColor="#ffffff" backgroundColor="#0d172a" transparent="1" />
        <widget name="detail_desc" position="860,318" size="365,175" font="Regular;19" foregroundColor="#cbd5e1" backgroundColor="#0d172a" transparent="1" />

        <eLabel position="860,505" size="365,1" backgroundColor="#1e293b" />
        <eLabel text="RECEIVER STATUS" position="860,515" size="365,30" font="Regular;19" foregroundColor="#38bdf8" backgroundColor="#0d172a" transparent="1" />
        <widget name="sys_info" position="860,550" size="365,110" font="Regular;18" foregroundColor="#94a3b8" backgroundColor="#0d172a" transparent="1" />

        <!-- شريط أزرار الريموت السفلي -->
        <eLabel position="20,690" size="1220,52" backgroundColor="#0d192e" />

        <eLabel position="35,700" size="275,34" backgroundColor="#991b1b" />
        <eLabel position="35,700" size="6,34" backgroundColor="#ef4444" />
        <widget name="key_red" position="48,700" size="255,34" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#991b1b" transparent="1" halign="center" valign="center" />

        <eLabel position="335,700" size="275,34" backgroundColor="#065f46" />
        <eLabel position="335,700" size="6,34" backgroundColor="#10b981" />
        <widget name="key_green" position="348,700" size="255,34" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#065f46" transparent="1" halign="center" valign="center" />

        <eLabel position="635,700" size="275,34" backgroundColor="#92400e" />
        <eLabel position="635,700" size="6,34" backgroundColor="#f59e0b" />
        <widget name="key_yellow" position="648,700" size="255,34" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#92400e" transparent="1" halign="center" valign="center" />

        <eLabel position="935,700" size="290,34" backgroundColor="#075985" />
        <eLabel position="935,700" size="6,34" backgroundColor="#00d2ff" />
        <widget name="key_blue" position="948,700" size="270,34" font="Regular;20" foregroundColor="#ffffff" backgroundColor="#075985" transparent="1" halign="center" valign="center" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self["logo"] = Pixmap()
        self["header_path"] = Label("Loading Online4Tech Store...")
        self["counter_lbl"] = Label("")
        self["detail_title"] = Label("Online4Tech Store v7.5")
        self["detail_desc"] = Label("Select any category or plugin from the list to view details and install directly.")
        self["sys_info"] = Label(self.get_sys_stats())
        self["key_red"] = Label("Exit")
        self["key_green"] = Label("Open / Install")
        self["key_yellow"] = Label("Uninstall")
        self["key_blue"] = Label("Refresh Server")
        self["list"] = O4TModernList([])

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "ok": self.ok_pressed,
            "cancel": self.back_pressed,
            "red": self.back_pressed,
            "green": self.ok_pressed,
            "yellow": self.uninstall_pressed,
            "blue": self.refresh_server,
            "up": self.move_up,
            "down": self.move_down,
        }, -1)

        self.db = {}
        self.mode = "main"
        self.current_section = ""
        self.onLayoutFinish.append(self.startup)

    def get_sys_stats(self):
        try:
            st = os.statvfs("/")
            free_mb = (st.f_bavail * st.f_frsize) // (1024 * 1024)
            total_mb = (st.f_blocks * st.f_frsize) // (1024 * 1024)
            model = "Enigma2 Receiver"
            if os.path.exists("/proc/stb/info/vumodel"):
                model = "Vu+ " + open("/proc/stb/info/vumodel").read().strip().upper()
            return "Box: %s\nFlash Free: %d MB / %d MB\nServer: Online4Tech GitHub Cloud" % (model, free_mb, total_mb)
        except Exception:
            return "Server: Online4Tech Cloud\nStatus: Connected"

    def startup(self):
        logo_file = os.path.join(PLUGIN_PATH, "logo.png")
        if os.path.exists(logo_file) and self["logo"].instance:
            self["logo"].instance.setPixmapFromFile(logo_file)
        self.load_database(force=False)

    def load_database(self, force=False):
        try:
            if force or not os.path.exists(CACHE_FILE):
                ctx = ssl._create_unverified_context()
                req = urllib.request.urlopen(DB_URL, context=ctx, timeout=15)
                raw = req.read().decode("utf-8")
                with open(CACHE_FILE, "w") as f:
                    f.write(raw)
            else:
                with open(CACHE_FILE, "r") as f:
                    raw = f.read()
            self.db = json.loads(raw)
            self.show_main()
        except Exception as e:
            self["header_path"].setText("Connection Error: " + str(e))

    def show_main(self):
        self.mode = "main"
        self["key_red"].setText("Exit")
        self["key_green"].setText("Open Category")
        entries = []
        cats = self.db.get("main", [])
        for i, item in enumerate(cats, 1):
            sec = item.get("section", "")
            cnt = len(self.db.get(sec, []))
            entries.append(build_entry("[%02d]" % i, item.get("name", sec), "%d items" % cnt, item))
        self["list"].setList(entries)
        self["header_path"].setText("HOME  >  Main Categories")
        self["counter_lbl"].setText("Total Categories: %d" % len(entries))
        self.update_details()

    def show_section(self, sec_key, sec_title):
        self.mode = "section"
        self.current_section = sec_key
        self["key_red"].setText("Back")
        self["key_green"].setText("Install Now")
        entries = []
        items = self.db.get(sec_key, [])
        for i, item in enumerate(items, 1):
            path = item.get("path", "")
            status = "INSTALLED" if (path and os.path.exists(path)) else "ONLINE"
            entries.append(build_entry("[%03d]" % i, item.get("name", "Package"), status, item))
        self["list"].setList(entries)
        self["header_path"].setText("HOME  >  %s" % sec_title)
        self["counter_lbl"].setText("Packages: %d" % len(entries))
        self.update_details()

    def update_details(self):
        cur = self["list"].getCurrent()
        if not cur:
            return
        data = cur[0]
        name = data.get("name", "")
        self["detail_title"].setText(name)
        if self.mode == "main":
            sec = data.get("section", "")
            cnt = len(self.db.get(sec, []))
            self["detail_desc"].setText("Category: %s\nAvailable Packages: %d\n\nPress OK or GREEN to browse packages inside this section." % (name, cnt))
        else:
            path = data.get("path", "")
            inst = "Yes (Found on Receiver)" if (path and os.path.exists(path)) else "Not Installed"
            self["detail_desc"].setText("Package: %s\nStatus: %s\nSource: Online4Tech Official Repo\n\nPress OK/GREEN to install, or YELLOW to remove." % (name, inst))

    def move_up(self):
        self["list"].up()
        self.update_details()

    def move_down(self):
        self["list"].down()
        self.update_details()

    def ok_pressed(self):
        cur = self["list"].getCurrent()
        if not cur:
            return
        data = cur[0]
        if self.mode == "main":
            self.show_section(data.get("section", ""), data.get("name", ""))
        else:
            cmd = data.get("cmd", "")
            if cmd:
                self.session.open(Console, title="Installing: " + data.get("name", ""), cmdlist=[cmd])

    def uninstall_pressed(self):
        if self.mode != "section":
            return
        cur = self["list"].getCurrent()
        if not cur:
            return
        data = cur[0]
        rcmd = data.get("remove_cmd", "")
        if rcmd:
            self.session.open(Console, title="Removing: " + data.get("name", ""), cmdlist=[rcmd])
        else:
            self.session.open(MessageBox, "No automatic uninstall command defined for this item.", MessageBox.TYPE_INFO, timeout=3)

    def refresh_server(self):
        self["header_path"].setText("Syncing with Online4Tech Server...")
        self.load_database(force=True)

    def back_pressed(self):
        if self.mode == "section":
            self.show_main()
        else:
            self.close()