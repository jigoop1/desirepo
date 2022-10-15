# -*- coding: utf-8 -*-
'''
DeccanDelight scraper plugin
Copyright (C) 2022 gujal

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
'''

import base64
import re

from bs4 import BeautifulSoup, SoupStrainer
from resources.lib import client
from resources.lib.base import Scraper


class dtelugu(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'http://desitelugu.net/category/'
        self.icon = self.ipath + 'dtelugu.png'
        self.list = {'01TV Serials': self.bu + 'daily-serials/',
                     '02TV Shows': self.bu + 'shows/'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []
        html = client.request(iurl)
        # mlink = SoupStrainer('div', {'class': 'td-ss-main-content'})
        # plink = SoupStrainer('div', {'class': 'page-nav'})
        soup = BeautifulSoup(html, "html5lib")
        mdiv = soup.find('div', {'class': 'td-ss-main-content'})
        pdiv = soup.find('div', {'class': 'page-nav'})
        items = mdiv.find_all('div', {'class': 'td_module_6'})
        for item in items:
            idiv, ldiv = item.select("img,h3")
            title = ldiv.text
            title = title.encode('utf8') if self.PY2 else title
            if ' Daily Serial' in title:
                title = title.split(' Daily Serial')[0]
            if ' –' in title:
                title = title.split(' –')[0]
            url = ldiv.a.get('href')
            icon = idiv.get('src')
            icon = re.sub(r'-\d+x\d+\.', '.', icon)
            shows.append((title, icon, url))

        if 'class="td-icon-menu-right"' in str(pdiv):
            purl = pdiv.find_all('a')[-1].get('href')
            pgtxt = pdiv.find('span', {'class': 'pages'}).text
            shows.append(('Next Page...(Currently in {0})'.format(pgtxt), self.nicon, purl))

        return (shows, 7)

    def get_items(self, url):
        movies = []
        html = client.request(url)
        html = re.sub(r'<br\s*/>', '</p><p>', html)
        mlink = SoupStrainer('div', {'class': 'td-post-content'})
        ilink = SoupStrainer('div', {'class': 'td-post-featured-image'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        idiv = BeautifulSoup(html, "html.parser", parse_only=ilink)

        try:
            thumb = idiv.find('img')['src']
            thumb = re.sub(r'-\d+x\d+\.', '.', thumb)
        except:
            thumb = self.icon

        items = mdiv.find_all('p')
        for item in items:
            try:
                if 'href' in str(item):
                    itxt = item.contents
                    ep = re.search(r'(E\d+)', itxt[0])
                    itxt = re.search(r'(\d+[a-zA-Z ]+)', itxt[-1])
                    if itxt:
                        ep = '[COLOR lime]{}[/COLOR] - '.format(ep.group(1)) if ep else ''
                        title = '{}[COLOR yellow]{}[/COLOR]'.format(ep, itxt.group(1))
                        self.log(title)
                        item = str(item).encode('base64') if self.PY2 else base64.b64encode(str(item).encode('utf-8'))
                        movies.append((title, thumb, item))
            except:
                continue

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        html = base64.b64decode(url).decode('utf8')
        links = re.findall('(<a.+?a>)', html, re.DOTALL)
        for link in links:
            vidurl = re.findall('href="([^"]+)', link)[0]
            vidtxt = re.findall('">([^<]+)', link)[0]
            if 'source=vidfy' in vidurl:
                url = 'http://vidfy.me/player.php?vid=' + re.findall(r'\?url=([^&]+)', vidurl)[0]
                html = client.request(url, referer='http://desitelugu.net/')
                if 'video is not available' not in html:
                    vidurl = re.findall('<source.+?src="([^"]+)', html)
                    if not vidurl:
                        vidurl = re.findall(r'src:\s*"([^"]+)', html)
                    if vidurl:
                        vidurl = vidurl[0] + '|Referer={}&User-Agent={}'.format(url, self.hdr['User-Agent'])
                        videos.append(('vidfy | {}'.format(vidtxt), vidurl))
            elif 'source=youtube' in vidurl:
                vidurl = 'https://www.youtube.com/embed/' + re.findall(r'\?url=([^&]+)', vidurl)[0]
                self.resolve_media(vidurl, videos, vidtxt)

        return videos
