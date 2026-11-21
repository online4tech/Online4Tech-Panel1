# -*- coding: utf-8 -*-
"""English / Arabic strings (follows the receiver language)."""
from __future__ import absolute_import
try:
    from Components.Language import language
except Exception:  # pragma: no cover
    language = None


def is_ar():
    try:
        from .utils import get_setting
        forced = get_setting("lang", "auto")
        if forced == "ar":
            return True
        if forced == "en":
            return False
    except Exception:
        pass
    try:
        return language.getLanguage()[:2] == "ar"
    except Exception:
        return False


STR = {
    # menu: title, subtitle, hint
    "m_plugins": ("Plugins", "البلجنات"),
    "s_plugins": ("Latest plugins", "احدث البلجنات"),
    "h_plugins": ("Browse and install the newest plugins from your image feed and Online4Tech picks.",
                  "تصفح وثبّت احدث البلجنات من فيد الصورة واختيارات Online4Tech."),
    "m_skins": ("Skins", "الاسكينات"),
    "s_skins": ("Latest skins", "احدث الاسكينات"),
    "h_skins": ("Browse and install the newest skins. Restart GUI to apply.",
                "تصفح وثبّت احدث الاسكينات. اعمل ريستارت للواجهة لتفعيلها."),
    "m_updates": ("Updates", "التحديثات"),
    "s_updates": ("Upgrade packages", "تحديث الحزم"),
    "h_updates": ("Check for newer versions of installed plugins and upgrade them.",
                  "افحص النسخ الاحدث من البلجنات المثبتة وحدّثها."),
    "m_installed": ("Installed", "المثبّت"),
    "s_installed": ("Manage / remove", "ادارة / حذف"),
    "h_installed": ("List the plugins and skins installed on this receiver and remove them.",
                    "اعرض البلجنات والاسكينات المثبتة على الجهاز وامسح اللي مش عايزه."),
    "m_tools": ("Tools", "ادوات"),
    "s_tools": ("Restart, clean, free RAM", "ريستارت وتنظيف وذاكرة"),
    "h_tools": ("Restart GUI, reboot, clear RAM cache and temporary files.",
                "ريستارت للواجهة، اعادة تشغيل، تفريغ الذاكرة ومسح الملفات المؤقتة."),
    "m_info": ("System info", "معلومات الجهاز"),
    "s_info": ("Image, memory, storage", "الصورة والذاكرة والتخزين"),
    "h_info": ("Image version, kernel, Python, memory, IP address and free space.",
               "نسخة الصورة والكيرنل والبايثون والذاكرة وعنوان IP والمساحة الفاضية."),
    "m_selfupdate": ("Panel update", "تحديث البانل"),
    "s_selfupdate": ("Online4Tech Panel", "Online4Tech Panel"),
    "h_selfupdate": ("Check GitHub for a newer version of this panel and update it.",
                     "افحص GitHub لو فيه نسخة احدث من البانل وحدّثها."),
    "m_about": ("About", "عن البانل"),
    "s_about": ("Online4Tech", "Online4Tech"),
    "h_about": ("About Online4Tech Panel.", "معلومات عن Online4Tech Panel."),
    # keys
    "k_exit": ("Exit", "خروج"),
    "k_open": ("Open", "فتح"),
    "k_back": ("Back", "رجوع"),
    "k_install": ("Install", "تثبيت"),
    "k_remove": ("Remove", "حذف"),
    "k_upgrade": ("Upgrade", "تحديث"),
    "k_upgrade_all": ("Upgrade all", "تحديث الكل"),
    "k_refresh": ("Refresh", "تحديث القائمة"),
    "k_feed": ("Source: Feed", "المصدر: الفيد"),
    "k_featured": ("Source: Picks", "المصدر: مختارات"),
    "k_filter": ("Filter", "فلتر"),
    "k_run": ("Run", "تنفيذ"),
    "k_update": ("Update", "تحديث"),
    "k_catalog": ("Sync picks", "مزامنة"),
    "k_about": ("About", "عن البانل"),
    "cat_feed": ("Image feed (opkg)", "فيد الصورة (opkg)"),
    "recommended": ("recommended for your image", "مناسب لصورتك"),
    "k_sync": ("Sync", "مزامنة"),
    "k_open_cat": ("Open", "فتح"),
    "cat_hint": ("Press OK to open this category.", "اضغط OK لفتح القسم."),
    "n_items": ("items", "عنصر"),
    "category": ("Category", "القسم"),
    "dl_from": ("Downloads from", "التحميل من"),
    "images": ("Compatible images", "الصور المتوافقة"),
    "search_all": ("Search results", "نتائج البحث"),
    "feed_hint": ("Packages available in your image's own feed, always the newest for your box.",
                  "الحزم المتاحة في فيد صورتك نفسها، دايما الاحدث لجهازك."),
    "cat_fav": ("Favourites", "المفضلة"),
    "fav_hint": ("Your favourite items. Press 3 to install all of them at once.",
                 "العناصر المفضلة عندك. اضغط 3 لتثبيتها كلها مرة واحدة."),
    "hint_items": ("1: favourite   2: incompatible items   3: install favourites",
                   "1: مفضلة   2: غير المتوافق   3: تثبيت المفضلة"),
    "is_fav": ("Favourite", "مفضلة"),
    "not_compat": ("Not compatible with this receiver's Python version",
                   "مش متوافق مع نسخة بايثون في الجهاز"),
    "compat_shown": ("Showing incompatible items too", "بيعرض العناصر غير المتوافقة كمان"),
    "compat_hidden": ("Incompatible items hidden", "العناصر غير المتوافقة مخفية"),
    "fav_added": ("Added to favourites", "اتضافت للمفضلة"),
    "fav_removed": ("Removed from favourites", "اتشالت من المفضلة"),
    "fav_empty": ("No favourites yet. Press 1 on any item to add it.",
                  "مفيش مفضلة لسه. اضغط 1 على اي عنصر لاضافته."),
    "confirm_fav_all": ("Install ALL favourites one after another?",
                        "تثبّت كل المفضلة ورا بعض؟"),
    "t_theme": ("Theme colour", "لون الواجهة"),
    "d_theme": ("Changes the highlight colour. Reopen the panel to apply.",
                "بيغيّر لون التحديد. اقفل البانل وافتحه تاني للتطبيق."),
    "t_lang": ("Language", "اللغة"),
    "d_lang": ("Auto follows the receiver language. Reopen the panel to apply.",
               "تلقائي = لغة الجهاز. اقفل البانل وافتحه تاني للتطبيق."),
    "s_path": ("Path", "المسار"),
    "s_icmd": ("Install command", "أمر التثبيت"),
    "s_rcmd": ("Remove command", "أمر الإزالة"),
    "k_reinstall": ("Reinstall", "إعادة التثبيت"),
    "k_fav_add": ("Add to favourites", "إضافة للمفضلة"),
    "k_fav_del": ("Remove from favourites", "إزالة من المفضلة"),
    "k_install_now": ("Install now", "تثبيت الآن"),
    "pager": ("Page %d/%d   -   %d items", "صفحة %d/%d   -   عدد الإضافات: %d"),
    "contact": ("WhatsApp 01092978131   |   Online4Tech", "واتساب 01092978131   |   Online4Tech"),
    "search_hint": ("Press MENU to search...", "اضغط MENU للبحث..."),
    "t_web": ("Web control (port 8080)", "التحكم عبر الويب (بورت 8080)"),
    "d_web": ("Address, password and options of the browser control panel.",
              "عنوان وكلمة سر وخيارات لوحة التحكم من المتصفح."),
    "w_auth": ("Password login", "الحماية بكلمة سر"),
    "w_shell": ("Web shell", "تيرمنال الويب"),
    "w_toggle": ("Enable/Disable", "تشغيل/إيقاف"),
    "w_state": ("Web server", "سيرفر الويب"),
    "w_on": ("ON", "مفعّل"), "w_off": ("OFF", "متوقف"),
    "w_help": ("Green: password login on/off | Yellow: web shell on/off | Blue: server on/off.\n"
               "Anyone on your network can open the page when password login is off.\nThe web shell runs commands as root - keep it off unless you need it.",
               "أخضر: الحماية بكلمة سر | أصفر: تيرمنال الويب | أزرق: تشغيل/إيقاف السيرفر.\n"
               "أي شخص على شبكتك يقدر يفتح الصفحة لو الحماية متوقفة.\nتيرمنال الويب ينفذ أوامر بصلاحية root - اتركه مغلقاً إلا عند الحاجة."),
    "t_diag": ("Support report", "تقرير الدعم"),
    "d_diag": ("Shows system, catalog and log details and saves them to /tmp/o4t_report.txt.",
               "بيعرض بيانات الجهاز والكتالوج واللوج ويحفظها في /tmp/o4t_report.txt."),
    "reopen": ("Saved. Close and reopen the panel to apply.", "اتحفظ. اقفل البانل وافتحه تاني للتطبيق."),
    "v_auto": ("Auto", "تلقائي"),
    "v_ar": ("Arabic", "عربي"),
    "v_en": ("English", "English"),
    "dev_title": ("This receiver", "الجهاز"),
    "dev_name": ("Device", "اسم الجهاز"),
    "dev_img": ("Image / software", "الصورة والسوفت وير"),
    "dev_panel": ("Panel version", "اصدار البانل"),
    "dev_ip": ("Receiver IP", "عنوان IP للجهاز"),
    "dev_web": ("Web page", "صفحة الويب"),
    "web_off": ("off", "متوقف"),
    "m_settings": ("Settings", "الاعدادات"),
    "t_design": ("Design", "التصميم"),
    "d_design": ("Glass: glowing cards. Console: gold list. Flame: orange store. Lite: flat colours, no pictures (fastest on weak receivers).",
                 "Glass: كروت مضيئة. Console: قايمة ذهبية. Flame: متجر برتقالي. Lite: الوان سادة بدون صور (الاسرع للاجهزة الضعيفة)."),
    "t_font": ("Text size", "حجم الخط"),
    "d_font": ("Small, normal or large text on every screen.", "خط صغير او عادي او كبير في كل الشاشات."),
    "ds_glass": ("Glass", "Glass زجاجي"), "ds_console": ("Console", "Console ذهبي"),
    "ds_flame": ("Flame", "Flame برتقالي"), "ds_lite": ("Lite", "Lite خفيف"),
    "fs_90": ("Small", "صغير"), "fs_100": ("Normal", "عادي"), "fs_115": ("Large", "كبير"),
    "k_change": ("Change", "تغيير"),
    "k_apply": ("Apply", "تطبيق"),
    "h_settings_tip": ("Green: change   |   Yellow/Back: apply and reopen",
                       "اخضر: تغيير   |   اصفر او رجوع: تطبيق واعادة الفتح"),
    "th_cyan": ("Cyan", "سماوي"), "th_violet": ("Violet", "بنفسجي"), "th_green": ("Green", "اخضر"),
    "th_orange": ("Orange", "برتقالي"), "th_pink": ("Pink", "وردي"),
    # generic
    "loading": ("Loading...", "جاري التحميل..."),
    "empty": ("Nothing to show here.", "مفيش حاجة تتعرض هنا."),
    "empty_feed": ("The package feed is empty.\nPress BLUE to refresh the feed (needs internet).",
                   "فيد الحزم فاضي.\nاضغط الازرق لتحديث الفيد (محتاج انترنت)."),
    "search": ("Search", "بحث"),
    "installed_yes": ("Installed", "مثبّت"),
    "installed_no": ("Not installed", "غير مثبّت"),
    "status": ("Status", "الحالة"),
    "version": ("Version", "النسخة"),
    "package": ("Package", "الحزمة"),
    "source": ("Source", "المصدر"),
    "src_feed": ("Image feed (opkg)", "فيد الصورة (opkg)"),
    "src_picks": ("Online4Tech picks", "مختارات Online4Tech"),
    "new_version": ("New version", "النسخة الجديدة"),
    "restart_q": ("Restart the GUI now to apply the changes?",
                  "تعمل ريستارت للواجهة دلوقتي عشان التغييرات تشتغل؟"),
    "confirm": ("Are you sure?", "متأكد؟"),
    "confirm_remove": ("Remove this package?", "تمسح الحزمة دي؟"),
    "confirm_upgrade_all": ("Upgrade ALL packages? This can take a while.",
                            "تحدّث كل الحزم؟ ممكن ياخد وقت."),
    "synced": ("Picks list synced.", "اتعملت مزامنة للمختارات."),
    "sync_failed": ("Could not reach GitHub, using the built-in list.",
                    "مقدرتش اوصل لـ GitHub، هستخدم القايمة الداخلية."),
    "up_to_date": ("Everything is up to date.", "كل حاجة محدّثة."),
    "only_plugins": ("Filter: plugins", "فلتر: بلجنات"),
    "all_pkgs": ("Filter: all", "فلتر: الكل"),
    "f_all": ("All", "الكل"),
    "f_plugins": ("Plugins", "بلجنات"),
    "f_skins": ("Skins", "اسكينات"),
    # tools
    "t_restart_gui": ("Restart GUI", "ريستارت للواجهة"),
    "d_restart_gui": ("Restarts Enigma2 only (fast).", "بيعمل ريستارت للانيجما فقط (سريع)."),
    "t_reboot": ("Reboot receiver", "اعادة تشغيل الجهاز"),
    "d_reboot": ("Full reboot of the receiver.", "اعادة تشغيل كاملة للجهاز."),
    "t_standby": ("Deep standby", "اطفاء الجهاز"),
    "d_standby": ("Shuts the receiver down.", "بيطفي الجهاز."),
    "t_ram": ("Free RAM cache", "تفريغ كاش الذاكرة"),
    "d_ram": ("Drops the page cache to free memory.", "بيفرّغ كاش الذاكرة."),
    "t_tmp": ("Clean temp files", "مسح الملفات المؤقتة"),
    "d_tmp": ("Deletes downloaded .ipk/.tar.gz and panel temp files from /tmp.",
              "بيمسح ملفات ipk وtar.gz والمؤقتات بتاعة البانل من /tmp."),
    "t_feed": ("Update package feed", "تحديث فيد الحزم"),
    "d_feed": ("Runs 'opkg update'.", "بينفذ 'opkg update'."),
    "t_df": ("Show free space", "عرض المساحة الفاضية"),
    "d_df": ("Shows disk usage of the receiver.", "بيعرض استخدام المساحة."),
    "done": ("Done.", "تم."),
    # self update
    "su_installed": ("Installed version", "النسخة المثبتة"),
    "su_latest": ("Latest on GitHub", "احدث نسخة على GitHub"),
    "su_checking": ("Checking GitHub...", "بفحص GitHub..."),
    "su_unreachable": ("Could not reach GitHub. Check the internet connection.",
                       "مقدرتش اوصل لـ GitHub. اتأكد من الانترنت."),
    "su_newer": ("A new version is available. Press GREEN to update.",
                 "فيه نسخة جديدة. اضغط الاخضر للتحديث."),
    "su_same": ("You have the latest version. Press GREEN to reinstall.",
                "معاك احدث نسخة. اضغط الاخضر لاعادة التثبيت."),
    # about
    "about_text": (
        "Online4Tech Panel\n"
        "A modern all-in-one panel for Enigma2 receivers: browse and install the newest "
        "plugins and skins, upgrade, manage and maintain your receiver from one place.\n\n"
        "Works on OpenATV, OpenPLi, OpenBH, OpenVIX, PurE2 and other open-source images "
        "(Python 2 and Python 3).\n\n"
        "Navigation: arrows + OK, colour keys at the bottom, numbers 1-8 on the main menu, "
        "MENU to search in lists.",
        "Online4Tech Panel\n"
        "بانل حديث للأجهزة اللي بتشتغل بنظام Enigma2: تصفح وثبّت احدث البلجنات والاسكينات، "
        "حدّث وادير جهازك من مكان واحد.\n\n"
        "بيشتغل على OpenATV وOpenPLi وOpenBH وOpenVIX وPurE2 وباقي الصور المفتوحة "
        "(بايثون 2 و3).\n\n"
        "التنقل: الأسهم + OK، الازرار الملونة تحت، ارقام 1-8 في القايمة الرئيسية، "
        "زر MENU للبحث داخل القوايم."),
}


def T(key):
    pair = STR.get(key)
    if not pair:
        return key
    return pair[1] if is_ar() else pair[0]
