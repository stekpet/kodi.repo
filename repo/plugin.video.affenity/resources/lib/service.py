# -*- coding: utf-8 -*-
from modules import service_functions
from modules.kodi_utils import Thread, xbmc_monitor, logger

on_notification_actions = service_functions.OnNotificationActions()

class afFENityMonitor(xbmc_monitor):
	def __init__ (self):
		xbmc_monitor.__init__(self)
		self.startUpServices()

	def startUpServices(self):
		service_functions.InitializeDatabases().run()
		service_functions.CheckSettings().run()
		service_functions.ScraperSettings().run()
		Thread(target=service_functions.TraktMonitor().run).start()
		Thread(target=service_functions.CustomActions().run).start()
		Thread(target=service_functions.CustomFonts().run).start()
		service_functions.AutoRun().run()

	def onNotification(self, sender, method, data):
		on_notification_actions.run(sender, method, data)

logger('afFENity', 'Main Monitor Service Starting')
logger('afFENity', 'Settings Monitor Service Starting')
afFENityMonitor().waitForAbort()
logger('afFENity', 'Settings Monitor Service Finished')
logger('afFENity', 'Main Monitor Service Finished')