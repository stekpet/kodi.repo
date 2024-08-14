"""
	Fenomscrapers Module
"""

import sqlite3 as db
from fenom.control import existsPath, dataPath, makeFile, cacheFile, lang


class Settings():
	def get_all(self):
		self.make_database_objects()
		results = self.dbcur.execute('SELECT * FROM settings')
		return self.process_keywords(results)

	def set_many(self, undesirables):
		self.make_database_objects()
		self.dbcur.executemany('INSERT OR REPLACE INTO settings VALUES (?, ?, ?)', undesirables)
		self.dbcon.commit()
		self.dbcon.close()

	def remove_many(self, undesirables):
		self.make_database_objects()
		self.dbcur.executemany('DELETE FROM settings WHERE id = ?', undesirables)
		self.dbcon.commit()
		self.dbcon.close()

	def make_connection(self):
		self.dbcon = db.connect(cacheFile, timeout=60)

	def make_cursor(self):
		self.dbcur = self.dbcon.cursor()
		self.dbcur.execute('''PRAGMA synchronous = OFF''')
		self.dbcur.execute('''PRAGMA journal_mode = OFF''')

	def make_database_objects(self):
		self.make_connection()
		self.make_cursor()

	def check_database(self):
		if not existsPath(dataPath): makeFile(dataPath)
		self.make_database_objects()
		try:
			self.dbcur.execute('SELECT id FROM settings WHERE value = ?', ('true',)).fetchone()[0]
			self.dbcon.close()
			return True
		except:
			self.dbcur.execute('CREATE TABLE IF NOT EXISTS settings (id TEXT NOT NULL, value TEXT NOT NULL, label TEXT, UNIQUE(id))')
			self.set_defaults()
			return False

	def set_defaults(self):
		from fenom.control import SETTINGS
		self.set_many(SETTINGS)

	def process_keywords(self, results):
		keywords = results.fetchall()
		self.dbcon.close()
		return keywords

def filtersSelect():
	from fenom.control import multiselectDialog
	from fenom.control import SETTINGS, make_settings_dict
	settings_cache = Settings()
	settings_cache.check_database()
	chosen = [i for i in settings_cache.get_all() if i[0].startswith('filter.')]
	try: preselect = [p for p, i in enumerate(chosen) if i[1] == 'true']
	except: preselect = [p for p, i in enumerate(SETTINGS) if i[0].startswith('filter.') and i[1] == 'true']
	choices = multiselectDialog([i[2] for i in chosen], preselect=preselect, heading='Select Providers')
	if choices is None: return
	new_settings = [(i[0], 'true' if p in choices else 'false', i[2]) for p, i in enumerate(chosen)]
	settings_cache.set_many(new_settings)
	make_settings_dict()

def debugSelect():
	from fenom.control import multiselectDialog
	from fenom.control import SETTINGS, make_settings_dict
	settings_cache = Settings()
	settings_cache.check_database()
	chosen = [i for i in settings_cache.get_all() if i[0].startswith('debug.')]
	try: preselect = [p for p, i in enumerate(chosen) if i[1] == 'true']
	except: preselect = [p for p, i in enumerate(SETTINGS) if i[0].startswith('debug.') and i[1] == 'true']
	choices = multiselectDialog([i[2] for i in chosen], preselect=preselect, heading='Select Providers')
	if choices is None: return
	new_settings = [(i[0], 'true' if p in choices else 'false', i[2]) for p, i in enumerate(chosen)]
	settings_cache.set_many(new_settings)
	make_settings_dict()

def providersSelect():
	from fenom.control import multiselectDialog
	from fenom.control import SETTINGS, make_settings_dict
	settings_cache = Settings()
	settings_cache.check_database()
	chosen = [i for i in settings_cache.get_all() if i[0].startswith('provider.')]
	try: preselect = [p for p, i in enumerate(chosen) if i[1] == 'true']
	except: preselect = [p for p, i in enumerate(SETTINGS) if i[0].startswith('provider.') and i[1] == 'true']
	choices = multiselectDialog([i[2] for i in chosen], preselect=preselect, heading='Select Providers')
	if not choices: return
	new_settings = [(i[0], 'true' if p in choices else 'false', i[2]) for p, i in enumerate(chosen)]
	settings_cache.set_many(new_settings)
	make_settings_dict()

