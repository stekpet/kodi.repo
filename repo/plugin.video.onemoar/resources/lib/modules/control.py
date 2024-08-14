# -*- coding: utf-8 -*-
"""
	OneMoar Add-on
"""

from json import dumps as jsdumps, loads as jsloads
import os.path
#import xml.etree.ElementTree as ET
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from threading import Thread
from urllib.parse import unquote, unquote_plus
from xml.dom.minidom import parse as mdParse

# Kodi JSON-RPC API endpoint
api_url = 'http://localhost:8080/jsonrpc'
addon = xbmcaddon.Addon
AddonID = xbmcaddon.Addon().getAddonInfo('id')
addonInfo = xbmcaddon.Addon().getAddonInfo
addonName = addonInfo('name')
addonVersion = addonInfo('version')
getLangString = xbmcaddon.Addon().getLocalizedString

dialog = xbmcgui.Dialog()
numeric_input = xbmcgui.INPUT_NUMERIC
alpha_input = xbmcgui.INPUT_ALPHANUM
getCurrentDialogId = xbmcgui.getCurrentWindowDialogId()
getCurrentWindowId = xbmcgui.getCurrentWindowId()
homeWindow = xbmcgui.Window(10000)
playerWindow = xbmcgui.Window(12005)
infoWindow = xbmcgui.Window(12003)
item = xbmcgui.ListItem
progressDialog = xbmcgui.DialogProgress()
progressDialogBG = xbmcgui.DialogProgressBG()
progress_line = '%s[CR]%s'
progress_line2 = '%s[CR]%s[CR]%s'

addItem = xbmcplugin.addDirectoryItem
content = xbmcplugin.setContent
directory = xbmcplugin.endOfDirectory
property = xbmcplugin.setProperty
resolve = xbmcplugin.setResolvedUrl
sortMethod = xbmcplugin.addSortMethod

condVisibility = xbmc.getCondVisibility
execute = xbmc.executebuiltin
infoLabel = xbmc.getInfoLabel
jsonrpc = xbmc.executeJSONRPC
keyboard = xbmc.Keyboard
log = xbmc.log
monitor_class = xbmc.Monitor
monitor = monitor_class()
player = xbmc.Player()
player2 = xbmc.Player
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
playlistM = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
skin = xbmc.getSkinDir()

deleteDir = xbmcvfs.rmdir
deleteFile = xbmcvfs.delete
existsPath = xbmcvfs.exists
legalFilename = xbmcvfs.makeLegalFilename
listDir = xbmcvfs.listdir
makeFile = xbmcvfs.mkdir
makeDirs = xbmcvfs.mkdirs
openFile = xbmcvfs.File
transPath = xbmcvfs.translatePath

joinPath = os.path.join
isfilePath = os.path.isfile
absPath = os.path.abspath

SETTINGS_PATH = transPath(joinPath(addonInfo('path'), 'resources', 'settings.xml'))
try: dataPath = transPath(addonInfo('profile')).decode('utf-8')
except: dataPath = transPath(addonInfo('profile'))
settingsFile = joinPath(dataPath, 'settings.xml')
viewsFile = joinPath(dataPath, 'views.db')
bookmarksFile = joinPath(dataPath, 'bookmarks.db')
providercacheFile = joinPath(dataPath, 'providers.db')
metacacheFile = joinPath(dataPath, 'metadata.db')
searchFile = joinPath(dataPath, 'search.db')
libcacheFile = joinPath(dataPath, 'library.db')
libCacheSimilar = joinPath(dataPath, 'librarymoviescache.db')
cacheFile = joinPath(dataPath, 'cache.db')
traktSyncFile = joinPath(dataPath, 'traktSync.db')
subsFile = joinPath(dataPath, 'substitute.db')
fanarttvCacheFile = joinPath(dataPath, 'fanarttv.db')
metaInternalCacheFile = joinPath(dataPath, 'video_cache.db')
favouritesFile = joinPath(dataPath, 'favourites.db')
plexSharesFile = joinPath(dataPath, 'plexshares.db')
trailer = 'plugin://plugin.video.youtube/play/?video_id=%s'
subtitlesPath = joinPath(dataPath, 'subtitles')
watchedcacheFile = joinPath(dataPath, 'watched.db')
KODI_VERSION = int(xbmc.getInfoLabel("System.BuildVersion")[:2])

def getKodiVersion(full=False):
	if full: return xbmc.getInfoLabel("System.BuildVersion")
	else: return int(xbmc.getInfoLabel("System.BuildVersion")[:2])

def setting(id, fallback=None):
	try: settings_dict = jsloads(homeWindow.getProperty('onemoar_settings'))
	except: settings_dict = make_settings_dict()
	if settings_dict is None: settings_dict = settings_fallback(id)
	value = settings_dict.get(id, '')
	if fallback is None: return value
	if value == '': return fallback
	return value

def settings_fallback(id):
	return {id: xbmcaddon.Addon().getSetting(id)}

def setSetting(id, value):
	xbmcaddon.Addon().setSetting(id, value)

def make_settings_dict(): # service runs upon a setting change
	try:
		#root = ET.parse(settingsFile).getroot()
		root = mdParse(settingsFile) #minidom instead of element tree
		curSettings = root.getElementsByTagName("setting") #minidom instead of element tree
		settings_dict = {}
		for item in curSettings:
			dict_item = {}
			#setting_id = item.get('id')
			setting_id = item.getAttribute('id') #minidom instead of element tree
			try:
				setting_value = item.firstChild.data #minidom instead of element tree
			except:
				setting_value = None
			if setting_value is None: setting_value = ''
			dict_item = {setting_id: setting_value}
			settings_dict.update(dict_item)
		homeWindow.setProperty('onemoar_settings', jsdumps(settings_dict))
		refresh_playAction()
		refresh_libPath()
		return settings_dict
	except: return None

def openSettings(query=None, id=addonInfo('id')):
	try:
		hide()
		execute('Addon.OpenSettings(%s)' % id)
		if not query: return
		c, f = query.split('.')
		execute('SetFocus(%i)' % (int(c) - 100))
		execute('SetFocus(%i)' % (int(f) - 80))
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def lang(language_id):
	return str(getLangString(language_id))

def sleep(time):  # Modified `sleep`(in milli secs) that honors a user exit request
	while time > 0 and not monitor.abortRequested():
		xbmc.sleep(min(100, time))
		time = time - 100

def getCurrentViewId():
	win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
	return str(win.getFocusId())

def getOneMoarVersion():
	return xbmcaddon.Addon('plugin.video.onemoar').getAddonInfo('version')

def addonVersion(addon):
	return xbmcaddon.Addon(addon).getAddonInfo('version')

def addonId():
	return addonInfo('id')

def addonName():
	return addonInfo('name')

def addonPath(addon):
	try: addonID = xbmcaddon.Addon(addon)
	except: addonID = None
	if addonID is None: return ''
	else:
		try: return transPath(addonID.getAddonInfo('path').decode('utf-8'))
		except: return transPath(addonID.getAddonInfo('path'))

def addonInstalled(addon_id):
	return condVisibility('System.HasAddon(%s)' % addon_id)

def artPath():
	theme = appearance()
	return joinPath(xbmcaddon.Addon('plugin.video.onemoar').getAddonInfo('path'), 'resources', 'media', theme)

def genreIconPath():
	theme = appearance()
	return joinPath(xbmcaddon.Addon('plugin.video.onemoar').getAddonInfo('path'), 'resources', 'media', 'genre_media', 'icons')

def genrePosterPath():
	theme = appearance()
	return joinPath(xbmcaddon.Addon('plugin.video.onemoar').getAddonInfo('path'), 'resources', 'media', 'genre_media', 'posters')

def appearance():
	theme = setting('appearance.1').lower()
	return theme

def iconFolders():
	return joinPath(xbmcaddon.Addon('plugin.video.onemoar').getAddonInfo('path'), 'resources', 'media')

def addonIcon():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ('-', '')): return joinPath(art, 'icon.png')
	return addonInfo('icon')

def addonThumb():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ('-', '')): return joinPath(art, 'poster.png')
	elif theme == '-': return 'DefaultFolder.png'
	return addonInfo('icon')

def addonPoster():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ('-', '')): return joinPath(art, 'poster.png')
	return 'DefaultVideo.png'

def addonFanart():
	user_background = setting('user_background')
	if user_background: return user_background
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ('-', '')): return joinPath(art, 'fanart.png')
	return addonInfo('fanart')

def addonBanner():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ('-', '')): return joinPath(art, 'banner.png')
	return 'DefaultVideo.png'

def addonNext():
	theme = appearance()
	art = artPath()
	if not (art is None and theme in ('-', '')): return joinPath(art, 'next.png')
	return 'DefaultVideo.png'

def skin_location():
	return transPath('special://home/addons/plugin.video.onemoar')

####################################################
# --- Custom Dialogs
####################################################
def getProgressWindow(heading='', icon=None):
	if icon == None:
		icon = addonIcon()
	from resources.lib.windows.onemoar_dialogs import ProgressOneMoar
	window = ProgressOneMoar('progress.xml', addonPath(addonId()), heading=heading, icon=icon)
	Thread(target=window.run).start()
	return window

####################################################
# --- Dialogs
####################################################
def notification(title=None, message=None, icon=None, time=3000, sound=(setting('notification.sound') == 'true')):
	if title == 'default' or title is None: title = addonName()
	if isinstance(title, int): heading = lang(title)
	else: heading = str(title)
	if isinstance(message, int): body = lang(message)
	else: body = str(message)
	if not icon or icon == 'default': icon = addonIcon()
	elif icon == 'INFO': icon = xbmcgui.NOTIFICATION_INFO
	elif icon == 'WARNING': icon = xbmcgui.NOTIFICATION_WARNING
	elif icon == 'ERROR': icon = xbmcgui.NOTIFICATION_ERROR
	return dialog.notification(heading, body, icon, time, sound)

def yesnoDialog(line1, line2, line3, heading=addonInfo('name'), nolabel='', yeslabel='', icon=None):
	message = '%s[CR]%s[CR]%s' % (line1, line2, line3)
	if setting('dialogs.useonemoardialog') == 'true':
		from resources.lib.windows.onemoar_dialogs import Confirm
		if yeslabel == '':
			myyes = lang(32179)
		else:
			myyes = yeslabel
		if nolabel == '':
			myno = lang(32180)
		else:
			myno = nolabel
		window = Confirm('confirm.xml', addonPath(addonId()), heading=heading, text=message, ok_label=myyes, cancel_label=myno, default_control=11, icon=icon)
		confirmWin = window.run()
		del window
		return confirmWin
	else:
		return dialog.yesno(heading, message, nolabel, yeslabel)

def yesnocustomDialog(line1, line2, line3, heading=addonInfo('name'), customlabel='', nolabel='', yeslabel=''):
	message = '%s[CR]%s[CR]%s' % (line1, line2, line3)
	return dialog.yesnocustom(heading, message, customlabel, nolabel, yeslabel)

def selectDialog(list, heading=addonInfo('name')):
	return dialog.select(heading, list)

def okDialog(title=None, message=None, icon=None):
	if title == 'default' or title is None: title = addonName()
	if isinstance(title, int): heading = lang(title)
	else: heading = str(title)
	if isinstance(message, int): body = lang(message)
	else: body = str(message)
	if setting('dialogs.useonemoardialog') == 'true':
		if icon == None:
			icon = addonIcon()
		from resources.lib.windows.onemoar_dialogs import OK
		window = OK('ok.xml', addonPath(addonId()), heading=heading, text=body, ok_label=lang(32179), icon=icon)
		okayWin = window.run()
		del window
		return okayWin
	else:
		return dialog.ok(heading, body)

def context(items=None, labels=None):
	if items:
		labels = [i[0] for i in items]
		choice = dialog.contextmenu(labels)
		if choice >= 0: return items[choice][1]()
		else: return False
	else: return dialog.contextmenu(labels)

def multiSelect(title=None, items=None, preselect=None):
    if items:
        labels = [i for i in items]
        if preselect == None:
            return dialog.multiselect(title, labels)
        else:
            return dialog.multiselect(title, labels, preselect=preselect)
    else: return

####################################################
# --- Built-in
####################################################
def busy():
	return execute('ActivateWindow(busydialognocancel)')

def hide():
	execute('Dialog.Close(busydialog)')
	execute('Dialog.Close(busydialognocancel)')

def closeAll():
	return execute('Dialog.Close(all,true)')

def closeOk():
	return execute('Dialog.Close(okdialog,true)')

def refresh():
	return execute('Container.Refresh')

def folderPath():
    return infoLabel('Container.FolderPath')

def queueItem():
	return execute('Action(Queue)') # seems broken in 19 for show and season level, works fine in 18

def refreshRepos():
	return execute('UpdateAddonRepos')
########################

def cancelPlayback():
	from sys import argv
	playlist.clear()
	resolve(int(argv[1]), False, item(offscreen=True))
	closeOk()

def apiLanguage(ret_name=None):
	langDict = {'Arabic Saudi Arabia': 'ar-SA', 'Bulgarian': 'bg', 'Chinese': 'zh', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Finnish': 'fi',
					'French': 'fr', 'German': 'de', 'Greek': 'el', 'Hebrew': 'he', 'Hungarian': 'hu', 'Italian': 'it', 'Japanese': 'ja', 'Korean': 'ko',
					'Norwegian': 'no', 'Polish': 'pl', 'Portuguese': 'pt', 'Romanian': 'ro', 'Russian': 'ru', 'Serbian': 'sr', 'Slovak': 'sk',
					'Slovenian': 'sl', 'Spanish': 'es', 'Swedish': 'sv', 'Thai': 'th', 'Turkish': 'tr', 'Ukrainian': 'uk'}
	trakt = ('bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'he', 'hr', 'hu', 'it', 'ja', 'ko', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sr', 'sv', 'th', 'tr', 'uk', 'zh')
	tvdb = ('en', 'sv', 'no', 'da', 'fi', 'nl', 'de', 'it', 'es', 'fr', 'pl', 'hu', 'el', 'tr', 'ru', 'he', 'ja', 'pt', 'zh', 'cs', 'sl', 'hr', 'ko')
	youtube = ('gv', 'gu', 'gd', 'ga', 'gn', 'gl', 'ty', 'tw', 'tt', 'tr', 'ts', 'tn', 'to', 'tl', 'tk', 'th', 'ti', 'tg', 'te', 'ta', 'de', 'da', 'dz', 'dv', 'qu', 'zh', 'za', 'zu',
					'wa', 'wo', 'jv', 'ja', 'ch', 'co', 'ca', 'ce', 'cy', 'cs', 'cr', 'cv', 'cu', 'ps', 'pt', 'pa', 'pi', 'pl', 'mg', 'ml', 'mn', 'mi', 'mh', 'mk', 'mt', 'ms',
					'mr', 'my', 've', 'vi', 'is', 'iu', 'it', 'vo', 'ii', 'ik', 'io', 'ia', 'ie', 'id', 'ig', 'fr', 'fy', 'fa', 'ff', 'fi', 'fj', 'fo', 'ss', 'sr', 'sq', 'sw', 'sv', 'su', 'st', 'sk',
					'si', 'so', 'sn', 'sm', 'sl', 'sc', 'sa', 'sg', 'se', 'sd', 'lg', 'lb', 'la', 'ln', 'lo', 'li', 'lv', 'lt', 'lu', 'yi', 'yo', 'el', 'eo', 'en', 'ee', 'eu', 'et', 'es', 'ru',
					'rw', 'rm', 'rn', 'ro', 'be', 'bg', 'ba', 'bm', 'bn', 'bo', 'bh', 'bi', 'br', 'bs', 'om', 'oj', 'oc', 'os', 'or', 'xh', 'hz', 'hy', 'hr', 'ht', 'hu', 'hi', 'ho',
					'ha', 'he', 'uz', 'ur', 'uk', 'ug', 'aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'as', 'ar', 'av', 'ay', 'az', 'nl', 'nn', 'no', 'na', 'nb', 'nd', 'ne', 'ng',
					'ny', 'nr', 'nv', 'ka', 'kg', 'kk', 'kj', 'ki', 'ko', 'kn', 'km', 'kl', 'ks', 'kr', 'kw', 'kv', 'ku', 'ky')
	tmdb = ('ar-SA','bg', 'cs', 'da', 'de', 'el', 'en', 'es', 'fi', 'fr', 'he', 'hr', 'hu', 'it', 'ja', 'ko', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sr', 'sv', 'th', 'tr', 'uk', 'zh')
	name = None
	name = setting('api.language')
	if not name: name = 'AUTO'
	if name[-1].isupper():
		try: name = xbmc.getLanguage(xbmc.ENGLISH_NAME).split(' ')[0]
		except: pass
	try: name = langDict[name]
	except: name = 'en'
	lang = {'trakt': name} if name in trakt else {'trakt': 'en'}
	lang['tvdb'] = name if name in tvdb else 'en'
	lang['youtube'] = name if name in youtube else 'en'
	lang['tmdb'] = name if name in tmdb else 'en'
	if ret_name:
		lang['trakt'] = [i[0] for i in iter(langDict.items()) if i[1] == lang['trakt']][0]
		lang['tvdb'] = [i[0] for i in iter(langDict.items()) if i[1] == lang['tvdb']][0]
		lang['youtube'] = [i[0] for i in iter(langDict.items()) if i[1] == lang['youtube']][0]
		lang['tmdb'] = [i[0] for i in iter(langDict.items()) if i[1] == lang['tmdb']][0]
	return lang

def mpaCountry():
# Countries with Content Rating System
	countryDict = {'Australia': 'AU', 'Austria': 'AT', 'Brazil': 'BR', 'Bulgaria': 'BG', 'Canada': 'CA', 'China': 'CN', 'Denmark': 'DK', 'Estonia': 'EE',
						'Finland': 'FI', 'France': 'FR', 'Germany': 'DE', 'Greece': 'GR', 'Hungary': 'HU', 'Hong Kong SAR China': 'HK', 'India': 'IN',
						'Indonesia': 'ID', 'Ireland': 'IE', 'Italy': 'IT', 'Japan': 'JP', 'Kazakhstan': 'KZ', 'Latvia': 'LV', 'Lithuania': 'LT', 'Malaysia': 'MY',
						'Mexico': 'MX', 'Netherlands': 'NL', 'New Zealand': 'NZ', 'Norway': 'NO', 'Philippines': 'PH', 'Poland': 'PL', 'Portugal': 'PT',
						'Romania': 'RO', 'Russia': 'RU', 'Saudi Arabia': 'SA', 'Singapore': 'SG', 'Slovakia': 'SK', 'South Africa': 'ZA', 'South Korea': 'KR',
						'Spain': 'ES', 'Sweden': 'SE', 'Switzerland': 'CH', 'Taiwan': 'TW', 'Thailand': 'TH', 'Turkey': 'TR', 'Ukraine': 'UA',
						'United Arab Emirates': 'AE', 'United Kingdom': 'GB', 'United States': 'US', 'Vietnam': 'VN'}
	return countryDict[setting('mpa.country')]

def autoTraktSubscription(tvshowtitle, year, imdb, tvdb): #---start adding TMDb to params
	from resources.lib.modules import library
	library.libtvshows().add(tvshowtitle, year, imdb, tvdb)

def getProviderHighlightColor(sourcename):
	#Real-Debrid
	#Premiumize.me
	sourcename = str(sourcename).lower()
	source = 'sources.'+ sourcename +'.color'
	colorString = setting(source)
	return colorString

def getProviderColors():
	return {
		'useproviders': True if setting('sources.highlightmethod') == '1' else False,
		'defaultcolor': setting('sources.highlight.color'),
		'realdebrid': getProviderHighlightColor('real-debrid'),
		'alldebrid': getProviderHighlightColor('alldebrid'),
		'premiumize': getProviderHighlightColor('premiumize.me'),
		'easynews': getProviderHighlightColor('easynews'),
		'plexshare': getProviderHighlightColor('plexshare'),
		'gdrive': getProviderHighlightColor('gdrive'),
		'filepursuit': getProviderHighlightColor('filepursuit')
	}

def getColorPicker(params):
	#will need to open a window here.
	from resources.lib.windows.colorpick import ColorPick
	window = ColorPick('colorpick.xml', addonPath(addonId()), current_setting=params.get('current_setting'), current_value=params.get('current_value'))
	colorPick = window.run()
	del window
	return colorPick

def showColorPicker(current_setting):
	current_value = setting(current_setting)
	chosen_color = getColorPicker({'current_setting': current_setting, 'current_value': current_value})
	if chosen_color:
		homeWindow.setProperty('onemoar.updateSettings', 'false')
		setSetting(current_setting+'.display', str('[COLOR %s]%s[/COLOR]' % (chosen_color, chosen_color)))
		homeWindow.setProperty('onemoar.updateSettings', 'true')
		setSetting(current_setting, str('%s' % (chosen_color)))

def getMenuEnabled(menu_title):
	is_enabled = setting(menu_title).strip()
	if (is_enabled == '' or is_enabled == 'false'): return False
	return True

def trigger_widget_refresh():
	# import time
	# timestr = time.strftime("%Y%m%d%H%M%S", time.gmtime())
	# homeWindow.setProperty("widgetreload", timestr)
	# homeWindow.setProperty('widgetreload-episodes', timestr)
	# homeWindow.setProperty('widgetreload-movies', timestr)
	execute('UpdateLibrary(video,/fake/path/to/force/refresh/on/home)') # make sure this is ok coupled with above

def refresh_playAction(): # for onemoar global CM play actions
	autoPlayTV = 'true' if setting('play.mode.tv') == '1' else '0'
	homeWindow.setProperty('onemoar.autoPlaytv.enabled', autoPlayTV)
	autoPlayMovie = 'true' if setting('play.mode.movie') == '1' else '0'
	homeWindow.setProperty('onemoar.autoPlayMovie.enabled', autoPlayMovie)

def refresh_libPath(): # for onemoar global CM library actions
	homeWindow.setProperty('onemoar.movieLib.path', transPath(setting('library.movie')))
	homeWindow.setProperty('onemoar.tvLib.path', transPath(setting('library.tv')))

def refresh_debugReversed(): # called from service "onSettingsChanged" to clear onemoar.log if setting to reverse has been changed
	if homeWindow.getProperty('onemoar.debug.reversed') != setting('debug.reversed'):
		homeWindow.setProperty('onemoar.debug.reversed', setting('debug.reversed'))
		execute('RunPlugin(plugin://plugin.video.onemoar/?action=tools_clearLogFile)')

def refresh_contextProperties():
	for prop in (
#		'context.onemoar.settings',
		'context.onemoar.addtoLibrary',
		'context.onemoar.addtoFavourite',
		'context.onemoar.playTrailer',
		'context.onemoar.playTrailerSelect',
		'context.onemoar.traktManager',
		'context.onemoar.clearProviders',
		'context.onemoar.clearBookmark',
		'context.onemoar.rescrape',
		'context.onemoar.playFromHere',
		'context.onemoar.autoPlay',
		'context.onemoar.sourceSelect',
		'context.onemoar.findSimilar',
		'context.onemoar.browseSeries',
		'context.onemoar.browseEpisodes'
	): homeWindow.setProperty(prop, setting(prop, 'false'))
	highlight_color = setting('highlight.color')
	if setting('context.useOneMoarContext') != 'true': prefix = ''
	else: prefix = '[B][COLOR %s]OneMoar[/COLOR][/B] - ' % highlight_color
	homeWindow.setProperty('context.onemoar.showOneMoar', prefix)
	homeWindow.setProperty('context.onemoar.highlightcolor', highlight_color)

# called only on new verison 4.04.15 in VersionIsUpdateCheck to force new color scheme ONE TIME
# to users who upgrade to this release.  new users will pick up new scheme in defaults.
# to be removed in next release.
def refresh_onemoarPalette():
	setSettingsDict({
		'highlight.color.display': '[COLOR FFE68B00]FFE68B00[/COLOR]',
		'highlight.color': 'FFE68B00',
		'dialogs.customcolor.display': '[COLOR FF37B6FF]FF37B6FF[/COLOR]',
		'dialogs.customcolor': 'FF37B6FF',
		'dialogs.titlebar.color.display': '[COLOR FF37B6FF]FF37B6FF[/COLOR]',
		'dialogs.titlebar.color': 'FF37B6FF',
		'dialogs.button.color.display': '[COLOR FF37B6FF]FF37B6FF[/COLOR]',
		'dialogs.button.color': 'FF37B6FF',
		'movie.unaired.identify.display': '[COLOR FF37B6FF]FF37B6FF[/COLOR]',
		'movie.unaired.identify': 'FF37B6FF',
		'unaired.identify.display': '[COLOR FF37B6FF]FF37B6FF[/COLOR]',
		'unaired.identify': 'FF37B6FF',
		'scraper.dialog.color.display': '[COLOR FFF5F5F5]FFF5F5F5[/COLOR]',
		'scraper.dialog.color': 'FFF5F5F5',
		'sources.highlight.color.display': '[COLOR FFE68B00]FFE68B00[/COLOR]',
		'sources.highlight.color': 'FFE68B00',
		'sources.highlightmethod': '0'
	})

# only needed for 4.04.24 to show users new Anime menu
def refresh_onemoarSimkl():
	setSettingsDict({
		'navi.movie.simkl.trendingweek': 'true',
		'navi.tv.simkl.trendingweek': 'true',
		'navi.anime': 'true'
	})

def metadataClean(metadata):
	if not metadata: return metadata
	allowed = ('genre', 'country', 'year', 'episode', 'season', 'sortepisode', 'sortseason', 'episodeguide', 'showlink',
					'top250', 'setid', 'tracknumber', 'rating', 'userrating', 'watched', 'playcount', 'overlay', 'cast', 'castandrole',
					'director', 'mpaa', 'plot', 'plotoutline', 'title', 'originaltitle', 'sorttitle', 'duration', 'studio', 'tagline', 'writer',
					'tvshowtitle', 'premiered', 'status', 'set', 'setoverview', 'tag', 'imdbnumber', 'code', 'aired', 'credits', 'lastplayed',
					'album', 'artist', 'votes', 'path', 'trailer', 'dateadded', 'mediatype', 'dbid')
	return {k: v for k, v in iter(metadata.items()) if k in allowed}

def set_info(item, meta, setUniqueIDs=None, fileNameandPath=None):
	meta_get = meta.get
	if KODI_VERSION < 20:
		if setUniqueIDs: item.setUniqueIDs(setUniqueIDs)
		item.setCast(meta_get('castandart', []) + meta_get('guest_stars', []))
		item.setInfo('video', metadataClean(meta))
		return item
	info_tag = item.getVideoInfoTag()
	try:
		if isinstance(meta_get('votes'), str): meta_votes = str(meta_get('votes')).replace(',', '')
		else: meta_votes = meta_get('votes') or 0
		if setUniqueIDs: info_tag.setUniqueIDs(setUniqueIDs)
		info_tag.setCast([xbmc.Actor(name=item['name'], role=item['role'], thumbnail=item['thumbnail']) for item in meta_get('castandart', [])])
		info_tag.setTitle(meta_get('title') or item.getLabel())
#		info_tag.setSortTitle(meta_get('sorttitle'))
#		info_tag.setSortEpisode(meta_get('sortepisode'))
#		info_tag.setSortSeason(meta_get('sortseason'))
		info_tag.setCountries(meta_get('country', []))
		info_tag.setDateAdded(meta_get('dateadded'))
		info_tag.setDirectors(meta_get('director', '').split(', '))
		info_tag.setDuration(meta_get('duration', 0))
		info_tag.setGenres(meta_get('genre', '').split(' / '))
		info_tag.setIMDBNumber(meta_get('imdb'))
		info_tag.setLastPlayed(meta_get('lastplayed'))
		info_tag.setMediaType(meta_get('mediatype'))
		info_tag.setMpaa(meta_get('mpaa'))
		info_tag.setOriginalTitle(meta_get('originaltitle'))
		info_tag.setPlot(meta_get('plot'))
		info_tag.setPlotOutline(meta_get('plot'))
		info_tag.setPlaycount(meta_get('playcount', 0))
		info_tag.setPremiered(meta_get('premiered'))
		info_tag.setRating(float(meta_get('rating') or 0.0))
		info_tag.setStudios(meta_get('studio', '').split(', '))
		info_tag.setTags(meta_get('tag', []))
		info_tag.setTagLine(meta_get('tagline'))
		info_tag.setTrailer(meta_get('trailer'))
		info_tag.setVotes(meta_votes)
		info_tag.setWriters(meta_get('writer', '').split(', '))
		info_tag.setYear(int(meta_get('year') or 0))
		if meta_get('mediatype') in ('tvshow', 'season'):
			info_tag.setTvShowTitle(meta_get('tvshowtitle'))
			info_tag.setTvShowStatus(meta_get('status'))
		if meta_get('mediatype') in ('episodes', 'episode'):
			info_tag.setTvShowTitle(meta_get('tvshowtitle'))
			info_tag.setEpisode(int(meta_get('episode')))
			info_tag.setSeason(int(meta_get('season')))
		if fileNameandPath:
			info_tag.setPath(unquote(fileNameandPath))
			info_tag.setFilenameAndPath(unquote(fileNameandPath))
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
	return item

def reload_addon():
    disable_enable_addon()
    update_local_addon()

def disable_enable_addon():
    #attempting to fix Crashy Crasherson
    jsonrpc('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": {"addonid": "plugin.video.onemoar", "enabled": false }}')
    xbmc.log('[ plugin.video.onemoar ] onemoar disabled', 1)
    jsonrpc('{"jsonrpc": "2.0", "id":1, "method": "Addons.SetAddonEnabled", "params": {"addonid": "plugin.video.onemoar", "enabled": true }}')
    xbmc.log('[ plugin.video.onemoar ] onemoar re-enabled', 1)

def addonEnabled(addon_id):
	return condVisibility('System.AddonIsEnabled(%s)' % addon_id)

def update_local_addon():
    execute('UpdateLocalAddons')

def jsonrpc_get_addons():
	try:
		results = jsonrpc('{"jsonrpc": "2.0", "id":1, "method": "Addons.GetAddons", "params": {"type": "xbmc.python.module", "properties": ["thumbnail", "name"] }}')
		results = jsloads(results)['result']['addons']
	except:
		results = []
	return results

def jsondate_to_datetime(jsondate_object, resformat, remove_time=False):
	import _strptime  # fix bug in python import
	from datetime import datetime
	import time
	if remove_time:
		try: datetime_object = datetime.strptime(jsondate_object, resformat).date()
		except TypeError: datetime_object = datetime(*(time.strptime(jsondate_object, resformat)[0:6])).date()
	else:
		try: datetime_object = datetime.strptime(jsondate_object, resformat)
		except TypeError: datetime_object = datetime(*(time.strptime(jsondate_object, resformat)[0:6]))
	return datetime_object

def checkPlayNextEpisodes():
	try:
		if setting('enable.playnext') == 'true': #we have to check for the episodes settings now
			nextEpisode = jsloads(jsonrpc('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue", "params":{"setting":"videoplayer.autoplaynextitem"}, "id":1}'))
			#selectAction = jsloads(jsonrpc('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue", "params":{"setting":"myvideos.selectaction"}, "id":1}'))
			try:
				nextEpisodeSetting = nextEpisode.get('result')['value'][0]
			except:
				nextEpisodeSetting = 0
			if nextEpisodeSetting != 2:
				jsonrpc('{"jsonrpc":"2.0", "method":"Settings.SetSettingValue", "params":{"setting":"videoplayer.autoplaynextitem", "value":[2]}, "id":1}')
			if not xbmc.getCondVisibility('Window.IsActive(settings)'):
				if setting('play.mode.tv') != '1':
					setSetting('play.mode.tv', '1')
		else:pass
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def setSettingsDict(update_dict):
	if not isinstance(update_dict, dict): return
	len_items = len(update_dict)
	if len_items > 1: homeWindow.setProperty('onemoar.updateSettings', 'false')
	for idx, (key, val) in enumerate(update_dict.items(), 1):
		if idx == len_items: homeWindow.setProperty('onemoar.updateSettings', 'true')
		try: setSetting(key, val)
		except: pass

def setContainerName(value):
	try:
		if value:
			value = unquote_plus(value)
		else:
			value = ''
		import sys
		xbmcplugin.setPluginCategory(int(sys.argv[1]), value)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()

def timeFunction(function, *args):
	from timeit import default_timer as timer
	from datetime import timedelta
	start = timer()
	try:
		exeFunction = function(*args)
	except:
		from resources.lib.modules import log_utils
		log_utils.error()
	stop = timer()
	from resources.lib.modules import log_utils
	log_utils.log('Function Timer: %s Time: %s' %(_get_function_name(function), timedelta(seconds=stop-start)),1)
	return exeFunction

def _get_function_name(function_instance):
	from re import sub as re_sub
	return re_sub(r'.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', repr(function_instance))
