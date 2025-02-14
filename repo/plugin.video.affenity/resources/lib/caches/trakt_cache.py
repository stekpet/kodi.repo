# -*- coding: utf-8 -*-
from caches.base_cache import connect_database
from modules.kodi_utils import sleep, confirm_dialog, close_all_dialog, Thread
# from modules.kodi_utils import logger

SELECT = 'SELECT id FROM trakt_data'
DELETE = 'DELETE FROM trakt_data WHERE id=?'
DELETE_LIKE = 'DELETE FROM trakt_data WHERE id LIKE "%s"'
WATCHED_INSERT = 'INSERT OR IGNORE INTO watched VALUES (?, ?, ?, ?, ?, ?)'
WATCHED_DELETE = 'DELETE FROM watched WHERE db_type = ?'
PROGRESS_INSERT = 'INSERT OR IGNORE INTO progress VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
PROGRESS_DELETE = 'DELETE FROM progress WHERE db_type = ?'
BASE_DELETE = 'DELETE FROM %s'
TC_BASE_GET = 'SELECT data FROM trakt_data WHERE id = ?'
TC_BASE_SET = 'INSERT OR REPLACE INTO trakt_data (id, data) VALUES (?, ?)'
TC_BASE_DELETE = 'DELETE FROM trakt_data WHERE id = ?'
timeout = 60

class TraktWatched:
	def __init__(self):
		self.dbcon = connect_database('trakt_db')

	def set_bulk_movie_watched(self, insert_list):
		self._delete(WATCHED_DELETE, ('movie',))
		self._executemany(WATCHED_INSERT, insert_list)

	def set_bulk_tvshow_watched(self, insert_list):
		self._delete(WATCHED_DELETE, ('episode',))
		self._executemany(WATCHED_INSERT, insert_list)

	def set_bulk_movie_progress(self, insert_list):
		self._delete(PROGRESS_DELETE, ('movie',))
		self._executemany(PROGRESS_INSERT, insert_list)

	def set_bulk_tvshow_progress(self, insert_list):
		self._delete(PROGRESS_DELETE, ('episode',))
		self._executemany(PROGRESS_INSERT, insert_list)

	def _executemany(self, command, insert_list):
		self.dbcon.executemany(command, insert_list)

	def _delete(self, command, args):
		self.dbcon.execute(command, args)
		self.dbcon.execute('VACUUM')

trakt_watched = TraktWatched()

class TraktCache:
	def __init__(self):
		self.dbcon = connect_database('trakt_db')

	def get(self, string):
		result = None
		try:
			cache_data = self.dbcon.execute(TC_BASE_GET, (string,)).fetchone()
			if cache_data: result = eval(cache_data[0])
		except: pass
		return result

	def set(self, string, data):
		try: self.dbcon.execute(TC_BASE_SET, (string, repr(data)))
		except: return None

	def delete(self, string):
		try:
			self.dbcon.execute(TC_BASE_DELETE, (string,))
		except: pass

_cache = TraktCache()

def cache_trakt_object(function, string, url):
	cache = _cache.get(string)
	if cache: return cache
	result = function(url)
	_cache.set(string, result)
	return result

def reset_activity(latest_activities):
	string = 'trakt_get_activity'
	cached_data = None
	try:
		dbcon = _cache.dbcon
		cached_data = dbcon.execute(TC_BASE_GET, (string,)).fetchone()
		if cached_data: cached_data = eval(cached_data[0])
		else: cached_data = default_activities()
		dbcon.execute(DELETE, (string,))
		_cache.set(string, latest_activities)
	except: pass
	return cached_data

def clear_trakt_hidden_data(list_type):
	string = 'trakt_hidden_items_%s' % list_type
	try: _cache.dbcon.execute(DELETE, (string,))
	except: pass

def clear_trakt_collection_watchlist_data(list_type, media_type):
	if media_type == 'movies': media_type = 'movie' 
	if media_type in ('tvshows', 'shows'): media_type = 'tvshow' 
	string = 'trakt_%s_%s' % (list_type, media_type)
	if media_type == 'movie': clear_trakt_movie_sets()
	try: _cache.dbcon.execute(DELETE, (string,))
	except: pass

def clear_trakt_list_contents_data(list_type):
	string = 'trakt_list_contents_' + list_type + '_%'
	try: _cache.dbcon.execute(DELETE_LIKE % string)
	except: pass

def clear_trakt_list_data(list_type):
	string = 'trakt_%s' % list_type
	try: _cache.dbcon.execute(DELETE, (string,))
	except: pass

def clear_trakt_calendar():
	try: _cache.dbcon.execute(DELETE_LIKE % 'trakt_get_my_calendar_%')
	except: return

def clear_trakt_recommendations(media_type):
	string = 'trakt_recommendations_%s' % (media_type)
	try: _cache.dbcon.execute(DELETE, (string,))
	except: pass

def clear_trakt_movie_sets():
	string = 'trakt_movie_sets'
	try: _cache.dbcon.execute(DELETE, (string,))
	except: pass

def clear_all_trakt_cache_data(silent=False, refresh=True):
	try:
		start = silent or confirm_dialog()
		if not start: return False
		dbcon = _cache.dbcon
		for table in ('trakt_data', 'progress', 'watched', 'watched_status'): dbcon.execute(BASE_DELETE % table)
		dbcon.execute('VACUUM')
		if refresh:
			from apis.trakt_api import trakt_sync_activities
			Thread(target=trakt_sync_activities).start()
		return True
	except: return False

def default_activities():
	return {
			'all': '2020-01-01T00:00:01.000Z',
			'movies':
				{
				'watched_at': '2020-01-01T00:00:01.000Z',
				'collected_at': '2020-01-01T00:00:01.000Z',
				'rated_at': '2020-01-01T00:00:01.000Z',
				'watchlisted_at': '2020-01-01T00:00:01.000Z',
				'recommendations_at': '2020-01-01T00:00:01.000Z',
				'commented_at': '2020-01-01T00:00:01.000Z',
				'paused_at': '2020-01-01T00:00:01.000Z',
				'hidden_at': '2020-01-01T00:00:01.000Z'
				},
			'episodes':
				{
				'watched_at': '2020-01-01T00:00:01.000Z',
				'collected_at': '2020-01-01T00:00:01.000Z',
				'rated_at': '2020-01-01T00:00:01.000Z',
				'watchlisted_at': '2020-01-01T00:00:01.000Z',
				'commented_at': '2020-01-01T00:00:01.000Z',
				'paused_at': '2020-01-01T00:00:01.000Z'
				},
			'shows':
				{
				'rated_at': '2020-01-01T00:00:01.000Z',
				'watchlisted_at': '2020-01-01T00:00:01.000Z',
				'recommendations_at': '2020-01-01T00:00:01.000Z',
				'commented_at': '2020-01-01T00:00:01.000Z', 
				'hidden_at': '2020-01-01T00:00:01.000Z'
				},
			'seasons':
				{
				'rated_at': '2020-01-01T00:00:01.000Z',
				'watchlisted_at': '2020-01-01T00:00:01.000Z',
				'commented_at': '2020-01-01T00:00:01.000Z',
				'hidden_at': '2020-01-01T00:00:01.000Z'
				},
			'comments':
				{
				'liked_at': '2020-01-01T00:00:01.000Z'
				},
			'lists':
				{
				'liked_at': '2020-01-01T00:00:01.000Z',
				'updated_at': '2020-01-01T00:00:01.000Z',
				'commented_at': '2020-01-01T00:00:01.000Z'
				},
			'watchlist':
				{
				'updated_at': '2020-01-01T00:00:01.000Z'
				},
			'recommendations':
				{
				'updated_at': '2020-01-01T00:00:01.000Z'
				},
			'account':
				{
				'settings_at': '2020-01-01T00:00:01.000Z',
				'followed_at': '2020-01-01T00:00:01.000Z',
				'following_at': '2020-01-01T00:00:01.000Z',
				'pending_at': '2020-01-01T00:00:01.000Z'
				}
			}
	