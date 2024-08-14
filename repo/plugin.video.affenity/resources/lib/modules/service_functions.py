# -*- coding: utf-8 -*-
from windows.base_window import FontUtils
from caches.base_cache import check_databases
from caches.settings_cache import get_setting, sync_settings
from apis.trakt_api import trakt_sync_activities
from modules import kodi_utils, settings
from modules.utils import jsondate_to_datetime, datetime_workaround

get_infolabel, run_plugin, external = kodi_utils.get_infolabel, kodi_utils.run_plugin, kodi_utils.external
pause_services_prop, xbmc_monitor, xbmc_player, userdata_path = kodi_utils.pause_services_prop, kodi_utils.xbmc_monitor, kodi_utils.xbmc_player, kodi_utils.userdata_path
get_window_id, make_directories, path_exists = kodi_utils.get_window_id, kodi_utils.make_directories, kodi_utils.path_exists
logger, run_addon, close_dialog = kodi_utils.logger, kodi_utils.run_addon, kodi_utils.close_dialog
get_property, set_property, clear_property, get_visibility = kodi_utils.get_property, kodi_utils.set_property, kodi_utils.clear_property, kodi_utils.get_visibility
kodi_refresh, current_skin_prop, notification = kodi_utils.kodi_refresh, kodi_utils.current_skin_prop, kodi_utils.notification
trakt_sync_interval, auto_start = settings.trakt_sync_interval, settings.auto_start
window_top_str, listitem_property_str = 'Window.IsTopMost(%s)', 'ListItem.Property(%s)'
movieinformation_str, contextmenu_str = 'movieinformation', 'contextmenu'
media_windows = (10000, 10025, 11121)

class InitializeDatabases:
	def run(self):
		logger('afFENity', 'InitializeDatabases Service Starting')
		check_databases()
		return logger('afFENity', 'InitializeDatabases Service Finished')

class CheckSettings:
	def run(self):
		logger('afFENity', 'CheckSettingsFile Service Starting')
		if not path_exists(userdata_path): make_directories(userdata_path)
		sync_settings()
		return logger('afFENity', 'CheckSettingsFile Service Finished')

class TraktMonitor:
	def run(self):
		logger('afFENity', 'TraktMonitor Service Starting')
		monitor, player = xbmc_monitor(), xbmc_player()
		wait_for_abort, is_playing = monitor.waitForAbort, player.isPlayingVideo
		trakt_service_string = 'TraktMonitor Service Update %s - %s'
		update_string = 'Next Update in %s minutes...'
		wait_time = 30 * 60
		first_run = True
		success_line_dict = {'success': 'Trakt Update Performed', 'no account': '(Unauthorized) Trakt Update Performed'}
		while not monitor.abortRequested():
			try:
				while is_playing() or get_property(pause_services_prop) == 'true': wait_for_abort(10)
				sync_interval, wait_time = trakt_sync_interval()
				next_update_string = update_string % sync_interval
				status = trakt_sync_activities()
				if status in ('success', 'no account'):
					logger('afFENity', trakt_service_string % ('Success', success_line_dict[status]))
					if not first_run: kodi_refresh()
				elif status == 'failed': logger('afFENity', trakt_service_string % ('Failed. Error from Trakt', next_update_string))
				else: logger('afFENity', trakt_service_string % ('Success. No Changes Needed', next_update_string))# 'not needed'
				first_run = False
			except Exception as e: logger('afFENity', trakt_service_string % ('Failed', 'The following Error Occured: %s' % str(e)))
			wait_for_abort(wait_time)
		try: del monitor
		except: pass
		try: del player
		except: pass
		return logger('afFENity', 'TraktMonitor Service Finished')

class CustomActions:
	def run(self):
		logger('afFENity', 'CustomActions Service Starting')
		monitor, player = xbmc_monitor(), xbmc_player()
		self.wait_for_abort, abort_requested, is_playing = monitor.waitForAbort, monitor.abortRequested, player.isPlayingVideo
		while not abort_requested():
			context_visible, info_visible, run_custom = False, False, False
			while not any([context_visible, info_visible]) and not abort_requested():
				if not get_setting('affenity.auto_custom_actions') == 'true': self.wait_for_abort(5); continue
				if not get_window_id() in media_windows: self.wait_for_abort(2); continue
				if get_property(pause_services_prop) == 'true' or is_playing(): self.wait_for_abort(2); continue
				context_menu_params = get_infolabel(listitem_property_str % 'affenity.options_params')
				extras_params = get_infolabel(listitem_property_str % 'affenity.extras_params')
				if context_menu_params or extras_params:
					run_custom = True
					self.wait_for_abort(0.25)
				else:
					run_custom = False
					self.wait_for_abort(1); continue
				context_visible, info_visible = get_visibility(window_top_str % contextmenu_str), get_visibility(window_top_str % movieinformation_str)
			try:
				if run_custom and (context_menu_params or extras_params):
					if info_visible:
						if extras_params: self.run_custom_action(extras_params, movieinformation_str)
					elif context_menu_params: self.run_custom_action(context_menu_params, contextmenu_str)
				else: self.wait_for_abort(1)
			except: self.wait_for_abort(2)
		try: del monitor
		except: pass
		try: del player
		except: pass
		return logger('afFENity', 'CustomActions Service Finished')

	def run_custom_action(self, action, window):
		close_dialog(window, True)
		run_plugin(action)

class CustomFonts:
	def run(self):
		logger('afFENity', 'CustomFonts Service Starting')
		monitor, player = xbmc_monitor(), xbmc_player()
		wait_for_abort, is_playing = monitor.waitForAbort, player.isPlayingVideo
		clear_property(current_skin_prop)
		font_utils = FontUtils()
		while not monitor.abortRequested():
			font_utils.execute_custom_fonts()
			if get_property(pause_services_prop) == 'true' or is_playing(): sleep = 20
			else: sleep = 10
			wait_for_abort(sleep)
		try: del monitor
		except: pass
		try: del player
		except: pass
		return logger('afFENity', 'CustomFonts Service Finished')

class AutoRun:
	def run(self):
		logger('afFENity', 'AutoRun Service Starting')
		if auto_start():
			try: run_addon()
			except: return logger('afFENity', 'AutoRun Service Failed')
		return logger('afFENity', 'AutoRun Service Finished')

class OnNotificationActions:
	def run(self, sender, method, data):
		if sender == 'xbmc':
			if method in ('GUI.OnScreensaverActivated', 'System.OnSleep'):
				set_property(pause_services_prop, 'true')
				logger('OnNotificationActions', 'PAUSING afFENity Services Due to Device Sleep')
			elif method in ('GUI.OnScreensaverDeactivated', 'System.OnWake'):
				clear_property(pause_services_prop)
				logger('OnNotificationActions', 'UNPAUSING afFENity Services Due to Device Awake')

class ScraperSettings:
	def run(self):
		from fenom.settings import Settings
		from fenom.undesirables import Undesirables
		logger('Fenom', 'ScaperSettings Service Starting')
		Settings().check_database()
		Undesirables().check_database()
		logger('Fenom', 'ScaperSettings Service Finished')
