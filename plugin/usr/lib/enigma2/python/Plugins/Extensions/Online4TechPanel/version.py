# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

VERSION = "1.9.11"
PLUGIN_NAME = "Online4Tech Panel"
SLOGAN = "خليك دايما اونلاين"

GITHUB_REPO = "online4tech/Online4Tech-Panel1"
BRANCH = "panel-v2"

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/%s/%s" % (GITHUB_REPO, BRANCH)
CATALOG_URL = RAW + "/catalog.json"
VERSION_URL = RAW + "/version.txt"
INSTALL_URL = RAW + "/install.sh"
HOME_URL = "https://github.com/%s/tree/%s" % (GITHUB_REPO, BRANCH)

TMP_CATALOG = "/tmp/o4t_catalog.json"
TMP_VERSION = "/tmp/o4t_version.txt"

# Contact links shown in the web panel (empty = hidden)
WHATSAPP_NUMBER = "201092978131"
WHATSAPP_URL = "https://wa.me/" + WHATSAPP_NUMBER
MESSENGER_URL = "https://www.facebook.com/ahmad.m.romeh/"
PAGE_URL = "https://www.facebook.com/online4tech0"
# Telegram channel link, e.g. "https://t.me/yourchannel" (empty = button hidden)
TELEGRAM_URL = "https://t.me/Online4tech"
STORE_URL = "https://sllr.co/online4tech"
SITE_URL = "https://online4tech.github.io/online4Tech/"
SUPPORT_URL = WHATSAPP_URL
WEB_PORT = 9095
