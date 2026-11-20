# -*- coding: utf-8 -*-
from __future__ import absolute_import
from Plugins.Plugin import PluginDescriptor

from .version import PLUGIN_NAME


def main(session, **kwargs):
    from .screens import O4TMain
    session.open(O4TMain)


def Plugins(**kwargs):
    desc = "Latest plugins & skins panel - Online4Tech"
    return [
        PluginDescriptor(name=PLUGIN_NAME, description=desc,
                         where=PluginDescriptor.WHERE_PLUGINMENU,
                         icon="plugin.png", fnc=main),
        PluginDescriptor(name=PLUGIN_NAME, description=desc,
                         where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main),
    ]
