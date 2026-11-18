# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from .o4t_store import Online4TechStoreScreen

def main(session, **kwargs):
    session.open(Online4TechStoreScreen)

def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name="Online4Tech Panel & Store",
            description="Online4Tech All-in-One Store (350+ Plugins, Skins & Cams)",
            where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU],
            fnc=main
        )
    ]