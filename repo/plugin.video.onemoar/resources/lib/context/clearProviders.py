# -*- coding: utf-8 -*-

import xbmc

if __name__ == '__main__':
	plugin = 'plugin://plugin.video.onemoar/'
	path = 'RunPlugin(%s?action=cache_clearSources&opensettings=false)' % plugin
	xbmc.executebuiltin(path)
