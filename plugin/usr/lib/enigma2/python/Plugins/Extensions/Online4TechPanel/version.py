# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

VERSION = "1.1.1"
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
