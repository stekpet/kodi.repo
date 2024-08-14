# -*- coding: utf-8 -*-
"""
	OneMoar Add-on (added by OneMoar Dev 12/23/22)
"""

import re
import requests
from requests.adapters import HTTPAdapter
from threading import Thread
from urllib3.util.retry import Retry
from resources.lib.database import cache
from resources.lib.modules import control

getLS = control.lang
getSetting = control.setting
simkl_icon = control.joinPath(control.artPath(), 'simkl.png')
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
session.mount('https://api.simkl.com', HTTPAdapter(max_retries=retries, pool_maxsize=100))


class SIMKL:
	def __init__(self):
		self.highlightColor = control.setting('highlight.color')
		self.simkl_hours = int(getSetting('cache.simkl'))
		self.API_key = getSetting('simkl.apikey')

	def get_request(self, url):
		params = {'client_id': self.API_key} if self.API_key else None
		try:
			try: response = session.get(url, params=params, timeout=20)
			except requests.exceptions.SSLError:
				response = session.get(url, verify=False)
		except requests.exceptions.ConnectionError:
			control.notification(message=40349)
			from resources.lib.modules import log_utils
			log_utils.error()
			return None
		if response.status_code in (200, 201): return response.json()
		elif response.status_code == 404:
			from resources.lib.modules import log_utils
			log_utils.log('Simkl get_request() failed: (404:NOT FOUND) - URL: %s' % url, level=log_utils.LOGDEBUG)
			return '404:NOT FOUND'
		elif 'Retry-After' in response.headers: # API REQUESTS ARE BEING THROTTLED, INTRODUCE WAIT TIME (TMDb removed rate-limit on 12-6-20)
			throttleTime = response.headers['Retry-After']
			control.notification(message='SIMKL Throttling Applied, Sleeping for %s seconds' % throttleTime)
			control.sleep((int(throttleTime) + 1) * 1000)
			return self.get_request(url)
		else:
			from resources.lib.modules import log_utils
			log_utils.log('SIMKL get_request() failed: URL: %s\n                       msg : SIMKL Response: %s' % (url, response.text), __name__, log_utils.LOGDEBUG)
			return None

	def simkl_list(self, url):
		try:
			result = cache.get(self.get_request, self.simkl_hours, url)
			if result is None: return
			items = result
		except: return
		collector = {}
		self.list = [] ; sortList = []
		threads = [] ; threads_append = threads.append
		for i in items:
			threads_append(Thread(target=self.summary, args=(i['ids']['simkl_id'], collector)))
			sortList.append(i['ids']['simkl_id'])

		[i.start() for i in threads]
		[i.join() for i in threads]
		for i in sortList:
			try:
				item = collector[i]
				values = {}
				values['tmdb'] = str(item.get('ids').get('tmdb')) if item.get('ids').get('tmdb') else ''
				values['imdb'] = str(item.get('ids').get('imdb')) if item.get('ids').get('imdb') else ''
				values['title'] = item.get('en_title') if item.get('en_title') else item.get('title')
				values['year'] = item.get('year')
				self.list.append(values)
			except: pass
		return self.list

	def summary(self, sid, collector):
		try:
			url = 'https://api.simkl.com/anime/%s?extended=full' % sid
			result = cache.get(self.get_request, self.simkl_hours, url)
			if result is None: return
			collector[sid] = result
		except: return

	def auth(self, fromSettings=0):
		pass

	def reset_authorization(self, fromSettings=0):
		pass
