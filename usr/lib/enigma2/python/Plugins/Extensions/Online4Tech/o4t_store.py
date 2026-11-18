# -*- coding: utf-8 -*-
import os, sys, json, time, socket, urllib.request, ssl
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eTimer
from Tools.LoadPixmap import LoadPixmap

PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/Online4Tech"
ICONS_PATH = os.path.join(PLUGIN_PATH, "icons")
DB_URL = "https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/main/o4t_database.json"
CACHE_FILE = "/tmp/o4t_database.json"

def guess_icon(sec_name):
    s = sec_name.lower()
    if "plugin" in s or "novaler" in s: return "plugins"
    if "channel" in s or "sat" in s: return "channels"
    if "cam" in s or "emu" in s or "oscam" in s: return "cams"
    if "feed" in s or "update" in s: return "feeds"
    if "picon" in s: return "picons"
    if "skin" in s: return "skins"
    if "panel" in s: return "panels"
    if "boot" in s or "spinner" in s or "image" in s: return "display"
    if "tool" in s or "system" in s or "setting" in s: return "tools"
    return "default"

class O4TCardList(MenuList):
    def __init__(self, items):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(76)
        self.l.setFont(0, gFont("Regular", 24))
        self.l.setFont(1, gFont("Regular", 19))

class O4TGridRows(MenuList):
    def __init__(self, items):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(255)
        self.l.setFont(0, gFont("Regular", 24))
        self.l.setFont(1, gFont("Regular", 19))

class Online4TechStoreScreen(Screen):
    skin = """
    <screen name="Online4TechStoreScreen" position="0,0" size="1920,1080" title="Online4Tech Panel" flags="wfNoBorder" backgroundColor="#0b0d12">
        <!-- الشريط العلوي -->
        <eLabel position="0,0" size="1920,115" backgroundColor="#0f1218" />
        <eLabel position="0,114" size="1920,2" backgroundColor="#1e222d" />

        <widget name="clock_lbl" position="55,15" size="260,48" font="Regular;40" foregroundColor="#ffffff" backgroundColor="#0f1218" transparent="1" halign="center" />
        <widget name="date_lbl" position="55,64" size="260,26" font="Regular;19" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />
        <eLabel text="NET: ONLINE" position="55,90" size="260,22" font="Regular;16" foregroundColor="#22c55e" backgroundColor="#0f1218" transparent="1" halign="center" />

        <eLabel position="460,28" size="960,56" backgroundColor="#161922" />
        <widget name="center_header" position="480,28" size="920,56" font="Regular;24" foregroundColor="#e2e8f0" backgroundColor="#161922" transparent="1" halign="center" valign="center" />

        <eLabel text="Online4TechPanel" position="1480,18" size="390,46" font="Regular;34" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="center" />
        <eLabel text="Online4Tech | v7.5 Gold" position="1480,68" size="390,28" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />

        <!-- العمود الأيسر: النظام -->
        <widget name="left_bg" position="40,145" size="380,820" backgroundColor="#11141c" />
        <widget name="left_title" position="55,165" size="350,38" font="Regular;24" foregroundColor="#f5d061" backgroundColor="#11141c" transparent="1" halign="center" />
        <widget name="left_line" position="65,212" size="330,1" backgroundColor="#262b38" />
        <widget name="left_info" position="60,230" size="340,710" font="Regular;21" foregroundColor="#cbd5e1" backgroundColor="#11141c" transparent="1" halign="center" />

        <!-- العمود الأوسط: البطاقات -->
        <widget name="page_info" position="460,128" size="320,32" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="left" />
        <widget name="section_heading" position="1080,124" size="340,38" font="Regular;28" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="right" />
        <widget name="list" position="460,170" size="960,795" backgroundColor="#0b0d12" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

        <!-- العمود الأيمن: الأقسام -->
        <widget name="right_bg" position="1460,145" size="420,820" backgroundColor="#11141c" />
        <widget name="right_header" position="1480,165" size="380,36" font="Regular;22" foregroundColor="#94a3b8" backgroundColor="#11141c" transparent="1" halign="center" />
        <widget name="right_line" position="1480,210" size="380,1" backgroundColor="#262b38" />
        <widget name="side_list" position="1475,225" size="390,720" font="Regular;23" itemHeight="54" foregroundColor="#cbd5e1" backgroundColor="#11141c" foregroundColorSelected="#f5d061" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

        <!-- وضع الشبكة 4x3 -->
        <widget name="grid_list" position="55,165" size="1810,780" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

        <!-- الشريط السفلي -->
        <eLabel position="0,990" size="1920,90" backgroundColor="#0f1218" />
        <eLabel position="0,990" size="1920,2" backgroundColor="#1e222d" />

        <eLabel position="1810,1022" size="24,24" backgroundColor="#ef4444" />
        <widget name="key_red" position="1610,1016" size="190,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

        <eLabel position="1520,1022" size="24,24" backgroundColor="#22c55e" />
        <widget name="key_green" position="1310,1016" size="200,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

        <eLabel position="1220,1022" size="24,24" backgroundColor="#eab308" />
        <widget name="key_yellow" position="940,1016" size="270,36" font="Regular;22" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="right" />

        <eLabel position="850,1022" size="24,24" backgroundColor="#3b82f6" />
        <widget name="key_blue" position="640,1016" size="200,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

        <widget name="mode_badge" position="80,1016" size="380,36" font="Regular;22" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="left" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self["clock_lbl"] = Label("")
        self["date_lbl"] = Label("")
        self["center_header"] = Label("متجر أونلاين تكنولوجي الشامل")
        self["left_bg"] = Label("")
        self["left_title"] = Label("النظام")
        self["left_line"] = Label("")
        self["left_info"] = Label("")
        self["page_info"] = Label("")
        self["section_heading"] = Label("الأقسام الرئيسية")
        self["right_bg"] = Label("")
        self["right_header"] = Label("الأقسام")
        self["right_line"] = Label("")

        self["key_red"] = Label("خروج")
        self["key_green"] = Label("تثبيت / فتح")
        self["key_yellow"] = Label("تبديل العرض (شبكة)")
        self["key_blue"] = Label("تحديث السيرفر")
        self["mode_badge"] = Label("عرض القائمة  |  أصفر للشبكة")

        self["list"] = O4TCardList([])
        self["side_list"] = MenuList([])
        self["grid_list"] = O4TGridRows([])

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "ok": self.ok_pressed,
            "cancel": self.back_pressed,
            "red": self.back_pressed,
            "green": self.ok_pressed,
            "yellow": self.toggle_view_mode,
            "blue": self.refresh_server,
            "up": self.move_up,
            "down": self.move_down,
            "left": self.move_left,
            "right": self.move_right,
        }, -1)

        self.db = {}
        self.mode = "main"
        self.view_style = "list"
        self.current_items = []
        self.grid_index = 0
        self.timer = eTimer()
        self.timer.callback.append(self.update_clock)
        self.onLayoutFinish.append(self.startup)

    def update_clock(self):
        self["clock_lbl"].setText(time.strftime("%H:%M"))
        self["date_lbl"].setText(time.strftime("%A %d %B"))

    def get_sys_info_text(self):
        lines = []
        try:
            model = "Vu+ Duo 4K"
            if os.path.exists("/proc/stb/info/vumodel"):
                model = "Vu+ " + open("/proc/stb/info/vumodel").read().strip().upper()
            lines.append("Box: " + model)
            if os.path.exists("/etc/issue"):
                img = open("/etc/issue").read().splitlines()[0].replace("\\n", "").replace("\\l", "").strip()
                lines.append("Image: " + img[:22])
            lines.append("Python: %d.%d.%d" % sys.version_info[:3])
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                lines.append("IP: " + ip)
            except Exception:
                lines.append("IP: Local")
            lines.append("Net: Online")
            st = os.statvfs("/")
            free_gb = (st.f_bavail * st.f_frsize) / (1024.0 ** 3)
            tot_gb = (st.f_blocks * st.f_frsize) / (1024.0 ** 3)
            lines.append("Flash: %.1fGB / %.1fGB" % (free_gb, tot_gb))
            if os.path.exists("/proc/meminfo"):
                mem = open("/proc/meminfo").read()
                tot_m = int([x for x in mem.splitlines() if "MemTotal" in x][0].split()[1]) // 1024
                avl_m = int([x for x in mem.splitlines() if "MemAvailable" in x][0].split()[1]) // 1024
                lines.append("Ram: %dMB / %dMB" % (tot_m - avl_m, tot_m))
        except Exception:
            pass
        return "\n\n".join(lines)

    def startup(self):
        self.update_clock()
        self.timer.start(10000)
        self.apply_view_visibility()
        self.load_database(force=False)

    def apply_view_visibility(self):
        is_grid = (self.view_style == "grid")
        for w in ["left_bg", "left_title", "left_line", "left_info", "page_info", "section_heading", "list", "right_bg", "right_header", "right_line", "side_list"]:
            if is_grid:
                self[w].hide()
            else:
                self[w].show()
        if is_grid:
            self["grid_list"].show()
            self["key_yellow"].setText("تبديل العرض (قائمة)")
            self["mode_badge"].setText("عرض الشبكة 4x3  |  أصفر للقائمة")
        else:
            self["grid_list"].hide()
            self["key_yellow"].setText("تبديل العرض (شبكة)")
            self["mode_badge"].setText("عرض القائمة  |  أصفر للشبكة")

    def toggle_view_mode(self):
        if self.view_style == "list":
            self.grid_index = self["list"].getSelectedIndex()
            self.view_style = "grid"
        else:
            self.view_style = "list"
        self.apply_view_visibility()
        self.render_current_items()

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
            self["center_header"].setText("Error: " + str(e))

    def get_icon_pix(self, icon_key):
        ic_file = os.path.join(ICONS_PATH, "ic_%s.png" % icon_key)
        if not os.path.exists(ic_file):
            ic_file = os.path.join(ICONS_PATH, "ic_default.png")
        return LoadPixmap(ic_file) if os.path.exists(ic_file) else None

    def make_list_card(self, title, subtitle, badge, icon_key, is_installed, data):
        ic_pix = self.get_icon_pix(icon_key)
        res = [data]
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 5, 4, 950, 68, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, "", 0x00161922, 0x00262012, 0x00161922, 0x00262012))
        if ic_pix:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 875, 6, 64, 64, ic_pix))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 440, 12, 415, 52, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, title, 0x00ffffff, 0x00f5d061))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 140, 12, 285, 52, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, subtitle, 0x00cbd5e1, 0x00ffffff))
        if is_installed:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 20, 18, 105, 40, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "مثبت", 0x00ff5555, 0x00ff8888))
        elif badge:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 20, 18, 105, 40, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, badge, 0x00f5d061, 0x00ffffff))
        return res

    def build_grid_rows(self):
        cols = 4
        col_x = [1365, 915, 465, 15]
        rows = []
        total = len(self.current_items)
        for r_start in range(0, total, cols):
            row_entries = [r_start]
            for c in range(cols):
                idx = r_start + c
                if idx >= total:
                    break
                entry = self.current_items[idx]
                x0 = col_x[c]
                is_selected = (idx == self.grid_index)
                bg_col = 0x00262012 if is_selected else 0x00161922
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0, 8, 430, 235, 0, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "", bg_col, bg_col, bg_col, bg_col))
                ic_pix = self.get_icon_pix(entry["icon"])
                if ic_pix:
                    row_entries.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x0 + 345, 22, 64, 64, ic_pix))
                t_col = 0x00f5d061 if is_selected else 0x00ffffff
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 24, 310, 60, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, entry["title"], t_col, t_col))
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 100, 390, 85, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, entry["subtitle"], 0x00cbd5e1, 0x00ffffff))
                if entry["installed"]:
                    row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 195, 110, 34, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, "مثبت", 0x00ff5555, 0x00ff5555))
            rows.append(row_entries)
        self["grid_list"].setList(rows)
        if rows:
            self["grid_list"].moveToIndex(self.grid_index // cols)

    def render_current_items(self):
        if self.view_style == "grid":
            self.build_grid_rows()
        else:
            cards = []
            for entry in self.current_items:
                cards.append(self.make_list_card(entry["title"], entry["subtitle"], entry["badge"], entry["icon"], entry["installed"], entry["data"]))
            self["list"].setList(cards)
            if cards and self.grid_index < len(cards):
                self["list"].moveToIndex(self.grid_index)

    def show_main(self):
        self.mode = "main"
        self.grid_index = 0
        self["key_red"].setText("خروج")
        self["section_heading"].setText("الأقسام الرئيسية")
        self["left_title"].setText("النظام")
        self["left_info"].setText(self.get_sys_info_text())

        cats = self.db.get("main", [])
        self.current_items = []
        side_items = []
        for item in cats:
            sec = item.get("section", "")
            raw_title = item.get("name", "") or item.get("title", "") or sec
            cnt = len(self.db.get(sec, []))
            ic_key = guess_icon(sec + " " + raw_title)
            self.current_items.append({
                "title": raw_title,
                "subtitle": "%d حزمة متاحة" % cnt,
                "badge": "(%d)" % cnt,
                "icon": ic_key,
                "installed": False,
                "data": item
            })
            side_items.append(("%s (%d)" % (raw_title, cnt), item))

        self["side_list"].setList(side_items)
        self["page_info"].setText("%d قسم" % len(self.current_items))
        self.render_current_items()

    def show_section(self, sec_key, sec_name):
        self.mode = "section"
        self.grid_index = 0
        self["key_red"].setText("رجوع")
        self["section_heading"].setText(sec_name)
        self["left_title"].setText("تفاصيل العنصر")
        ic_key = guess_icon(sec_key + " " + sec_name)

        items = self.db.get(sec_key, [])
        self.current_items = []
        for item in items:
            name = item.get("name", "") or item.get("title", "Package")
            path = item.get("path", "")
            inst = bool(path and os.path.exists(path))
            self.current_items.append({
                "title": name,
                "subtitle": "Online4Tech Official",
                "badge": "",
                "icon": ic_key,
                "installed": inst,
                "data": item
            })

        self["page_info"].setText("%d حزمة" % len(self.current_items))
        self.render_current_items()
        self.update_left_detail()

    def update_left_detail(self):
        if self.mode != "section" or not self.current_items:
            return
        idx = self.grid_index if self.view_style == "grid" else self["list"].getSelectedIndex()
        if idx < 0 or idx >= len(self.current_items):
            return
        data = self.current_items[idx]["data"]
        name = data.get("name", "") or data.get("title", "")
        path = data.get("path", "")
        inst = "مثبت" if (path and os.path.exists(path)) else "غير مثبت"
        txt = "%s\n\nالحالة: %s\n\nالمصدر:\nOnline4Tech Official" % (name, inst)
        self["left_info"].setText(txt)

    def move_up(self):
        if self.view_style == "grid":
            if self.grid_index >= 4:
                self.grid_index -= 4
                self.build_grid_rows()
        else:
            self["list"].up()
            self.grid_index = self["list"].getSelectedIndex()
            if self.mode == "main":
                self["side_list"].moveToIndex(self.grid_index)
            else:
                self.update_left_detail()

    def move_down(self):
        if self.view_style == "grid":
            if self.grid_index + 4 < len(self.current_items):
                self.grid_index += 4
                self.build_grid_rows()
        else:
            self["list"].down()
            self.grid_index = self["list"].getSelectedIndex()
            if self.mode == "main":
                self["side_list"].moveToIndex(self.grid_index)
            else:
                self.update_left_detail()

    def move_left(self):
        if self.view_style == "grid" and self.grid_index + 1 < len(self.current_items):
            self.grid_index += 1
            self.build_grid_rows()

    def move_right(self):
        if self.view_style == "grid" and self.grid_index > 0:
            self.grid_index -= 1
            self.build_grid_rows()

    def ok_pressed(self):
        if not self.current_items:
            return
        idx = self.grid_index if self.view_style == "grid" else self["list"].getSelectedIndex()
        if idx < 0 or idx >= len(self.current_items):
            return
        data = self.current_items[idx]["data"]
        if self.mode == "main":
            sec = data.get("section", "")
            title = data.get("name", "") or data.get("title", "") or sec
            self.show_section(sec, title)
        else:
            cmd = data.get("cmd", "")
            if cmd:
                self.session.open(Console, title="Online4Tech: " + (data.get("name", "") or "Install"), cmdlist=[cmd])

    def refresh_server(self):
        self["center_header"].setText("جاري تحديث قاعدة البيانات...")
        self.load_database(force=True)
        self["center_header"].setText("متجر أونلاين تكنولوجي الشامل")

    def back_pressed(self):
        if self.mode == "section":
            self.show_main()
        else:
            self.timer.stop()
            self.close()