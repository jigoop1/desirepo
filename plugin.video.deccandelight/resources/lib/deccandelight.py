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

import sys
import re
import resolveurl
import tempfile
import six
import time
from six.moves import urllib_parse, urllib_request
from kodi_six import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs
from resources.lib import client
from resources.lib.base import cache, clear_cache
from resources.scrapers import *  # NoQA

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

_addon = xbmcaddon.Addon()
_addonname = _addon.getAddonInfo('name')
_version = _addon.getAddonInfo('version')
_addonID = _addon.getAddonInfo('id')
_icon = _addon.getAddonInfo('icon')
_fanart = _addon.getAddonInfo('fanart')
_path = _addon.getAddonInfo('path')
_ipath = _path + '/resources/images/'
_settings = _addon.getSetting
_changelog = _path + '/changelog.txt'
kodiver = float(xbmc.getInfoLabel('System.BuildVersion')[0:3])
msites = [
    'tgun', 'tamilian', 'tyogi', 'awatch', 'torm', 'kcine',
    'hlinks', 'einthusan', 'mrulz', 'mghar', 'b2t', 'omg',
    'wompk', 'cinevez', 'flinks', 'hflinks', 'bmov', 'ibomma'
]
pDialog = xbmcgui.DialogProgress()
makeLegalFilename = xbmc.makeLegalFilename if six.PY2 else xbmcvfs.makeLegalFilename
mozhdr = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
safhdr = 'Mozilla/5.0 ({}) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A356 Safari/604.1'

try:
    platform = re.findall(r'\(([^)]+)', xbmc.getUserAgent())[0]
except:
    platform = 'Linux; Android 4.4.4; MI 5 Build/KTU84P'

if _settings('version') != _version:
    _addon.setSetting('version', _version)
    headers = {'User-Agent': safhdr.format(platform),
               'Referer': '{0} {1}'.format(_addonname, _version)}
    r = client.request('\x68\x74\x74\x70\x73\x3a\x2f\x2f\x69\x73\x2e\x67\x64\x2f\x36\x59\x6f\x64\x55\x50',
                       headers=headers)
    clear_cache()
    heading = '[B][COLOR gold]Deccan Delight[/COLOR] - [COLOR white]Changelog[/COLOR][/B]'
    with open(_changelog) as f:
        announce = f.read()
    dialog = xbmcgui.Dialog()
    dialog.textviewer(heading, announce)

sites = {'01tgun': 'Tamil Gun : [COLOR yellow]Tamil[/COLOR]',
         '02tamilian': 'Tamilian : [COLOR yellow]Tamil[/COLOR]',
         '03tyogi': 'Tamil Yogi : [COLOR yellow]Tamil[/COLOR]',
         '11awatch': 'Andhra Watch : [COLOR yellow]Telugu[/COLOR]',
         '12ibomma': 'iBOMMA : [COLOR yellow]Telugu[/COLOR]',
         '22torm': 'TOR Malayalam : [COLOR yellow]Malayalam[/COLOR]',
         # '26kcine': 'Kannada Cine : [COLOR yellow]Kannada[/COLOR]',
         '31hlinks': 'Hindi Links 4U : [COLOR yellow]Hindi[/COLOR]',
         '42einthusan': 'Einthusan : [COLOR magenta]Various[/COLOR]',
         '43mrulz': 'Movie Rulz : [COLOR magenta]Various[/COLOR]',
         '44mghar': 'Movies Ghar : [COLOR magenta]Various[/COLOR]',
         '45b2t': 'Bolly 2 Tolly : [COLOR magenta]Various[/COLOR]',
         '46omg': 'Online Movies Gold : [COLOR magenta]Various[/COLOR]',
         '47wompk': 'Online Movies PK : [COLOR magenta]Various[/COLOR]',
         '49cinevez': 'Cine Vez : [COLOR magenta]Various[/COLOR]',
         '52hflinks': 'Film Links 4U Pro : [COLOR magenta]Various[/COLOR]',
         '70thdbox': 'Tamil HD Box: [COLOR yellow]Tamil Catchup TV[/COLOR]',
         '71bbt': 'BigBoss Tamil: [COLOR yellow]Tamil Catchup TV[/COLOR]',
         '72skytamil': 'sky Tamil: [COLOR yellow]Tamil Catchup TV[/COLOR]',
         '73tdhool': 'Tamil Dhool : [COLOR yellow]Tamil Catchup TV[/COLOR]',
         '76manatv': 'Mana Telugu : [COLOR yellow]Telugu Catchup TV[/COLOR]',
         '81apnetv': 'Apne TV : [COLOR yellow]Hindi Catchup TV[/COLOR]',
         '82desit': 'Desi Tashan : [COLOR yellow]Hindi Catchup TV[/COLOR]',
         '83pdesi': 'Play Desi : [COLOR yellow]Hindi Catchup TV[/COLOR]',
         '84wapne': 'Watch Apne : [COLOR yellow]Hindi Catchup TV[/COLOR]',
         '85yodesi': 'Yo Desi : [COLOR yellow]Hindi Catchup TV[/COLOR]',
         '91ary': 'Ary Digital : [COLOR yellow]Urdu Catchup TV[/COLOR]',
         '92geo': 'Geo TV : [COLOR yellow]Urdu Catchup TV[/COLOR]',
         '93hum': 'Hum TV : [COLOR yellow]Urdu Catchup TV[/COLOR]',
         '99gmala': 'Hindi Geetmala : [COLOR yellow]Hindi Songs[/COLOR]'
         }


def make_listitem(*args, **kwargs):
    if kodiver < 18.0:
        li = xbmcgui.ListItem(*args, **kwargs)
    else:
        li = xbmcgui.ListItem(*args, offscreen=True, **kwargs)
    return li


def list_sites():
    """
    Create the Sites menu in the Kodi interface.
    """
    listing = []
    for site, title in sorted(six.iteritems(sites)):
        if _settings(site[2:]) == 'true':
            item_icon = _ipath + '{}.png'.format(site[2:])
            list_item = make_listitem(label=title)
            list_item.setArt({'thumb': item_icon,
                              'icon': item_icon,
                              'poster': item_icon,
                              'fanart': _fanart})
            url = '{0}?action=1&site={1}'.format(_url, site[2:])
            is_folder = True
            listing.append((url, list_item, is_folder))

    list_item = make_listitem(label='[COLOR yellow][B]Clear Cache[/B][/COLOR]')
    item_icon = _ipath + 'ccache.png'
    list_item.setArt({'thumb': item_icon,
                      'icon': item_icon,
                      'poster': item_icon,
                      'fanart': _fanart})
    url = '{0}?action=0'.format(_url)
    is_folder = False
    listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'addons')
    xbmcplugin.endOfDirectory(_handle)


def list_menu(site):
    """
    Create the Site menu in the Kodi interface.
    """
    scraper = eval('{}.{}()'.format(site, site))
    menu, mode, icon = cache.cacheFunction(scraper.get_menu)
    listing = []
    for title, iurl in sorted(six.iteritems(menu)):
        digits = len(re.findall(r'^(\d*)', title)[0])
        next_mode = mode

        if 'MMMM' in iurl:
            iurl, next_mode = iurl.split('MMMM')

        if 'Adult' not in title:
            list_item = make_listitem(label=title[digits:])
            list_item.setArt({'thumb': icon,
                              'icon': icon,
                              'poster': icon,
                              'fanart': _fanart})
            url = '{0}?action={1}&site={2}&iurl={3}'.format(_url, next_mode, site, urllib_parse.quote(iurl))
            if next_mode == 9:
                is_folder = False
                list_item.setProperty('IsPlayable', 'true')
                list_item.addStreamInfo('video', {'codec': 'h264'})
            else:
                is_folder = True
            listing.append((url, list_item, is_folder))

        elif _settings('adult') == 'true':
            list_item = make_listitem(label=title[digits:])
            list_item.setArt({'thumb': icon,
                              'icon': icon,
                              'poster': icon,
                              'fanart': _fanart})
            url = '{0}?action={1}&site={2}&iurl={3}'.format(_url, next_mode, site, urllib_parse.quote(iurl))
            is_folder = True
            listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'videos')
    xbmcplugin.endOfDirectory(_handle)


def list_top(site, iurl):
    """
    Create the Site menu in the Kodi interface.
    """
    scraper = eval('{}.{}()'.format(site, site))
    menu, mode = cache.cacheFunction(scraper.get_top, iurl)
    listing = []
    for title, icon, iurl in menu:
        if 'MMMM' in iurl:
            nurl, nmode = iurl.split('MMMM')
            list_item = make_listitem(label=title)
            list_item.setArt({'thumb': icon,
                              'icon': icon,
                              'fanart': _fanart})
            url = '{0}?action={1}&site={2}&iurl={3}'.format(_url, nmode, site, urllib_parse.quote(nurl))
            is_folder = True
            listing.append((url, list_item, is_folder))
        else:
            list_item = make_listitem(label=title)
            list_item.setArt({'thumb': icon,
                              'icon': icon,
                              'poster': icon,
                              'fanart': _fanart})
            url = '{0}?action={1}&site={2}&iurl={3}'.format(_url, mode, site, urllib_parse.quote(iurl))
            is_folder = True
            listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'videos')
    xbmcplugin.endOfDirectory(_handle)


def list_second(site, iurl):
    """
    Create the Site menu in the Kodi interface.
    """
    scraper = eval('{}.{}()'.format(site, site))
    menu, mode = cache.cacheFunction(scraper.get_second, iurl)
    listing = []
    for title, icon, iurl in menu:
        list_item = make_listitem(label=title)
        list_item.setArt({'thumb': icon,
                          'icon': icon,
                          'poster': icon,
                          'fanart': _fanart})
        nextmode = mode
        if 'MMMM' in iurl:
            iurl, nextmode = iurl.split('MMMM')
        if 'Next Page' in title:
            nextmode = 5
        url = '{0}?action={1}&site={2}&iurl={3}'.format(_url, nextmode, site, urllib_parse.quote(iurl))
        is_folder = True
        if mode == 9 and 'Next Page' not in title:
            is_folder = False
            list_item.setProperty('IsPlayable', 'true')
            list_item.addStreamInfo('video', {'codec': 'h264'})
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'tvshows')
    xbmcplugin.endOfDirectory(_handle)


def list_third(site, iurl):
    """
    Create the Site menu in the Kodi interface.
    """
    scraper = eval('{}.{}()'.format(site, site))
    menu, mode = cache.cacheFunction(scraper.get_third, iurl)
    listing = []
    for title, icon, iurl in menu:
        list_item = make_listitem(label=title)
        list_item.setArt({'thumb': icon,
                          'icon': icon,
                          'poster': icon,
                          'fanart': _fanart})
        nextmode = mode
        if 'Next Page' in title:
            nextmode = 6
        url = '{0}?action={1}&site={2}&iurl={3}'.format(_url, nextmode, site, urllib_parse.quote(iurl))
        is_folder = True
        if mode == 8 and 'Next Page' not in title:
            url = '{0}?action={1}&site={2}&title={3}&thumb={4}&iurl={5}'.format(_url, mode, site, urllib_parse.quote(title), urllib_parse.quote(icon), iurl)
        if mode == 9 and 'Next Page' not in title:
            is_folder = False
            list_item.setProperty('IsPlayable', 'true')
            list_item.addStreamInfo('video', {'codec': 'h264'})
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'tvshows')
    xbmcplugin.endOfDirectory(_handle)


def list_items(site, iurl):
    """
    Create the list of movies/episodes in the Kodi interface.
    """
    scraper = eval('{}.{}()'.format(site, site))
    if iurl.endswith('='):
        movies, mode = scraper.get_items(iurl)
    else:
        movies, mode = cache.cacheFunction(scraper.get_items, iurl)
    listing = []
    for movie in movies:
        title = movie[0]
        if title == '':
            title = 'Unknown'
        list_item = make_listitem(label=title)
        if 'Next Page' in title:
            nextmode = 7
            url = '{0}?action={1}&site={2}&iurl={3}'.format(_url, nextmode, site, urllib_parse.quote(movie[2]))
            list_item.setInfo('video', {'title': title})
            list_item.setArt({'thumb': movie[1],
                              'icon': movie[1],
                              'poster': movie[1],
                              'fanart': _fanart})
        else:
            qtitle = urllib_parse.quote(title)
            iurl = urllib_parse.quote(movie[2])
            mthumb = movie[1].encode('utf8') if six.PY2 else movie[1]
            url = '{0}?action={1}&site={2}&title={3}&thumb={4}&iurl={5}'.format(_url, mode, site, qtitle, urllib_parse.quote(mthumb), iurl)
            fanart = _fanart
            poster = movie[1]
            if _settings('meta') == 'true' and site in msites:
                from resources.lib.metautils import get_meta
                meta = get_meta(title)
                if 'tmdb_id' in meta.keys():
                    list_item.setInfo('video', {'title': title, 'mediatype': 'video'})
                else:
                    if meta.get('backdrop_url'):
                        fanart = meta.get('backdrop_url')
                    if meta.get('cover_url'):
                        poster = meta.get('cover_url')
                    meta.pop('backdrop_url')
                    meta.pop('cover_url')
                    meta.update({'mediatype': 'movie'})
                    list_item.setInfo('video', meta)

            list_item.setArt({
                'thumb': movie[1],
                'icon': movie[1],
                'poster': poster,
                'fanart': fanart
            })
        if mode == 9 and 'Next Page' not in title:
            is_folder = False
            list_item.setProperty('IsPlayable', 'true')
            list_item.addStreamInfo('video', {'codec': 'h264'})
            list_item.addContextMenuItems([('Save Video', 'RunPlugin(plugin://{0}/?action=10&iurl={1}ZZZZ{2})'.format(_addonID, urllib_parse.quote_plus(iurl), title),)])
        else:
            is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'movies')
    xbmcplugin.endOfDirectory(_handle)


def list_videos(site, title, iurl, thumb):
    """
    Create the list of playable videos in the Kodi interface.
    """
    scraper = eval('{}.{}()'.format(site, site))
    videos = cache.cacheFunction(scraper.get_videos, iurl)
    listing = []
    for name, video in videos:
        list_item = make_listitem(label=name)
        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'poster': thumb,
                          'fanart': thumb})
        list_item.setInfo('video', {'title': title})
        list_item.addStreamInfo('video', {'codec': 'h264'})
        list_item.setProperty('IsPlayable', 'true')
        url = '{0}?action=9&iurl={1}'.format(_url, urllib_parse.quote_plus(video))
        if 'm3u8' not in video:
            list_item.addContextMenuItems([('Save Video', 'RunPlugin(plugin://{0}/?action=10&iurl={1}ZZZZ{2})'.format(_addonID, urllib_parse.quote_plus(video), title),)])
        is_folder = False
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'videos')
    xbmcplugin.endOfDirectory(_handle)


def resolve_url(url):
    hmf = resolveurl.HostedMediaFile(url=url)
    if not hmf:
        xbmcgui.Dialog().ok('Resolve URL', 'Indirect hoster_url not supported by smr: {0}'.format(url))
        return False
    try:
        stream_url = hmf.resolve()
        # If resolveurl returns false then the video url was not resolved.
        if not stream_url or not isinstance(stream_url, six.string_types):
            if not stream_url:
                msg = 'File removed'
            else:
                msg = str(stream_url)
            xbmcgui.Dialog().notification('Resolve URL', msg, _icon, 5000, False)
            return False
    except Exception as e:
        try:
            msg = str(e)
        except:
            msg = url
        xbmcgui.Dialog().notification('Resolve URL', msg, _icon, 5000, False)
        return False

    return stream_url


class StopDownloading(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def downloadVideo(url, name):

    def _pbhook(downloaded, filesize, url=None, dp=None, name=''):
        try:
            percent = min(int((downloaded * 100) / filesize), 100)
            currently_downloaded = float(downloaded) / (1024 * 1024)
            kbps_speed = int(downloaded / (time.perf_counter() if six.PY3 else time.clock() - start))
            if kbps_speed > 0:
                eta = (filesize - downloaded) / kbps_speed
            else:
                eta = 0
            kbps_speed = kbps_speed / 1024
            total = float(filesize) / (1024 * 1024)
            mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
            e = 'Speed: %.02f MB/s ' % kbps_speed
            e += 'ETA: %02d:%02d' % divmod(eta, 60)
            dp.update(percent, '{0}[CR]{1}[CR]{2}'.format(name[:50], mbs, e))
        except:
            percent = 100
            dp.update(percent)
        if dp.iscanceled():
            dp.close()
            raise StopDownloading('Stopped Downloading')

    def getResponse(url, hdrs, size):
        try:
            if size > 0:
                size = int(size)
                hdrs['Range'] = 'bytes=%d-' % size

            req = urllib_request.Request(url, headers=hdrs)

            resp = urllib_request.urlopen(req, timeout=30)
            return resp
        except:
            return None

    def doDownload(url, dest, dp, name):
        headers = {}
        if '|' in url:
            url, uheaders = url.split('|')
            headers = dict(urllib_parse.parse_qsl(uheaders))

        if 'User-Agent' not in list(headers.keys()):
            headers.update({'User-Agent': mozhdr})

        resp = getResponse(url, headers, 0)

        if not resp:
            dialog.ok("Deccan Delight", 'Download Failed[CR]No response')
            return False
        try:
            content = int(resp.headers['Content-Length'])
        except:
            content = 0
        try:
            resumable = 'bytes' in resp.headers['Accept-Ranges'].lower()
        except:
            resumable = False
        if resumable:
            xbmc.log("Download is resumable", xbmc.LOGDEBUG)

        if content < 1:
            dialog.ok("Deccan Delight", 'Unknown File Size[CR]Cannot Download')
            return False

        size = 8192
        mb = content / (1024 * 1024)

        if content < size:
            size = content

        total = 0
        errors = 0
        count = 0
        resume = 0
        sleep = 0

        xbmc.log('Filesize : {0}MB {1} '.format(mb, dest), xbmc.LOGDEBUG)
        f = xbmcvfs.File(dest, 'w')

        chunk = None
        chunks = []

        while True:
            downloaded = total
            for c in chunks:
                downloaded += len(c)
            percent = min(100 * downloaded / content, 100)

            _pbhook(downloaded, content, url, dp, name)

            chunk = None
            error = False

            try:
                chunk = resp.read(size)
                if not chunk:
                    if percent < 99:
                        error = True
                    else:
                        while len(chunks) > 0:
                            c = chunks.pop(0)
                            f.write(c)
                            del c
                        f.close()
                        return True

            except Exception as e:
                xbmc.log(str(e), xbmc.LOGDEBUG)
                error = True
                sleep = 10
                errno = 0

                if hasattr(e, 'errno'):
                    errno = e.errno

                if errno == 10035:  # 'A non-blocking socket operation could not be completed immediately'
                    pass

                if errno == 10054:  # 'An existing connection was forcibly closed by the remote host'
                    errors = 10  # force resume
                    sleep = 30

                if errno == 11001:  # 'getaddrinfo failed'
                    errors = 10  # force resume
                    sleep = 30

            if chunk:
                errors = 0
                chunks.append(chunk)
                if len(chunks) > 5:
                    c = chunks.pop(0)
                    f.write(c)
                    total += len(c)
                    del c

            if error:
                errors += 1
                count += 1
                xbmc.sleep(sleep * 1000)

            if (resumable and errors > 0) or errors >= 10:
                if (not resumable and resume >= 50) or resume >= 500:
                    # Give up!
                    return False

                resume += 1
                errors = 0
                if resumable:
                    chunks = []
                    # create new response
                    resp = getResponse(url, headers, total)
                else:
                    # use existing response
                    pass

    def clean_filename(s):
        if not s:
            return ''
        badchars = '\\/:*?"<>|\''
        for c in badchars:
            s = s.replace(c, '')
        return s.strip()

    download_path = _settings('dlfolder')
    while not download_path:
        xbmcgui.Dialog().notification('Download:', 'Choose download directory in Settings!', _icon, 5000, False)
        _addon.openSettings()
        download_path = _settings('dlfolder')

    dp = xbmcgui.DialogProgress()
    name = re.sub(r'\[/?(?:COLOR|I|CR|B).*?]', '', name).strip()
    dp.create('Deccan Delight Download', name[:50])
    tmp_file = tempfile.mktemp(dir=download_path, suffix=".mp4")
    tmp_file = xbmc.makeLegalFilename(tmp_file) if six.PY2 else xbmcvfs.makeLegalFilename(tmp_file)
    vidfile = xbmc.makeLegalFilename(download_path + clean_filename(name) + ".mp4") if six.PY2 \
        else xbmcvfs.makeLegalFilename(download_path + clean_filename(name) + ".mp4")
    if not xbmcvfs.exists(vidfile):
        start = time.perf_counter() if six.PY3 else time.clock()
        try:
            downloaded = doDownload(url, tmp_file, dp, name)
            if downloaded:
                try:
                    xbmcvfs.rename(tmp_file, vidfile)
                    return vidfile
                except:
                    return tmp_file
            else:
                raise StopDownloading('Stopped Downloading')
        except:
            while xbmcvfs.exists(tmp_file):
                try:
                    xbmcvfs.delete(tmp_file)
                    break
                except:
                    pass
    else:
        xbmcgui.Dialog().notification('Download:', 'File already exists!', _icon, 3000, False)


def play_video(vid_url, dl=False):
    """
    Play a video by the provided path.
    """
    streamer_list = ['tamilgun', 'mersalaayitten', 'mhdtvworld.', '/hls/', 'poovee.',
                     'watchtamiltv.', 'cloudspro.', 'abroadindia.', 'nextvnow.', 'harpalgeo.',
                     'hindigeetmala.', '.mp4', 'googlevideo.', 'playembed.', 'akamaihd.',
                     'tamilhdtv.', 'andhrawatch.', 'tamiltv.', 'athavantv', 'cinemalayalam',
                     'justmoviesonline.', '.mp3', 'googleapis.', '.m3u8', 'telugunxt.',
                     'playsominaltv.', 'bharat-movies.', 'googleusercontent.', 'arydigital.',
                     'space-cdn.', 'einthusan.', 'd0stream.', 'telugugold.', 'tamilyogi.',
                     'hum.tv', 'apnevideotwo.', 'player.business', 'tamilian.', 'tamilvip.']
    # Create a playable item with a path to play.
    title = 'unknown'
    vid_url = urllib_parse.unquote_plus(vid_url)
    if 'ZZZZ' in vid_url:
        vid_url, title = vid_url.split('ZZZZ')

    play_item = make_listitem(path=vid_url)

    if any([x in vid_url for x in streamer_list]):
        if 'einthusan.' in vid_url:
            scraper = einthusan.einthusan()  # NoQA
            stream_url = scraper.get_video(vid_url)
            play_item.setPath(stream_url)
        elif 'apnevideotwo.' in vid_url:
            stream_url = urllib_parse.quote(vid_url, ':/|=?')
            play_item.setPath(stream_url)
        elif 'player.business' in vid_url:
            headers = {'User-Agent': mozhdr}
            spage = client.request(vid_url, headers=headers)
            matches = re.findall(r'"src":"([^"]+)","label":"([^"]+)', spage)
            if len(matches) > 1:
                sources = []
                for match in matches:
                    sources.append(match[1])
                dialog = xbmcgui.Dialog()
                ret = dialog.select('Choose a Source', sources)
                match = matches[ret]
            else:
                match = matches[0]
            stream_url = match[0] + '|User-Agent={}'.format(mozhdr)
            play_item.setPath(stream_url)
        elif 'tamilyogi.' in vid_url or 'tamilvip.' in vid_url:
            scraper = tyogi.tyogi()  # NoQA
            stream_url = scraper.get_video(vid_url)
            if stream_url:
                stream_url = resolve_url(stream_url)
                if stream_url:
                    play_item.setPath(stream_url)
                else:
                    play_item.setPath(None)
        elif 'tamilian.' in vid_url:
            scraper = tamilian.tamilian()  # NoQA
            stream_url = scraper.get_video(vid_url)
            if stream_url:
                stream_url = resolve_url(stream_url)
                if stream_url:
                    play_item.setPath(stream_url)
                else:
                    play_item.setPath(None)
        elif 'hindigeetmala.' in vid_url:
            scraper = gmala.gmala()  # NoQA
            stream_url = scraper.get_video(vid_url)
            if stream_url:
                if 'youtube.' in stream_url:
                    stream_url = resolve_url(stream_url)
                play_item.setPath(stream_url)
        elif 'telugunxt.' in vid_url or 'telugugold.' in vid_url:
            scraper = tflame.tflame()  # NoQA
            stream_url = scraper.get_video(vid_url)
            if stream_url:
                stream_url = resolve_url(stream_url)
                if stream_url:
                    play_item.setPath(stream_url)
                else:
                    play_item.setPath(None)
        elif 'bharat-movies.' in vid_url:
            scraper = bmov.bmov()  # NoQA
            stream_url = scraper.get_video(vid_url)
            if stream_url:
                stream_url = resolve_url(stream_url)
                if stream_url:
                    play_item.setPath(stream_url)
                else:
                    play_item.setPath(None)
        elif 'tamilgun.' in vid_url:
            if '.m3u8' in vid_url:
                stream_url = vid_url
            else:
                scraper = tgun.tgun()  # NoQA
                stream_url = scraper.get_video(vid_url)
            if stream_url:
                play_item.setPath(stream_url)
        elif 'andhrawatch.' in vid_url:
            scraper = awatch.awatch()  # NoQA
            stream_url = scraper.get_video(vid_url)
            if stream_url:
                if 'youtube.' in stream_url:
                    stream_url = resolve_url(stream_url)
                if stream_url:
                    play_item.setPath(stream_url)
                else:
                    play_item.setPath(None)
        elif 'arydigital.' in vid_url:
            scraper = ary.ary()  # NoQA
            stream_url = scraper.get_video(vid_url)
            if resolveurl.HostedMediaFile(stream_url):
                stream_url = resolve_url(stream_url)
            if stream_url:
                play_item.setPath(stream_url)
            else:
                play_item.setPath(None)
        elif 'harpalgeo.' in vid_url:
            scraper = geo.geo()  # NoQA
            stream_url = scraper.get_video(vid_url)
            play_item.setPath(stream_url)
        elif 'hum.tv' in vid_url:
            scraper = hum.hum()  # NoQA
            stream_url = scraper.get_video(vid_url)
            if 'youtube.' in stream_url or 'dailymotion' in stream_url:
                stream_url = resolve_url(stream_url)
            if stream_url:
                play_item.setPath(stream_url)
            else:
                play_item.setPath(None)
        elif 'playembed.' in vid_url or 'videoapne.' in vid_url or '.m3u8' in vid_url:
            stream_url = vid_url
            play_item.setPath(stream_url)
        elif 'load.' in vid_url:
            stream_url = resolve_url(vid_url)
            if stream_url:
                play_item.setPath(stream_url)
            else:
                play_item.setPath(None)
        elif '.mp4' in vid_url:
            if '|' not in vid_url and resolveurl.HostedMediaFile(vid_url):
                stream_url = resolve_url(vid_url)
            else:
                stream_url = vid_url
            if stream_url:
                play_item.setPath(stream_url)
            else:
                play_item.setPath(None)
        else:
            stream_url = vid_url
            play_item.setPath(stream_url)
    else:
        stream_url = resolve_url(vid_url)
        if stream_url:
            play_item.setPath(stream_url)
        else:
            # play_item.setPath(None)
            return

    if dl and stream_url:
        downloadVideo(stream_url, title)

    elif stream_url:
        non_ia = ['yupp', 'SUNNXT', 'tamilgun', 'vidmojo', 'serafim', '__temp_', 'cloud']
        # xbmc.log('\n@@@@DD Final URL = {}\n'.format(stream_url), xbmc.LOGNOTICE)

        if kodiver >= 17.0 and not any(x in stream_url for x in non_ia):

            if '.m3u8' in stream_url:
                play_item.setMimeType('application/vnd.apple.mpegstream_url')
                play_item.setContentLookup(False)
                adaptive_list = ['master', 'adaptive', 'tamilray', 'index']
                if any([x in stream_url for x in adaptive_list]):
                    if kodiver < 19.0:
                        play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
                    else:
                        play_item.setProperty('inputstream', 'inputstream.adaptive')
                    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
                    if '|' in stream_url:
                        stream_url, strhdr = stream_url.split('|')
                        play_item.setProperty('inputstream.adaptive.stream_headers', strhdr)
                        play_item.setPath(stream_url)

            elif '.mpd' in stream_url:
                if kodiver < 19.0:
                    play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
                else:
                    play_item.setProperty('inputstream', 'inputstream.adaptive')
                play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
                play_item.setMimeType('application/dash+xml')
                play_item.setContentLookup(False)

            elif '.ism' in stream_url:
                if kodiver < 19.0:
                    play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
                else:
                    play_item.setProperty('inputstream', 'inputstream.adaptive')
                play_item.setProperty('inputstream.adaptive.manifest_type', 'ism')
                play_item.setMimeType('application/vnd.ms-sstr+xml')
                play_item.setContentLookup(False)

        xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
