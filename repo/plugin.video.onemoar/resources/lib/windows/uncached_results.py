# -*- coding: utf-8 -*-
"""
	OneMoar Add-on
"""

from json import dumps as jsdumps
from urllib.parse import quote_plus
from resources.lib.modules.control import joinPath, transPath, dialog, getProviderHighlightColor, addonFanart, notification, setting as getSetting, getProviderColors
from resources.lib.modules.source_utils import getFileType
from resources.lib.modules import tools
from resources.lib.windows.base import BaseDialog


class UncachedResultsXML(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2001
		self.uncached = kwargs.get('uncached')
		self.total_results = str(len(self.uncached))
		self.meta = kwargs.get('meta')
		self.defaultbg = addonFanart()
		self.colors = getProviderColors()
		self.useProviderColors = True if self.colors['useproviders'] == True else False
		self.sourceHighlightColor = self.colors['defaultcolor']
		self.realdebridHighlightColor = self.colors['realdebrid']
		self.alldebridHighlightColor = self.colors['alldebrid']
		self.premiumizeHighlightColor = self.colors['premiumize']
		self.easynewsHighlightColor = self.colors['easynews']
		self.plexHighlightColor = self.colors['plexshare']
		self.gdriveHighlightColor = self.colors['gdrive']
		self.filePursuitHighlightColor = self.colors['filepursuit']
		self.source_color = self.source_color = getSetting('sources.highlight.color')
		self.make_items()
		self.set_properties()

	def onInit(self):
		win = self.getControl(self.window_id)
		win.addItems(self.item_list)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		self.clearProperties()
		return self.selected

	def onAction(self, action):
		try:
			action_id = action.getId()# change to just "action" as the ID is already returned in that.
			if action_id in self.info_actions:
				chosen_source = self.item_list[self.get_position(self.window_id)]
				chosen_source = chosen_source.getProperty('onemoar.source_dict')
				syssource = quote_plus(chosen_source)
				self.execute_code('RunPlugin(plugin://plugin.video.onemoar/?action=sourceInfo&source=%s)' % syssource)
			if action_id in self.selection_actions:
				chosen_source = self.item_list[self.get_position(self.window_id)]
				source = chosen_source.getProperty('onemoar.source')
				if 'UNCACHED' in source:
					debrid = chosen_source.getProperty('onemoar.debrid')
					source_dict = chosen_source.getProperty('onemoar.source_dict')
					link_type = 'pack' if 'package' in source_dict else 'single'
					sysname = quote_plus(self.meta.get('title'))
					if 'tvshowtitle' in self.meta and 'season' in self.meta and 'episode' in self.meta:
						poster = self.meta.get('season_poster') or self.meta.get('poster')
						sysname += quote_plus(' S%02dE%02d' % (int(self.meta['season']), int(self.meta['episode'])))
					elif 'year' in self.meta: sysname += quote_plus(' (%s)' % self.meta['year'])
					try: new_sysname = quote_plus(chosen_source.getProperty('onemoar.name'))
					except: new_sysname = sysname
					self.execute_code('RunPlugin(plugin://plugin.video.onemoar/?action=cacheTorrent&caller=%s&type=%s&title=%s&items=%s&url=%s&source=%s&meta=%s)' %
											(debrid, link_type, sysname, quote_plus(jsdumps(self.uncached)), quote_plus(chosen_source.getProperty('onemoar.url')), quote_plus(source_dict), quote_plus(jsdumps(self.meta))))
					self.selected = (None, '')
				else:
					self.selected = (None, '')
				return self.close()
			elif action_id in self.context_actions:
				chosen_source = self.item_list[self.get_position(self.window_id)]
				source_dict = chosen_source.getProperty('onemoar.source_dict')
				cm_list = [('[B]Additional Link Info[/B]', 'sourceInfo')]

				source = chosen_source.getProperty('onemoar.source')
				if 'UNCACHED' in source:
					debrid = chosen_source.getProperty('onemoar.debrid')
					seeders = chosen_source.getProperty('onemoar.seeders')
					cm_list += [('[B]Cache to %s Cloud (seeders=%s)[/B]' % (debrid, seeders) , 'cacheToCloud')]

				chosen_cm_item = dialog.contextmenu([i[0] for i in cm_list])
				if chosen_cm_item == -1: return
				cm_action = cm_list[chosen_cm_item][1]

				if cm_action == 'sourceInfo':
					self.execute_code('RunPlugin(plugin://plugin.video.onemoar/?action=sourceInfo&source=%s)' % quote_plus(source_dict))

				if cm_action == 'cacheToCloud':
					debrid = chosen_source.getProperty('onemoar.debrid')
					source_dict = chosen_source.getProperty('onemoar.source_dict')
					link_type = 'pack' if 'package' in source_dict else 'single'
					sysname = quote_plus(self.meta.get('title'))
					if 'tvshowtitle' in self.meta and 'season' in self.meta and 'episode' in self.meta:
						poster = self.meta.get('season_poster') or self.meta.get('poster')
						sysname += quote_plus(' S%02dE%02d' % (int(self.meta['season']), int(self.meta['episode'])))
					elif 'year' in self.meta: sysname += quote_plus(' (%s)' % self.meta['year'])
					try: new_sysname = quote_plus(chosen_source.getProperty('onemoar.name'))
					except: new_sysname = sysname
					self.execute_code('RunPlugin(plugin://plugin.video.onemoar/?action=cacheTorrent&caller=%s&type=%s&title=%s&items=%s&url=%s&source=%s&meta=%s)' %
											(debrid, link_type, sysname, quote_plus(jsdumps(self.uncached)), quote_plus(chosen_source.getProperty('onemoar.url')), quote_plus(source_dict), quote_plus(jsdumps(self.meta))))
			elif action in self.closing_actions:
				self.selected = (None, '')
				self.close()
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def get_quality_iconPath(self, quality):
		try:
			return joinPath(transPath('special://home/addons/plugin.video.onemoar/resources/skins/Default/media/resolution'), '%s.png' % quality)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def get_provider1_iconPath(self, provider):
		try:
			if provider == 'premiumize.me': provider = 'premiumize'
			return joinPath(transPath('special://home/addons/plugin.video.onemoar/resources/skins/Default/media/resolution1'), '%s.png' % provider)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def get_quality1_iconPath(self, quality):
		try:
			return joinPath(transPath('special://home/addons/plugin.video.onemoar/resources/skins/Default/media/resolution1'), '%s.png' % quality)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def debrid_abv(self, debrid):
		try:
			d_dict = {'AllDebrid': 'AD', 'Premiumize.me': 'PM', 'Real-Debrid': 'RD'}
			d = d_dict[debrid]
		except:
			d = ''
		return d

	def debrid_name(self, debrid):
		try:
			d_dict = {'AllDebrid': 'AllDebrid', 'Premiumize.me': 'Premiumize', 'Real-Debrid': 'Real-Debrid'}
			d = d_dict[debrid]
		except:
			d = ''
		return d

	def make_items(self):
		def builder():
			for count, item in enumerate(self.uncached, 1):
				try:
					listitem = self.make_listitem()
					quality = item.get('quality', 'SD')
					quality_icon = self.get_quality_iconPath(quality)
					quality1_icon = self.get_quality1_iconPath(quality)
					extra_info = item.get('info')
					if self.useProviderColors == True:
						if item.get('debrid') is not None and item.get('debrid') !='':
							if str(item.get('debrid')).lower() == 'real-debrid':
								providerHighlight = self.realdebridHighlightColor
							elif str(item.get('debrid')).lower() == 'alldebrid':
								providerHighlight = self.alldebridHighlightColor
							elif str(item.get('debrid')).lower()== 'premiumize.me':
								providerHighlight = self.premiumizeHighlightColor
						else:
							if item.get('provider') == 'easynews':
								providerHighlight = self.easynewsHighlightColor
							elif str(item.get('provider')).lower() == 'plexshare':
								providerHighlight = self.plexHighlightColor
							elif str(item.get('provider')).lower() == 'gdrive':
								providerHighlight = self.gdriveHighlightColor
							elif str(item.get('provider')).lower() == 'filepursuit':
								providerHighlight = self.filePursuitHighlightColor
							else:
								providerHighlight = self.sourceHighlightColor
					else:
						providerHighlight = self.sourceHighlightColor
					size_label = str(round(item.get('size', ''), 2)) + ' GB' if item.get('size') else 'NA'
					listitem.setProperty('onemoar.source_dict', jsdumps([item]))
					listitem.setProperty('onemoar.debrid', self.debrid_name(item.get('debrid')))
					listitem.setProperty('onemoar.debridabrv', self.debrid_abv(item.get('debrid')))
					listitem.setProperty('onemoar.provider', item.get('provider').upper())
					listitem.setProperty('onemoar.source', item.get('source').upper())
					listitem.setProperty('onemoar.seeders', str(item.get('seeders')))
					listitem.setProperty('onemoar.hash', item.get('hash', 'N/A'))
					listitem.setProperty('onemoar.name', item.get('name'))
					listitem.setProperty('onemoar.quality', quality.upper())
					listitem.setProperty('onemoar.quality_icon', quality_icon)
					listitem.setProperty('onemoar.url', item.get('url'))
					listitem.setProperty('onemoar.extra_info', extra_info)
					listitem.setProperty('onemoar.size_label', size_label)
					listitem.setProperty('onemoar.count', '%02d.)' % count)
					listitem.setProperty('onemoar.providerhighlight', str(providerHighlight))
					listitem.setProperty('onemoar.quality_icon1', str(quality1_icon))
					yield listitem
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
		try:
			self.item_list = list(builder())
			self.total_results = str(len(self.item_list))
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def set_properties(self):
		if self.meta is None: return
		try:
			if 'tvshowtitle' in self.meta and 'season' in self.meta and 'episode' in self.meta: 
				self.setProperty('onemoar.seas_ep', 'S%02dE%02d' % (int(self.meta['season']), int(self.meta['episode'])))
				self.setProperty('onemoar.season', str(self.meta.get('season', '')))
				self.setProperty('onemoar.episode', str(self.meta.get('episode', '')))
			if self.meta.get('title'): self.setProperty('onemoar.title', self.meta.get('title'))
			if self.meta.get('season_poster'):	self.setProperty('onemoar.poster', self.meta.get('season_poster', ''))
			else: self.setProperty('onemoar.poster', self.meta.get('poster', ''))
			if self.meta.get('fanart'): self.setProperty('onemoar.poster1', self.meta.get('fanart', ''))
			else: self.setProperty('onemoar.poster1', 'common/fanart.jpg')
			self.setProperty('onemoar.clearlogo', self.meta.get('clearlogo', ''))
			self.setProperty('onemoar.plot', self.meta.get('plot', ''))
			if self.meta.get('premiered'):
				pdate = str(self.meta.get('premiered'))[:4]
				self.setProperty('onemoar.year', str(pdate))
			new_date = tools.convert_time(stringTime=str(self.meta.get('premiered', '')), formatInput='%Y-%m-%d', formatOutput='%m-%d-%Y', zoneFrom='utc', zoneTo='utc')
			self.setProperty('onemoar.premiered', new_date)
			if self.meta.get('mpaa'): self.setProperty('onemoar.mpaa', self.meta.get('mpaa'))
			else: self.setProperty('onemoar.mpaa', 'NA ')
			if self.meta.get('duration'):
				duration = int(self.meta.get('duration')) / 60
				self.setProperty('onemoar.duration', str(int(duration)))
			else: self.setProperty('onemoar.duration', 'NA ')
			self.setProperty('onemoar.total_results', self.total_results)
			self.setProperty('onemoar.highlight.color', self.source_color)
			self.setProperty('onemoar.dialog.color', getSetting('scraper.dialog.color'))
			if getSetting('sources.select.fanartBG') == 'true':
				self.setProperty('onemoar.fanartBG', '1')
			else:
				self.setProperty('onemoar.fanartBG', '0')
				self.setProperty('onemoar.fanartdefault', str(self.defaultbg))
			if getSetting('sources.highlightmethod') == '1':
				self.setProperty('onemoar.useprovidercolors', '1')
				self.setProperty('onemoar.realdebridcolor', self.realdebridHighlightColor)
				self.setProperty('onemoar.alldebridcolor', self.alldebridHighlightColor)
				self.setProperty('onemoar.premiumizecolor', self.premiumizeHighlightColor)
				self.setProperty('onemoar.plexcolor', self.plexHighlightColor)
				self.setProperty('onemoar.easynewscolor', self.easynewsHighlightColor)
				self.setProperty('onemoar.gdrivecolor', self.gdriveHighlightColor)
				self.setProperty('onemoar.filepursuitcolor', self.filePursuitHighlightColor)
				
				if getSetting('sources.usecoloricons') == 'true':
					self.setProperty('onemoar.usecoloricons', '1')
				else:
					self.setProperty('onemoar.usecoloricons', '0')
			else:
				self.setProperty('onemoar.useprovidercolors', '0')
				self.setProperty('onemoar.usecoloricons', '0')
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
