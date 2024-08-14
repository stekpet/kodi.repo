# -*- coding: utf-8 -*-
"""
	OneMoar Add-on
"""

import sys
from resources.lib.modules import router
from xbmc import getInfoLabel
if __name__ == '__main__':
	router.router(sys.argv[2])
	if 'onemoar' not in getInfoLabel('Container.PluginName'): sys.exit(1) #TikiPeter RLI-Fix Test
