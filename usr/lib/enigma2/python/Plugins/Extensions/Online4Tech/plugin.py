# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from .o4t_store import Online4TechStoreScreen


def main(session, **kwargs):
    session.open(Online4TechStoreScreen)


def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name="Online4Tech Panel & Store",
            description="Online4Tech Gold Store v7.5 (838+ Plugins, Skins, Cams & IPTV)",
            where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
            icon="plugin.png",
            fnc=main,
        )
    ]