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

AR_FORMS = {
    u'\u0621': (u'\ufe80', u'\ufe80', u'\ufe80', u'\ufe80'),
    u'\u0622': (u'\ufe81', u'\ufe82', u'\ufe81', u'\ufe82'),
    u'\u0623': (u'\ufe83', u'\ufe84', u'\ufe83', u'\ufe84'),
    u'\u0624': (u'\ufe85', u'\ufe86', u'\ufe85', u'\ufe86'),
    u'\u0625': (u'\ufe87', u'\ufe88', u'\ufe87', u'\ufe88'),
    u'\u0626': (u'\ufe89', u'\ufe8a', u'\ufe8b', u'\ufe8c'),
    u'\u0627': (u'\ufe8d', u'\ufe8e', u'\ufe8d', u'\ufe8e'),
    u'\u0628': (u'\ufe8f', u'\ufe90', u'\ufe91', u'\ufe92'),
    u'\u0629': (u'\ufe93', u'\ufe94', u'\ufe93', u'\ufe94'),
    u'\u062a': (u'\ufe95', u'\ufe96', u'\ufe97', u'\ufe98'),
    u'\u062b': (u'\ufe99', u'\ufe9a', u'\ufe9b', u'\ufe9c'),
    u'\u062c': (u'\ufe9d', u'\ufe9e', u'\ufe9f', u'\ufea0'),
    u'\u062d': (u'\ufea1', u'\ufea2', u'\ufea3', u'\ufea4'),
    u'\u062e': (u'\ufea5', u'\ufea6', u'\ufea7', u'\ufea8'),
    u'\u062f': (u'\ufea9', u'\ufeaa', u'\ufea9', u'\ufeaa'),
    u'\u0630': (u'\ufeab', u'\ufeac', u'\ufeab', u'\ufeac'),
    u'\u0631': (u'\ufead', u'\ufeae', u'\ufead', u'\ufeae'),
    u'\u0632': (u'\ufeaf', u'\ufeb0', u'\ufeaf', u'\ufeb0'),
    u'\u0633': (u'\ufeb1', u'\ufeb2', u'\ufeb3', u'\ufeb4'),
    u'\u0634': (u'\ufeb5', u'\ufeb6', u'\ufeb7', u'\ufeb8'),
    u'\u0635': (u'\ufeb9', u'\ufeba', u'\ufebb', u'\ufebc'),
    u'\u0636': (u'\ufebd', u'\ufebe', u'\ufebf', u'\ufec0'),
    u'\u0637': (u'\ufec1', u'\ufec2', u'\ufec3', u'\ufec4'),
    u'\u0638': (u'\ufec5', u'\ufec6', u'\ufec7', u'\ufec8'),
    u'\u0639': (u'\ufec9', u'\ufeca', u'\ufecb', u'\ufecc'),
    u'\u063a': (u'\ufecd', u'\ufece', u'\ufecf', u'\ufed0'),
    u'\u0641': (u'\ufed1', u'\ufed2', u'\ufed3', u'\ufed4'),
    u'\u0642': (u'\ufed5', u'\ufed6', u'\ufed7', u'\ufed8'),
    u'\u0643': (u'\ufed9', u'\ufeda', u'\ufedb', u'\ufedc'),
    u'\u0644': (u'\ufedd', u'\ufede', u'\ufedf', u'\ufee0'),
    u'\u0645': (u'\ufee1', u'\ufee2', u'\ufee3', u'\ufee4'),
    u'\u0646': (u'\ufee5', u'\ufee6', u'\ufee7', u'\ufee8'),
    u'\u0647': (u'\ufee9', u'\ufeea', u'\ufeeb', u'\ufeec'),
    u'\u0648': (u'\ufeed', u'\ufeee', u'\ufeed', u'\ufeee'),
    u'\u0649': (u'\ufeef', u'\ufef0', u'\ufeef', u'\ufef0'),
    u'\u064a': (u'\ufef1', u'\ufef2', u'\ufef3', u'\ufef4'),
}
NON_CONNECT_NEXT = set(u'\u0621\u0622\u0623\u0624\u0625\u0627\u0629\u062f\u0630\u0631\u0632\u0648\u0649')

def ar(text):
    if not text or not any(u'\u0600' <= c <= u'\u06ff' for c in text):
        return text
    out = []
    n = len(text)
    for i, ch in enumerate(text):
        if ch not in AR_FORMS:
            out.append(ch)
            continue
        prev_c = (i > 0 and text[i - 1] in AR_FORMS and text[i - 1] not in NON_CONNECT_NEXT)
        next_c = (i + 1 < n and text[i + 1] in AR_FORMS)
        idx = (2 if next_c else 0) + (1 if prev_c else 0)
        out.append(AR_FORMS[ch][idx])
    shaped = "".join(out)
    tokens = shaped.split(" ")
    res_tokens = []
    ar_buf = []
    for tok in tokens:
        if any(u'\u0600' <= c <= u'\u06ff' or u'\ufe70' <= c <= u'\ufeff' for c in tok):
            ar_buf.insert(0, tok[::-1])
        else:
            if ar_buf:
                res_tokens.extend(ar_buf)
                ar_buf = []
            res_tokens.append(tok)
    if ar_buf:
        res_tokens.extend(ar_buf)
    return " ".join(res_tokens)

AR_CAT_MAP = {
    "Online4Tech Official": (u"باقة أونلاين تكنولوجي", u"إضافات وملفات حصرية لمتجر Online4Tech", "default"),
    "My Favourites": (u"المفضلة", u"الإضافات والبلاجنات المختارة", "default"),
    "Update Dependencic": (u"تحديث المكتبات", u"تحديث مكتبات البايثون والنظام", "tools"),
    "Backup Images": (u"صور الباك اب", u"تحميل وتثبيت صور أجهزة انيجما 2", "display"),
    "Panels": (u"البانلات", u"استكشف بانلات انيجما 2 مع روابط المطورين", "panels"),
    "Plugins": (u"الإضافات", u"إدارة وتثبيت البلاجيـنات", "plugins"),
    "Novaler": (u"نوفالر", u"بلاجيـنات وأدوات لأجهزة نوفالر", "plugins"),
    "Channels": (u"ملفات القنوات", u"تحديث وتثبيت أحدث ملفات القنوات", "channels"),
    "Feeds": (u"الفيدات", u"تحديث وتثبيت الفيدات", "feeds"),
    "Bootlogos": (u"شعارات الإقلاع", u"تغيير شعارات الإقلاع وأيقونات التحميل", "display"),
    "Spinners": (u"أيقونات التحميل", u"تغيير سبينر التحميل الدوار", "display"),
    "Tools": (u"الأدوات", u"أدوات وإضافات مفيدة للنظام", "tools"),
    "System": (u"خدمات النظام", u"إعدادات وأوامر صيانة الرسيفر", "tools"),
    "Softcams": (u"السوفتكامات", u"إدارة وتشغيل إيموهات التشفير", "cams"),
    "Skins": (u"السكينات", u"اختيار وتطبيق السكينات", "skins"),
    "Picons": (u"البيكونات", u"تثبيت وإدارة شعارات القنوات", "picons"),
}

class O4TCardList(MenuList):
    def __init__(self, items):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(74)
        self.l.setFont(0, gFont("Regular", 22))
        self.l.setFont(1, gFont("Regular", 18))

class O4TGridRows(MenuList):
    def __init__(self, items):
        MenuList.__init__(self, items, False, eListboxPythonMultiContent)
        self.l.setItemHeight(255)
        self.l.setFont(0, gFont("Regular", 24))
        self.l.setFont(1, gFont("Regular", 18))

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

        <!-- عناصر وضع القائمة (3 أعمدة) -->
        <widget name="left_bg" position="40,145" size="380,820" backgroundColor="#11141c" />
        <widget name="left_title" position="55,165" size="350,38" font="Regular;24" foregroundColor="#f5d061" backgroundColor="#11141c" transparent="1" halign="center" />
        <widget name="left_line" position="65,212" size="330,1" backgroundColor="#262b38" />
        <widget name="left_info" position="60,230" size="340,710" font="Regular;20" foregroundColor="#cbd5e1" backgroundColor="#11141c" transparent="1" halign="center" />

        <widget name="page_info" position="460,128" size="320,32" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="left" />
        <widget name="section_heading" position="1080,124" size="340,38" font="Regular;28" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="right" />
        <widget name="list" position="460,170" size="960,795" backgroundColor="#0b0d12" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

        <widget name="right_bg" position="1460,145" size="420,820" backgroundColor="#11141c" />
        <widget name="right_header" position="1480,165" size="380,36" font="Regular;22" foregroundColor="#94a3b8" backgroundColor="#11141c" transparent="1" halign="center" />
        <widget name="right_line" position="1480,210" size="380,1" backgroundColor="#262b38" />
        <widget name="side_list" position="1475,225" size="390,720" font="Regular;23" itemHeight="54" foregroundColor="#cbd5e1" backgroundColor="#11141c" foregroundColorSelected="#f5d061" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

        <!-- وضع الشبكة 4x3 (ملء الشاشة) -->
        <widget name="grid_list" position="55,165" size="1810,780" backgroundColor="#0b0d12" backgroundColorSelected="#0b0d12" scrollbarMode="showNever" enableWrapAround="1" />

        <!-- الشريط السفلي لأزرار الريموت -->
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
        self["center_header"] = Label(ar(u"متجر أونلاين تكنولوجي الشامل"))

        self["left_bg"] = Label("")
        self["left_title"] = Label(ar(u"النظام"))
        self["left_line"] = Label("")
        self["left_info"] = Label("")

        self["page_info"] = Label("")
        self["section_heading"] = Label(ar(u"الرئيسية"))

        self["right_bg"] = Label("")
        self["right_header"] = Label(ar(u"الأقسام"))
        self["right_line"] = Label("")

        self["key_red"] = Label(ar(u"خروج"))
        self["key_green"] = Label(ar(u"تثبيت / فتح"))
        self["key_yellow"] = Label(ar(u"تبديل العرض (شبكة)"))
        self["key_blue"] = Label(ar(u"تحديث السيرفر"))
        self["mode_badge"] = Label(ar(u"عرض القائمة  |  أصفر للشبكة"))

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
        self.sec_icon_key = "default"

        self.card_norm = None
        self.grid_norm = None
        self.grid_sel = None

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
        try:
            for attr, fname in [("card_norm", "card_normal.png"), ("grid_norm", "grid_norm.png"), ("grid_sel", "grid_sel.png")]:
                p = os.path.join(ICONS_PATH, fname)
                if os.path.exists(p):
                    setattr(self, attr, LoadPixmap(p))
            self.update_clock()
            self.timer.start(10000)
            self.apply_view_visibility()
            self.load_database(force=False)
        except Exception as e:
            self["center_header"].setText("Startup Error: " + str(e))

    def apply_view_visibility(self):
        is_grid = (self.view_style == "grid")
        for w in ["left_bg", "left_title", "left_line", "left_info", "page_info", "section_heading", "list", "right_bg", "right_header", "right_line", "side_list"]:
            if is_grid:
                self[w].hide()
            else:
                self[w].show()
        if is_grid:
            self["grid_list"].show()
            self["key_yellow"].setText(ar(u"تبديل العرض (قائمة)"))
            self["mode_badge"].setText(ar(u"عرض الشبكة 4x3  |  أصفر للقائمة"))
        else:
            self["grid_list"].hide()
            self["key_yellow"].setText(ar(u"تبديل العرض (شبكة)"))
            self["mode_badge"].setText(ar(u"عرض القائمة  |  أصفر للشبكة"))

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
            self["center_header"].setText("DB Error: " + str(e))

    def get_icon_pix(self, icon_key):
        ic_file = os.path.join(ICONS_PATH, "ic_%s.png" % icon_key)
        if not os.path.exists(ic_file):
            ic_file = os.path.join(ICONS_PATH, "ic_default.png")
        return LoadPixmap(ic_file) if os.path.exists(ic_file) else None

    def make_list_card(self, title, subtitle, badge, icon_key, is_installed, data):
        ic_pix = self.get_icon_pix(icon_key)
        res = [data]
        if self.card_norm:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 10, 3, 940, 68, self.card_norm))
        if ic_pix:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 875, 11, 52, 52, ic_pix))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 470, 14, 385, 44, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, ar(title), 0x00ffffff, 0x00f5d061))
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 140, 14, 315, 44, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, ar(subtitle), 0x00cbd5e1, 0x00ffffff))
        if is_installed:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 25, 16, 105, 40, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, ar(u"مثبت"), 0x00ff5555, 0x00ff8888))
        elif badge:
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 25, 16, 105, 40, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, badge, 0x00f5d061, 0x00ffffff))
        return res

    def build_grid_rows(self):
        # 4 أعمدة في كل صف من اليمين إلى اليسار كما في الصورة الثالثة
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
                bg_pix = self.grid_sel if is_selected else self.grid_norm
                if bg_pix:
                    row_entries.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x0, 8, 430, 235, bg_pix))
                ic_pix = self.get_icon_pix(entry["icon"])
                if ic_pix:
                    row_entries.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, x0 + 350, 28, 52, 52, ic_pix))
                t_col = 0x00f5d061 if is_selected else 0x00ffffff
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 28, 315, 52, 0, RT_HALIGN_RIGHT | RT_VALIGN_CENTER, ar(entry["title"]), t_col, t_col))
                row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 95, 390, 95, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, ar(entry["subtitle"]), 0x00cbd5e1, 0x00ffffff))
                if entry["installed"]:
                    row_entries.append((eListboxPythonMultiContent.TYPE_TEXT, x0 + 20, 192, 110, 32, 1, RT_HALIGN_CENTER | RT_VALIGN_CENTER, ar(u"مثبت"), 0x00ff5555, 0x00ff5555))
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
        self["key_red"].setText(ar(u"خروج"))
        self["section_heading"].setText(ar(u"الأقسام الرئيسية"))
        self["left_title"].setText(ar(u"النظام"))
        self["left_info"].setText(self.get_sys_info_text())

        cats = self.db.get("main", [])
        self.current_items = []
        side_items = []
        for item in cats:
            en_name = item.get("name", "")
            sec = item.get("section", "")
            cnt = len(self.db.get(sec, []))
            ar_title, ar_desc, ic_key = AR_CAT_MAP.get(en_name, (en_name, "%d Packages" % cnt, "default"))
            self.current_items.append({
                "title": ar_title,
                "subtitle": ar_desc,
                "badge": "(%d)" % cnt,
                "icon": ic_key,
                "installed": False,
                "data": item
            })
            side_items.append((ar(ar_title) + "  (%d)" % cnt, item))

        self["side_list"].setList(side_items)
        self["page_info"].setText(ar(u"%d عنصر" % len(self.current_items)))
        self.render_current_items()

    def show_section(self, sec_key, sec_name):
        self.mode = "section"
        self.grid_index = 0
        self["key_red"].setText(ar(u"رجوع"))
        ar_title, _, ic_key = AR_CAT_MAP.get(sec_name, (sec_name, "", "default"))
        self["section_heading"].setText(ar(ar_title))
        self["left_title"].setText(ar(u"تفاصيل العنصر"))

        items = self.db.get(sec_key, [])
        self.current_items = []
        for item in items:
            name = item.get("name", "Package")
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

        self["page_info"].setText(ar(u"%d حزمة" % len(self.current_items)))
        self.render_current_items()
        self.update_left_detail()

    def update_left_detail(self):
        if self.mode != "section" or not self.current_items:
            return
        idx = self.grid_index if self.view_style == "grid" else self["list"].getSelectedIndex()
        if idx < 0 or idx >= len(self.current_items):
            return
        data = self.current_items[idx]["data"]
        name = data.get("name", "")
        path = data.get("path", "")
        inst = ar(u"مثبت") if (path and os.path.exists(path)) else ar(u"غير مثبت")
        txt = "%s\n\n%s: %s\n\n%s:\nOnline4Tech Official" % (
            name, ar(u"الحالة"), inst, ar(u"المصدر")
        )
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
            self.show_section(data.get("section", ""), data.get("name", ""))
        else:
            cmd = data.get("cmd", "")
            if cmd:
                self.session.open(Console, title="Online4Tech: " + data.get("name", ""), cmdlist=[cmd])

    def refresh_server(self):
        self["center_header"].setText(ar(u"جاري تحديث قاعدة البيانات..."))
        self.load_database(force=True)
        self["center_header"].setText(ar(u"متجر أونلاين تكنولوجي الشامل"))

    def back_pressed(self):
        if self.mode == "section":
            self.show_main()
        else:
            self.timer.stop()
            self.close()