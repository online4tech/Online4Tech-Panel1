# Online4Tech Panel

بانل احترافي لأجهزة **Enigma2** (صور مفتوحة المصدر: OpenATV / OpenPLi / OpenBH / OpenVIX / PurE2 ...) بيجمع **احدث البلجنات والاسكينات** في مكان واحد بتصميم زجاجي (Glass UI).
متوافق مع **Python 2 و Python 3** وبيشتغل على شاشات HD (1280×720) و Full HD (1920×1080).

A modern glass-style panel for Enigma2 receivers: browse and install the newest plugins and skins, upgrade, manage and maintain the box from one screen. Python 2 + 3, HD + FHD.

## المميزات / Features

| # | القسم | الوظيفة |
|---|-------|---------|
| 1 | Plugins | اقسام Online4Tech + فيد الصورة، بحث (MENU)، تثبيت وحذف |
| 2 | Skins | اسكينات حسب نوع الصورة + بوت لوجو + سبينر + بايكونز |
| 3 | Updates | يفحص النسخ الأحدث ويحدّث حزمة او الكل |
| 4 | Installed | عرض وحذف البلجنات/الاسكينات المثبتة |
| 5 | Tools | ريستارت واجهة، ريبوت، تفريغ الرام، مسح /tmp، تحديث الفيد |
| 6 | System info | الصورة، الذاكرة، IP، المساحة |
| 7 | Panel update | تحديث البانل نفسه من GitHub |
| 8 | About | معلومات |

التنقل: الأسهم + OK، ارقام 1-8، الألوان تحت الشاشة، **MENU** للبحث.

## التثبيت / Install

### Telnet / SSH (الأسهل)

```sh
wget -q --no-check-certificate -O - https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/stable/install.sh | sh
```

بيحمّل ملف IPK صغير (~400KB) ويثبّته، وبعدها الجهاز بيعمل ريستارت للواجهة تلقائي. افتح **Plugins** او **Extensions** ← *Online4Tech Panel*.

### IPK يدوي

```sh
opkg install --force-reinstall /tmp/enigma2-plugin-extensions-online4techpanel_all.ipk
```

## الجديد في 1.1.0

* **فلتر التوافق:** العناصر اللي محتاجة بايثون 2 او 3 (بتتعرف من الاسم/القسم) بتتخفي لو مش مناسبة لجهازك. زر **2** يعرضها كلها.
* **المفضلة:** زر **1** يضيف/يشيل العنصر من المفضلة (علامة `+`)، وقسم *Favourites* بيظهر اول القايمة، وزر **3** يثبّت كل المفضلة ورا بعض. بتتحفظ في `/etc/enigma2/o4t_favorites.json`.
* **الاعدادات (Tools):** لون الواجهة (سماوي/بنفسجي/اخضر/برتقالي/وردي) واللغة (تلقائي/عربي/English).
* **تقرير الدعم (Tools):** بيعرض بيانات الجهاز والكتالوج واللوج وبيحفظها في `/tmp/o4t_report.txt`؛ ابعته لو حصلت مشكلة. اوامر التثبيت/الحذف بتتسجل في `/tmp/o4t_panel.log`.
* **تحديث تلقائي للكتالوج:** `.github/workflows/update-catalog.yml` (يشتغل يومياً لما يكون في الفرع الافتراضي للمستودع).

## الأقسام (من قواعد بيانات Online4Tech)

الكتالوج `catalog.json` (627 عنصر) متجمّع من ملفات JSON اللي في حساب online4tech، ومقسّم زي تقسيمها الأصلي:

* **Plugins:** Panels, Plugins, Media, IPTV, Audio, EPG, Tools, System, Settings, Translation, Ciefp, Novaler, Multiboot, Dependencies, Community
* **Skins (حسب نوع الصورة):** OpenATV, OpenBH, Egami, OpenPLi Py3, OpenPLi Py2, OpenSPA, OpenVIX, PurE2, TeamNitro, Display (LCD), XStreamity, Community Skins + Bootlogos, Spinners, Picons
* **Image feed (opkg):** اول عنصر في كل قسم، بيقرا فيد صورتك مباشرة.

البانل بيكتشف صورتك (OpenATV/OpenBH/...) ويطلّع قسم السكينات المناسب لها اول القايمة، وبيعلّم المثبّت بنجمة `*`، وبيدعم الحذف للعناصر اللي ليها أمر حذف.

### تحديث الكتالوج

```sh
python3 tools/build_catalog.py            # يسحب المصادر من GitHub ويبني catalog.json
python3 tools/build_catalog.py --local DIR   # من نسخ محلية
git add catalog.json plugin && git commit -m "update catalog" && git push
```

البانل بيزامن `catalog.json` من GitHub كل ما تفتحه (او الزر الأصفر)، وعنده نسخة داخلية للعمل بدون انترنت.

**الأمان:** اي أمر تثبيت في الكتالوج بيتقبل بس لو بيحمّل من مواقع موثوقة (raw.githubusercontent.com, github.com, gitlab.com, dreambox4u.com, ...) — القايمة في `utils.py` (`TRUSTED_HOSTS`). اوامر الحذف لازم تكون `rm` لمسارات مطلقة غير سطحية او `opkg remove`. اللي مش مطابق بيتشال من الكتالوج.
اقسام Softcam/CCcam/BISS/DCW والقنوات والباك اب مش مضافة (خارج نطاق بلجنات وسكينات)؛ `--include-softcam` موجود في الأداة لو عايزها.

## للمطور / Development

```sh
python3 tools/make_assets.py     # يعيد توليد الأيقونات والخلفيات الزجاجية (Pillow)
python3 tools/build_catalog.py   # يعيد بناء catalog.json
./build_ipk.sh                   # ينتج release/enigma2-plugin-extensions-online4techpanel_all.ipk
```
مكان GitHub متسجل في `plugin/.../version.py` و `install.sh` (REPO / BRANCH).

الهيكل:

```
plugin/usr/lib/enigma2/python/Plugins/Extensions/Online4TechPanel/
  plugin.py  screens.py  skin.py  catalog.py  i18n.py  utils.py  version.py
  assets/{fhd,hd}/   data/catalog.json (نسخة offline)
```

الكود مكتوب بدون f-strings / type hints عشان يشتغل على Python 2.7 و 3.x.
الواجهة عربي/إنجليزي حسب لغة الجهاز.

## License

MIT


## Web control (port 8080)

Open `http://<receiver-ip>:8080` (no login by default; optional password in
**Tools > Web control**). Features: device status, quick
control, browse/install/remove plugins, skins, channel lists and picons from the catalog,
XStreamity/XKlass playlist entry, live console output, optional web shell.

Security: Basic auth + 5-attempt lockout, CSRF header on POST, install commands come only
from the validated catalog, web shell is OFF until enabled on the receiver (runs as root).
Not included on purpose: softcam installers and CCcam/oscam/ncam server-line writers.

## Release channels

| Channel | Branch | Install command | Who |
|---|---|---|---|
| **stable** | `stable` | `wget -q --no-check-certificate -O - https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/stable/install.sh \| sh` | customers |
| **dev** | `dev` | `wget -q --no-check-certificate -O - https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/stable/install.sh \| sh` | testing (shows `-dev` in the version) |

Work happens on `dev`. When a version is tested: `tools/promote.sh` copies it to `stable` and tags it.
Problem after a release? `tools/rollback.sh v1.9.0` puts customers back on the older tag.
