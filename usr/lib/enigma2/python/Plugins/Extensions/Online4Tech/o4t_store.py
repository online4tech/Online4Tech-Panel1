# -*- coding: utf-8 -*-
import os, sys, json, time, socket, traceback, urllib.request, ssl
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
    "Online4Tech Official": (u"باقة أونلاين تكنولوجي الرسمية", u"إضافات وملفات حصرية لمتجر Online4Tech", "default"),
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

class Online4TechStoreScreen(Screen):
    skin = """
    <screen name="Online4TechStoreScreen" position="0,0" size="1920,1080" title="Online4Tech Panel" flags="wfNoBorder" backgroundColor="#0b0d12">
        <eLabel position="0,0" size="1920,115" backgroundColor="#0f1218" />
        <eLabel position="0,114" size="1920,2" backgroundColor="#1e222d" />

        <widget name="clock_lbl" position="55,15" size="260,48" font="Regular;40" foregroundColor="#ffffff" backgroundColor="#0f1218" transparent="1" halign="center" />
        <widget name="date_lbl" position="55,64" size="260,26" font="Regular;19" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />
        <eLabel text="NET: ONLINE" position="55,90" size="260,22" font="Regular;16" foregroundColor="#22c55e" backgroundColor="#0f1218" transparent="1" halign="center" />

        <eLabel position="460,28" size="960,56" backgroundColor="#161922" />
        <widget name="center_header" position="480,28" size="920,56" font="Regular;24" foregroundColor="#e2e8f0" backgroundColor="#161922" transparent="1" halign="center" valign="center" />

        <eLabel text="Online4TechPanel" position="1480,18" size="390,46" font="Regular;34" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="center" />
        <eLabel text="Online4Tech | v7.5 Gold" position="1480,68" size="390,28" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0f1218" transparent="1" halign="center" />

        <eLabel position="40,145" size="380,820" backgroundColor="#11141c" />
        <widget name="left_title" position="55,165" size="350,38" font="Regular;24" foregroundColor="#f5d061" backgroundColor="#11141c" transparent="1" halign="center" />
        <eLabel position="65,212" size="330,1" backgroundColor="#262b38" />
        <widget name="left_info" position="60,230" size="340,710" font="Regular;20" foregroundColor="#cbd5e1" backgroundColor="#11141c" transparent="1" halign="center" />

        <widget name="page_info" position="460,128" size="320,32" font="Regular;20" foregroundColor="#94a3b8" backgroundColor="#0b0d12" transparent="1" halign="left" />
        <widget name="section_heading" position="1080,124" size="340,38" font="Regular;28" foregroundColor="#ffffff" backgroundColor="#0b0d12" transparent="1" halign="right" />
        <widget name="list" position="460,170" size="960,795" backgroundColor="#0b0d12" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

        <eLabel position="1460,145" size="420,820" backgroundColor="#11141c" />
        <widget name="right_header" position="1480,165" size="380,36" font="Regular;22" foregroundColor="#94a3b8" backgroundColor="#11141c" transparent="1" halign="center" />
        <eLabel position="1480,210" size="380,1" backgroundColor="#262b38" />
        <widget name="side_list" position="1475,225" size="390,720" font="Regular;23" itemHeight="54" foregroundColor="#cbd5e1" backgroundColor="#11141c" foregroundColorSelected="#f5d061" backgroundColorSelected="#262012" scrollbarMode="showNever" enableWrapAround="1" />

        <eLabel position="0,990" size="1920,90" backgroundColor="#0f1218" />
        <eLabel position="0,990" size="1920,2" backgroundColor="#1e222d" />

        <eLabel position="1810,1022" size="24,24" backgroundColor="#ef4444" />
        <widget name="key_red" position="1610,1016" size="190,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

        <eLabel position="1520,1022" size="24,24" backgroundColor="#22c55e" />
        <widget name="key_green" position="1310,1016" size="200,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

        <eLabel position="1220,1022" size="24,24" backgroundColor="#eab308" />
        <widget name="key_yellow" position="1000,1016" size="210,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

        <eLabel position="910,1022" size="24,24" backgroundColor="#3b82f6" />
        <widget name="key_blue" position="700,1016" size="200,36" font="Regular;22" foregroundColor="#e2e8f0" backgroundColor="#0f1218" transparent="1" halign="right" />

        <widget name="mode_badge" position="80,1016" size="300,36" font="Regular;22" foregroundColor="#f5d061" backgroundColor="#0f1218" transparent="1" halign="left" />
    </screen>
    """

    def __init__(self, session):
        Screen.__init__(self, session)
        self["clock_lbl"] = Label("")
        self["date_lbl"] = Label("")
        self["center_header"] = Label(ar(u"متجر أونلاين تكنولوجي الشامل"))
        self["left_title"] = Label(ar(u"النظام"))
        self["left_info"] = Label("")
        self["page_info"] = Label("")
        self["section_heading"] = Label(ar(u"الرئيسية"))
        self["right_header"] = Label(ar(u"الأقسام"))
        self["key_red"] = Label(ar(u"خروج"))
        self["key_green"] = Label(ar(u"تثبيت / فتح"))
        self["key_yellow"] = Label(ar(u"تحديث السيرفر"))
        self["key_blue"] = Label(ar(u"حذف"))
        self["mode_badge"] = Label(ar(u"حديث  |  متعدد"))

        self["list"] = O4TCardList([])
        self["side_list"] = MenuList([])

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "ok": self.ok_pressed,
            "cancel": self.back_pressed,
            "red": self.back_pressed,
            "green": self.ok_pressed,
            "yellow": self.refresh_server,
            "blue": self.uninstall_pressed,
            "up": self.move_up,
            "down": self.move_down,
        }, -1)

        self.db = {}
        self.mode = "main"
        self.card_norm = None
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
            c_file = os.path.join(ICONS_PATH, "card_normal.png")
            if os.path.exists(c_file):
                self.card_norm = LoadPixmap(c_file)
            self.update_clock()
            self.timer.start(10000)
            self["left_info"].setText(self.get_sys_info_text())
            self.load_database(force=False)
        except Exception as e:
            self["center_header"].setText("Startup Error: " + str(e))

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

    def make_card(self, title, subtitle, badge, icon_key, is_installed, data):
        ic_file = os.path.join(ICONS_PATH, "ic_%s.png" % icon_key)
        if not os.path.exists(ic_file):
            ic_file = os.path.join(ICONS_PATH, "ic_default.png")
        ic_pix = LoadPixmap(ic_file) if os.path.exists(ic_file) else None
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

    def show_main(self):
        try:
            self.mode = "main"
            self["key_red"].setText(ar(u"خروج"))
            self["section_heading"].setText(ar(u"الأقسام الرئيسية"))
            self["left_title"].setText(ar(u"النظام"))
            self["left_info"].setText(self.get_sys_info_text())

            cats = self.db.get("main", [])
            cards = []
            side_items = []
            for item in cats:
                en_name = item.get("name", "")
                sec = item.get("section", "")
                cnt = len(self.db.get(sec, []))
                ar_title, ar_desc, ic_key = AR_CAT_MAP.get(en_name, (en_name, "%d Packages" % cnt, "default"))
                cards.append(self.make_card(ar_title, ar_desc, "(%d)" % cnt, ic_key, False, item))
                side_items.append((ar(ar_title) + "  (%d)" % cnt, item))

            self["list"].setList(cards)
            self["side_list"].setList(side_items)
            self["page_info"].setText(ar(u"%d عنصر" % len(cards)))
        except Exception as e:
            self["center_header"].setText("Main Error: " + str(e))

    def show_section(self, sec_key, sec_name):
        try:
            self.mode = "section"
            self["key_red"].setText(ar(u"رجوع"))
            ar_title, _, ic_key = AR_CAT_MAP.get(sec_name, (sec_name, "", "default"))
            self["section_heading"].setText(ar(ar_title))
            self["left_title"].setText(ar(u"تفاصيل العنصر"))

            items = self.db.get(sec_key, [])
            cards = []
            for item in items:
                name = item.get("name", "Package")
                path = item.get("path", "")
                inst = bool(path and os.path.exists(path))
                cards.append(self.make_card(name, "Online4Tech", "", ic_key, inst, item))

            self["list"].setList(cards)
            self["page_info"].setText(ar(u"%d حزمة" % len(cards)))
            self.update_left_detail()
        except Exception as e:
            self["center_header"].setText("Sec Error: " + str(e))

    def update_left_detail(self):
        if self.mode != "section":
            return
        cur = self["list"].getCurrent()
        if not cur:
            return
        data = cur[0]
        name = data.get("name", "")
        path = data.get("path", "")
        inst = ar(u"مثبت") if (path and os.path.exists(path)) else ar(u"غير مثبت")
        txt = "%s\n\n%s: %s\n\n%s:\nOnline4Tech Official" % (
            name, ar(u"الحالة"), inst, ar(u"المصدر")
        )
        self["left_info"].setText(txt)

    def move_up(self):
        self["list"].up()
        if self.mode == "main":
            self["side_list"].moveToIndex(self["list"].getSelectedIndex())
        else:
            self.update_left_detail()

    def move_down(self):
        self["list"].down()
        if self.mode == "main":
            self["side_list"].moveToIndex(self["list"].getSelectedIndex())
        else:
            self.update_left_detail()

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
                self.session.open(Console, title="Online4Tech: " + data.get("name", ""), cmdlist=[cmd])

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
            self.session.open(MessageBox, ar(u"لا يوجد أمر حذف تلقائي لهذا العنصر"), MessageBox.TYPE_INFO, timeout=3)

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