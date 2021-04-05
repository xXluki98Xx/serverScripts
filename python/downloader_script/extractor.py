import logging
import urllib.request

import youtube_dl

from downloader import *
from functions import *
from ioutils import *


# ----- # ----- #
def getLanguage(dto, platform):
    output = '--no-mark-watched --hls-prefer-ffmpeg --socket-timeout 30 '

    if platform == 'crunchyroll':
        if dto.getSubLang() == 'de': return output + '-f "best[format_id*=adaptive_hls-audio-jpJP-hardsub-deDE]"'
        if dto.getDubLang() == 'de': return output + '-f "best[format_id*=adaptive_hls-audio-deDE][format_id!=hardsub]"'


def getUserCredentials(dto, platform):
    credentialList = ['animeondemand', 'udemy']

    dto.publishLoggerDebug(dto.getData())

    if platform in credentialList:
        if platform == 'animeondemand':
            for p in dto.getData()['animeondemand']:
                parameter = '-u ' + p['username'] + ' -p ' + p['password'] + ' ' + dto.getParameters()

        if platform == 'udemy':
            for p in dto.getData()['udemy']:
                parameter = '-u ' + p['username'] + ' -p ' + p['password'] + ' ' + dto.getParameters()

    if dto.getCookieFile():
        parameter = '--cookies ' + dto.getCookieFile() + ' ' + dto.getParameters()

    dto.publishLoggerDebug(parameter)

    return parameter


# ----- # ----- #
def ydl_extractor(dto, content):
    title = ''
    stringReferer = ''
    directory = '.'

    try:
        (url, title, stringReferer, directory) = content.split(';')
    except ValueError:
        try:
            (url, title, stringReferer) = content.split(';')            
        except ValueError:
            try:
                (url, title) = content.split(';')
            except ValueError:
                url = content

    if ('magnet:?xt=urn:btih' in content):
        dto.publishLoggerInfo('current Download: ' + url)
        try:
            (url, directory) = content.split(';')
        except ValueError:
            url = content
            directory = ''

        return download_aria2c_magnet(dto, url, directory)

    webpageResult = testWebpage(dto, url.split('?')[0])
    if webpageResult != 0:
        return webpageResult

    mostly = ['fruithosted', 'oloadcdn', 'verystream', 'vidoza', 'vivo']

    dto.publishLoggerInfo('current Download: ' + url)

    for domain in mostly:
        if domain in url : return host_mostly(dto, url, title, stringReferer, directory)

    # if ('animeholics' in url) : return host_animeholics(dto, url, title, stringReferer, directory)

    if ('haho.moe' in url) :
        if (len(url.rsplit('/',1)[1]) < 3):
            return host_hahomoe(dto, url, title, stringReferer, directory)
        else:
            i = 1
            while testWebpage(dto, url+'/'+str(i)) == 0:
                ydl_extractor(dto, url+'/'+str(i))
                i += 1

            i = 1
            while testWebpage(dto, url+'/s'+str(i)) == 0:
                ydl_extractor(dto, url+'/s'+str(i))
                i += 1

            return 0

    if ('sxyprn' in url) : return host_sxyprn(dto, url, title, stringReferer, directory)
    if ('porngo' in url) : return host_porngo(dto, url, title, stringReferer, directory)
    if ('xvideos' in url) : return host_xvideos(dto, url, title, stringReferer, directory)

    if ('udemy' in url) : return host_udemy(dto, url, title, stringReferer, directory)
    if ('crunchyroll' in url) : return host_crunchyroll(dto, url, title, stringReferer, directory)
    if ('anime-on-demand' in url) : return host_animeondemand(dto, url, title, stringReferer, directory)
    if ('vimeo' in url) : return host_vimeo(dto, url, title, stringReferer, directory)
    if ('cloudfront' in url) : return host_cloudfront(dto, url, title, stringReferer, directory)

    return host_default(dto, url, title, stringReferer, directory)


def host_default(dto, content, title, stringReferer, directory):
    if not dto.getPlaylist():

        ydl_opts = {
            'outtmpl': '%(title)s',
            'restrictfilenames': True,
            'forcefilename':True
        }

        try:
            if title == '':
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(content, download = False)
                    filename = ydl.prepare_filename(info)

                    dto.publishLoggerDebug('extracted filename: ' + filename)

                filename = getTitleFormated(filename)

                output = '-f best --no-playlist -o "{dir}/{title}.%(ext)s"'.format(title = filename, dir = directory)
                return download_ydl(dto, content, dto.getParameters(), output, stringReferer)
            else:
                filename = getTitleFormated(title)

                output = '-f best --no-playlist -o "{dir}/{title}.%(ext)s"'.format(title = filename, dir = directory)
                return download_ydl(dto, content, dto.getParameters(), output, stringReferer)

        except:
            output = '-f best --no-playlist -o "{dir}/%(title)s.%(ext)s"'.format(dir = directory)
            return download_ydl(dto, content, dto.getParameters(), output, stringReferer)

    else:
        output = '-i -f best -o "{dir}/%(extractor)s--%(playlist_uploader)s_%(playlist_title)s/%(playlist_index)s_%(title)s.%(ext)s"'.format(dir = directory)
        return download_ydl(dto, content, dto.getParameters(), output, stringReferer)


def host_mostly(dto, content, title, stringReferer, directory):
    if title == '':
        title = str(input('\nPlease enter the Title:\n'))

    title = getTitleFormated(title)
    output = '-f best -o "{dir}/{title}.%(ext)s"'.format(title = title, dir = directory)

    return download_ydl(dto, content, dto.getParameters(), output, stringReferer)


def host_hanime(dto, content, title, stringReferer, directory):
    if title == '':
        title = content.rsplit('?',1)[0].rsplit('/',1)[1]

    title = getTitleFormated(title)
    output = '-f best -o "{dir}/{title}.%(ext)s"'.format(title = title, dir = directory)

    return download_ydl(dto, content, dto.getParameters(), output, stringReferer)


def host_hahomoe(dto, content, title, stringReferer, directory):
    url = content
    webpage = ''

    req = urllib.request.Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        webpage = response.read()

    urlRegex = re.compile('<source data-fluid-hd="" src="(.*?)" title="720p" type="video/mp4"></source>')
    m = urlRegex.search(str(webpage))
    if m:
        url = m.group(1)

    if title == '':
        titleRegex = re.compile('<title>(.*?)</title>')
        m = titleRegex.search(str(webpage))
        if m:
            title = m.group(1).rsplit(' ',4)[0]
        else:
            title = ''

    title = getTitleFormated(title)
    output = '-f best -o "{dir}/{title}.mp4"'.format(title = title, dir = directory)

    return download_ydl(dto, url, dto.getParameters(), output, stringReferer)


def host_sxyprn(dto, content, title, stringReferer, directory):
    url = content
    webpage = ''

    req = urllib.request.Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        webpage = response.read()

    if title == '':
        title = str(webpage).split('<title>')[1].split('</title>')[0]
        title = title.rsplit('-', 1)[0]
        title = title.casefold().replace(' ', '-').replace('.','').rsplit('-', 1)[0]

        if '#' in title:
            title = title.split('-#',1)[0]

    title = getTitleFormated(title)
    output = '-f best -o "{dir}/{title}.%(ext)s"'.format(title = title, dir = directory)

    return download_ydl(dto, content, dto.getParameters(), output, stringReferer)


def host_xvideos(dto, content, title, stringReferer, directory):
    if title == '':
        title = content.rsplit('/',1)[1]

    title = getTitleFormated(title)
    output = '-f best -o "{dir}/{title}.mp4"'.format(title = title, dir = directory)

    return download_ydl(dto, content, dto.getParameters(), output, stringReferer)


def host_porngo(dto, content, title, stringReferer, directory):
    if title == '':
        title = content.rsplit('/',1)[0].rsplit('/',1)[1]

    title = getTitleFormated(title)
    output = '-f best -o "{dir}/{title}.%(ext)s"'.format(title = title, dir = directory)

    return download_ydl(dto, content, dto.getParameters(), output, stringReferer)


def host_animeondemand(dto, content, title, stringReferer, directory):
    parameters = getUserCredentials(dto, 'animeondemand')

    if 'www.' not in content:
        swap = content.split('/', 2)
        content = 'https://www.' + swap[2]

    output = '-f "best[format_id*=ger-Dub]" -o "{dir}/%(playlist)s/episode-%(playlist_index)s.%(ext)s"'

    return download_ydl(dto, content, parameters, output, stringReferer)


def host_crunchyroll(dto, content, title, stringReferer, directory):
    parameters = getUserCredentials(dto, 'crunchyroll')

    if 'www.' not in content:
        swap = content.split('/', 2)
        content = 'https://www.' + swap[2]

    output = str(getLanguage(dto, 'crunchyroll'))
    output += ' -i -o "{dir}/%(playlist)s/season-%(season_number)s-episode-%(episode_number)s-%(episode)s.%(ext)s"'.format(dir = directory)

    return download_ydl(dto, content, parameters, output, stringReferer)


def host_udemy(dto, content, title, stringReferer, directory):
    parameter = getUserCredentials(dto, 'udemy')

    if '/course/' in content:
        content = content.replace('/course', '')

    if 'https://udemy.com' in content:
        content = content.replace('https://udemy.com', 'https://www.udemy.com')

    title = content.split('/')[3]

    dto.publishLoggerInfo('udemy title: ' + str(title))
    dto.publishLoggerInfo('udemy url: ' + content)

    output = '-f best -o "{dir}/%(playlist)s - {title}/%(chapter_number)s-%(chapter)s/%(playlist_index)s-%(title)s.%(ext)s"'.format(title = title, dir = directory)

    return download_ydl(dto, content, parameter, output, stringReferer)


def host_vimeo(dto, content, title, stringReferer, directory):
    if title == '':
        title = str(input('\nPlease enter the Title:\n'))

    if stringReferer == '':
        stringReferer = str(input('\nPlease enter the reference URL:\n'))

    content = content.split('?')[0]
    title = getTitleFormated(title)
    output = '-f best -o "{dir}/{title}.%(ext)s"'.format(title = title, dir = directory)

    return download_ydl(dto, content, dto.getParameters(), output, stringReferer)


def host_cloudfront(dto, content, title, stringReferer, directory):
    if title == '':
        title = str(input('\nPlease enter the Title:\n'))

    title = getTitleFormated(title)
    output = '-f best -o "{dir}/{title}.mp4"'.format(title = title, dir = directory)

    return download_ydl(dto, content, dto.getParameters(), output, stringReferer)