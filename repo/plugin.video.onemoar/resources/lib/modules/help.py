# -*- coding: utf-8 -*-
"""
	OneMoar Add-on
"""

from resources.lib.modules.control import addonPath, addonId, getOneMoarVersion, joinPath
from resources.lib.windows.textviewer import TextViewerXML


def get(file):
	onemoar_path = addonPath(addonId())
	onemoar_version = getOneMoarVersion()
	helpFile = joinPath(onemoar_path, 'resources', 'help', file + '.txt')
	f = open(helpFile, 'r', encoding='utf-8', errors='ignore')
	text = f.read()
	f.close()
	heading = '[B]OneMoar -  v%s - %s[/B]' % (onemoar_version, file)
	windows = TextViewerXML('textviewer.xml', onemoar_path, heading=heading, text=text)
	windows.run()
	del windows
