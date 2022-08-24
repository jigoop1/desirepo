"""
    Deccan Delight Kodi Addon
    Copyright (C) 2016 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
from resources.lib import access
from metahandler import metahandlers

metaget = metahandlers.MetaData(tmdb_api_key=access.tk, omdb_api_key=access.ok)


def get_meta(title):
    year = ''
    name = title
    r = re.search(r'[([](\d+)[)\]]', name)
    if r:
        year = r.group(1)
    name = re.sub(r"[([].+", "", name).strip()
    meta = metaget.get_meta('movie', name=name, year=year)
    if meta.get('tmdb_id'):
        meta.pop('tmdb_id')
        imdb_id = meta.get('imdb_id')
        if imdb_id:
            meta.update({'imdbnumber': imdb_id})
        if not meta.get('trailer') and imdb_id:
            meta.update({
                'trailer': 'plugin://plugin.video.imdb.trailers/?action=play_id&imdb={0}'.format(imdb_id)
            })
        meta.pop('imdb_id')
        meta.pop('thumb_url')
        if 'imgs_prepacked' in meta.keys():
            meta.pop('imgs_prepacked')
        meta.pop('trailer_url')
    return meta
