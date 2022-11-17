"""
DeccanDelight scraper plugin
Copyright (C) 2019 gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper
from six.moves import urllib_parse


class todaypk(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://ww3.1todaypk.net/category/'
        self.icon = self.ipath + 'todaypk.png'
        self.list = {'01Tamil Movies': 'tamil',
                     '02Telugu Movies': 'telugu',
                     '03Malayalam Movies': 'malayalam',
                     '04Bollywood Movies': 'bollywood',
                     '05Hollywood Movies': 'hollywood',
                     '06Dubbed Movies': 'dubbed',
                     '07Punjabi Movies': self.bu[:-9] + 'language/punjabiMMMM7',
                     '08Bengali Movies': self.bu[:-9] + 'language/bengaliMMMM7',
                     '09Urdu Movies': self.bu[:-9] + 'language/urduMMMM7',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + 'search?s=MMMM7'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of categories.
        """
        cats = []
        page = client.request(self.bu[:-9])
        mlink = SoupStrainer('div', {'class': 'caja1'})
        mdiv = BeautifulSoup(page, "html.parser", parse_only=mlink)
        submenus = mdiv.find_all('li', {'class': 'menu-item-has-children'})

        for submenu in submenus:
            if iurl in submenu.a.text.lower():
                break
        items = submenu.find_all('li')
        for item in items:
            title = item.text
            url = item.find('a')['href']
            url = url if url.startswith('http') else self.bu[:-9] + url
            cats.append((title, self.icon, url))

        return (cats, 7)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Today PK')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text
        mlink = SoupStrainer('div', {'class': 'sbox'})
        html = client.request(url)
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'paginado1'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': 'fitem'})
        for item in items:
            title = item.find_all('b')[-1].text
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'Next' in str(Paginator):
            purl = Paginator.find("a", text=re.compile('^Next'))['href']
            purl = purl if purl.startswith('http') else self.bu[:-10] + purl
            currpg = Paginator.find('a', {'class': 'current'}).text
            pgtxt = currpg
            lurl = Paginator.find("a", text=re.compile('^Last'))
            if lurl:
                pgtxt = '{0} of {1}'.format(currpg, lurl.get('href').split('/')[-1])
            title = 'Next Page... (Currently in Page {0})'.format(pgtxt)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = client.request(url, headers=self.hdr)
        mlink = SoupStrainer('div', {'class': 'column ak_middle'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        links = videoclass.find_all('span', {'class': 'a'})
        try:
            for link in links:
                vidurl = link.find('a')['href']
                vidurl = vidurl if vidurl.startswith('http') else 'https:' + vidurl
                self.resolve_media(vidurl, videos)
        except:
            pass

        return videos
