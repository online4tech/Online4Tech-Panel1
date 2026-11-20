# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Plugins.Plugin import PluginDescriptor

from .version import PLUGIN_NAME


def main(session, **kwargs):
    from .screens import O4TMain
    session.open(O4TMain)


def autostart(reason, **kwargs):
    if reason == 0:
        try:
            from . import webserver
            webserver.start()
        except Exception as exc:  # never break enigma2 start-up
            try:
                from .utils import log
                log("web autostart failed: %s" % exc)
            except Exception:
                pass


def Plugins(**kwargs):
    desc = "Latest plugins & skins panel - Online4Tech"
    return [
        PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart),
        PluginDescriptor(name=PLUGIN_NAME, description=desc,
                         where=PluginDescriptor.WHERE_PLUGINMENU,
                         icon="plugin.png", fnc=main),
        PluginDescriptor(name=PLUGIN_NAME, description=desc,
                         where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main),
    ]
