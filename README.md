# Online4Tech Panel

بانل احترافي لأجهزة **Enigma2** (صور مفتوحة المصدر: OpenATV / OpenPLi / OpenBH / OpenVIX / PurE2 ...) بيجمع **احدث البلجنات والاسكينات** في مكان واحد بتصميم زجاجي (Glass UI).
متوافق مع **Python 2 و Python 3** وبيشتغل على شاشات HD (1280×720) و Full HD (1920×1080).

A modern glass-style panel for Enigma2 receivers: browse and install the newest plugins and skins, upgrade, manage and maintain the box from one screen. Python 2 + 3, HD + FHD.

## المميزات / Features

| # | القسم | الوظيفة |
|---|-------|---------|
| 1 | Plugins | تصفح فيد الصورة (opkg) + مختارات Online4Tech، بحث (MENU)، تثبيت بزر واحد |
| 2 | Skins | نفس الفكرة للاسكينات |
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
wget -q --no-check-certificate -O - https://raw.githubusercontent.com/YOUR_GITHUB_USER/Online4Tech-Panel/main/install.sh | sh
```

الجهاز هيعمل ريستارت للواجهة تلقائي، وبعدها افتح **Plugins** او **Extensions** ← *Online4Tech Panel*.

### IPK

```sh
./build_ipk.sh            # ينتج dist/enigma2-plugin-extensions-online4techpanel_<ver>_all.ipk
opkg install /tmp/enigma2-plugin-extensions-online4techpanel_*.ipk
```

## ازاي البلجنات "الأحدث" بتتجاب؟

* **فيد الصورة (opkg):** البانل بيقرا `opkg list` مباشرة، فبيعرض اللي متاح فعلاً لصورتك ونسخته الحالية (محتاج `opkg update` من الزر الأزرق مرة).
* **مختارات Online4Tech:** ملف [`catalog.json`](catalog.json) على GitHub. عدّله وارفعه والبانل بيعمل مزامنة تلقائية عند فتحه (او زر الأصفر). كل عنصر:

```json
{ "type": "plugin|skin", "name": "...", "version": "...", "desc": "...",
  "install": { "method": "feed|ipk|tar", "pkg": "اسم الحزمة", "url": "https://..." } }
```

`feed` = اسم حزمة opkg، `ipk` = رابط مباشر لملف ipk، `tar` = رابط tar.gz بيتفك على `/`.
البانل بيرفض أي اسم حزمة او رابط فيه رموز shell خطرة.

## للمطور / Development

```sh
python3 tools/make_assets.py     # يعيد توليد الأيقونات والخلفيات الزجاجية (Pillow)
tools/set_repo.sh USER/REPO      # يغيّر مكان GitHub في كل الملفات
./build_ipk.sh
```

الهيكل:

```
plugin/usr/lib/enigma2/python/Plugins/Extensions/Online4TechPanel/
  plugin.py  screens.py  skin.py  catalog.py  i18n.py  utils.py  version.py
  assets/{fhd,hd}/   data/catalog.json
```

الكود مكتوب بدون f-strings / type hints عشان يشتغل على Python 2.7 و 3.x.
الواجهة عربي/إنجليزي حسب لغة الجهاز.

## License

MIT
