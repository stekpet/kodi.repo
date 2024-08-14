# -*- coding: utf-8 -*-
from caches.favorites_cache import favorites
from modules.utils import sort_for_article
# from modules.kodi_utils import logger

def get_favorites(media_type, page_no):
	data = favorites.get_favorites(media_type)
	data = sort_for_article(data, 'title')
	return [{'media_id': i['tmdb_id'], 'title': i['title']} for i in data]
