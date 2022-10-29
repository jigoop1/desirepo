"""
apnetv deccandelight plugin
Copyright (C) 2018 Gujal

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


class apnetv(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://apnetv.to/Hindi-Serials'
        self.icon = self.ipath + 'apnetv.png'
        self.videos = []

    def get_menu(self):
        mlist = {}
        html = client.request(self.bu)
        mlink = SoupStrainer('ul', {'class': 'channel-list-tab'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.findAll('li', {'class': True})
        ino = 1
        for item in items:
            mlist['{:02d}{}'.format(ino, item.a.span.text)] = item.a.span.text
            ino += 1
        return (mlist, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []
        html = client.request(self.bu)
        mlink = SoupStrainer('ul', {'class': 'channel-list-tab'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.findAll('li', {'class': True})
        for item in items:
            if item.a.span.text == iurl:
                serials = item.find_all('li')
                thumb = item.figure.img.get('src')
                for serial in serials:
                    title = self.unescape(serial.text).strip()
                    url = serial.find('a')['href']
                    t = url.split('/')
                    t.insert(4, 'episodes')
                    url = '/'.join(t)
                    shows.append((title, thumb, url))
                break

        return (shows, 7)

    def get_items(self, iurl):
        episodes = []
        html = client.request(iurl)
        mlink = SoupStrainer('ul', {'class': 'ul'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.findAll('li')
        for item in items:
            title = self.unescape(item.h2.text + ' - ' + item.find('div', {'class': 'date'}).text.strip())
            url = item.find('a')['href']
            if item.find('img'):
                thumb = item.find('img')['src']
            else:
                thumb = self.icon
            episodes.append((title, thumb, url))

        plink = SoupStrainer('div', {'class': 'pagination_btns'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        if 'Next' in str(Paginator):
            nlinks = Paginator.findAll('a', {'class': 'prev_next_btns'})
            iurl = nlinks[-2].get('href')
            currpg = Paginator.find('a', {'class': re.compile('^page_active')}).text
            lastpg = nlinks[-1].get('href').split('/')[-1]
            title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
            episodes.append((title, self.nicon, iurl))

        return (episodes, 8)

    def get_videos(self, iurl):
        def process_item(item):
            vid_link = item.find('a')['href'] + '|Referer=' + self.bu
            self.resolve_media(vid_link, self.videos)

        html = client.request(iurl)
        mlink = SoupStrainer('div', {'class': 'bottom_episode_list'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.findAll('li')
        threads = []
        for item in items:
            threads.append(self.Thread(process_item, item))

        [i.start() for i in threads]
        [i.join() for i in threads]

        return sorted(self.videos)
