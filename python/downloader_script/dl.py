#!/usr/bin/env python3

import os
import random
import sys
import time
from datetime import datetime

import bs4
import click
import requests
import safer
# import youtube_dl
# from exitstatus import ExitStatus

from downloader import *
from dto import dto
from functions import *
from ioutils import *
from extractor import *


# ----- # ----- # time measurement
def elapsedTime():
    time_elapsed = datetime.now() - dto.getTimeStart()
    dto.publishLoggerInfo('Time elapsed (hh:mm:ss.ms): {}'.format(time_elapsed))


# ----- # ----- #
def getLinkList(link, listFile):
    dto.publishLoggerInfo('beginning link extraction')

    itemList = 'list_Links'
    page = requests.get(link)
    if page.status_code == 200:
        dto.publishLoggerInfo('got page')
        content = page.content

        DOMdocument = bs4.BeautifulSoup(content, 'html.parser')

        listLinks = []

        # for a in DOMdocument.find_all('a'):
        #     if 'serie/' in a:
        #         listLinks.append(a.string)

        dto.publishLoggerInfo('writting links to file')
        with safer.open(listFile, 'w') as f:
            for url in listLinks:
                if 'pdf' in url:
                    f.write(link+'%s\n' % url)
        dto.publishLoggerInfo('finished writing')


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
        for i in range(wanted_parts) ]


def chunks(lst, n):
    '''Yield successive n-sized chunks from lst.'''
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# - - - - - # - - - - - # - - - - - # - - - - - # main functions

# ----- # ----- # main
@click.group()

# switch
@click.option('-a', '--axel', default=False, is_flag=True, help='Using Axel')
@click.option('-p', '--playlist', default=False, is_flag=True, help='Playlist')
@click.option('-nr', '--no-remove', default=False, is_flag=True, help='remove Files at wget')
@click.option('-up', '--update-packages', default=False, is_flag=True, help='updates packages listed in requirements.txt')
@click.option('-sy', '--sync', default=False, is_flag=True, help='')
@click.option('-v', '--verbose', default=False, is_flag=True, help='Verbose mode')
@click.option('-cr', '--credentials', default=False, is_flag=True, help='Need Credentials')

# int
@click.option('--retries', default=5, help='Enter an Number for Retries')
@click.option('--min-sleep', default=2, help='Enter an Number for min-Sleep between retries/ downloads')
@click.option('--max-sleep', default=15, help='Enter an Number for max-Sleep between retries/ downloads')
@click.option('-bw','--bandwidth', default='0', help='Enter an Bandwidthlimit like 1.5M')

# string
@click.option('-cf','--cookie-file', default='', help='Enter Path to cookie File')
@click.option('-sl','--sub-lang', default='', help='Enter language Code (de / en)')
@click.option('-dl','--dub-lang', default='', help='Enter language Code (de / en)')
@click.option('-d', '--debug', default='INFO', help='Using Logging mode')

def main(retries, min_sleep, max_sleep, bandwidth, axel, cookie_file, sub_lang, dub_lang, playlist, no_remove, update_packages, debug, sync, verbose, credentials):
    global dto
    dto = dto()
    dto.setVerbose(verbose)
    dto.setLogger(debug)

    dto.setBandwidth(bandwidth)
    dto.setSubLang(sub_lang)
    dto.setDubLang(dub_lang)
    dto.setCookieFile(cookie_file)
    dto.setPlaylist(playlist)
    dto.setRemoveFiles(no_remove)
    dto.setSync(sync)
    dto.setAxel(axel)
    dto.setSingle(False)
    dto.setPathToRoot(getRootPath(dto))
    dto.setCredentials(credentials)

    if update_packages:
        update(dto, dto.getPathToRoot())

    dto.setData(loadConfig(dto.getPathToRoot()))

    parameters = '--retries {retries} --min-sleep-interval {min_sleep} --max-sleep-interval {max_sleep} --continue'.format(retries = retries, min_sleep = min_sleep, max_sleep = max_sleep)
    dto.setParameters(parameters)


# ----- # ----- # rename command
@main.command(help='Path for rename, not file')

# string
@click.option('-os', '--offset', default=0, help='String Offset')
@click.option('-c', '--cut', default=0, help='Cut String')
@click.option('-p', '--platform', default='', help='Platform')

# switch
@click.option('-cr', '--crunchyroll', default=False, is_flag=True, help='syntax Crunchyroll')
@click.option('-s', '--single', default=False, is_flag=True, help='series is only one Season')

# arguments
@click.argument('rename', nargs=-1)

def rename(rename, offset, cut, platform, single):
    dto.setSingle(single)

    if platform:
        platform = 'crunchyroll'

    for itemPath in rename:
        func_rename(dto, itemPath, platform, offset, cut)


# ----- # ----- # replace command
@main.command(help='Path, old String, new String')

# string
@click.option('-o', '--old', default='', help='old String')
@click.option('-n', '--new', default='', help='new String')

# arguments
@click.argument('replace', nargs=-1)
def replace(replace, old, new):
    for itemPath in replace:
        func_replace(dto, itemPath, old, new)


# ----- # ----- # convertFiles command
@main.command(help='Path for convert, not file')

# switch
@click.option('-f', '--ffmpeg', default=False, is_flag=True, help='ffmpeg')
@click.option('-nf', '--no-fix', default=False, is_flag=True, help='fixing')
@click.option('-nr', '--no-renaming', default=False, is_flag=True, help='Directories Rename?')

# string
@click.option('-sp', '--subpath', default='', help='Path which will contain the new Files')
@click.option('-vc', '--vcodec', default='', help='new Video Codec')
@click.option('-ac', '--acodec', default='copy', help='new Audio Codec')

# arguments
@click.argument('newformat', nargs=1)
@click.argument('path', nargs=-1)

def convertFiles(newformat, path, subpath, ffmpeg, vcodec, acodec, no_fix, no_renaming):
    if ffmpeg:
        try:
            for itemPath in path:
                itemPathComplete = os.path.join(os.getcwd(), itemPath)

                dto.publishLoggerDebug('convertFiles')
                dto.publishLoggerDebug('filePathComplete: ' + itemPath)

                if os.path.isfile(itemPathComplete):
                    dto.publishLoggerDebug('is File: ' + str(os.path.isfile(itemPathComplete)))
                    func_convertFilesFfmpeg(dto, itemPathComplete, newformat, subpath, vcodec, acodec, no_fix)


                if os.path.isdir(itemPathComplete):
                    dto.publishLoggerDebug('is Dir: ' + str(os.path.isdir(itemPathComplete)))
                    func_convertDirFiles(dto, itemPathComplete, newformat, subpath, vcodec, acodec, no_fix)

                    if not no_renaming:
                        try:
                            os.rename(itemPath, func_formatingDirectories(itemPath))
                        except:
                            pass


        except:
            dto.publishLoggerInfo('error at convertFiles ffmpeg: ' + str(sys.exc_info()))

    elapsedTime()


# ----- # ----- # divideAndConquer command
@main.command(help='')

# switch
@click.option('-r', '--reverse', default=False, is_flag=True, help='reverse')

# string
@click.option('-d', '--dir', default='', help='Path which will contain the new Files')
@click.option('-f', '--file', default='', help='Path which will contain the new Files')

# int
@click.option('-cs', '--chunck-size', default=10, help='Enter an Number for Chunksize')

# arguments
@click.argument('url', nargs=1)

def dnc(url, file, dir, chunck_size, reverse):
    if not os.path.isfile(file):
        getLinkList(url, file)

    dto.publishLoggerDebug('dnc')

    with safer.open(file) as f:
        urlList = f.readlines()
        urlList = [x.strip() for x in urlList]

    urlCopy = urlList.copy()

    chunkedList = list(chunks(urlCopy, chunck_size))

    if reverse:
        chunkedList.reverse()

    for itemList in chunkedList:

        random.shuffle(itemList)

        try:
            dto.publishLoggerDebug('downloading: ' + str(itemList))

            # if dl == 'wget':
            #     if download_wget2(str(item), dir) == 0:
            #         urlCopy.remove(item)
            #         print('\nremoved: ' + str(item) + ' | rest list ' + str(urlCopy))

            # if dl == 'aria':
            if download_aria2c(dto, itemList, dir) == 0:
                for i in itemList:
                    urlCopy.remove(i)

                dto.publishLoggerDebug('removed: ' + str(itemList) + ' | rest list ' + str(urlCopy))

        except KeyboardInterrupt:
            with safer.open(file, 'w') as f:
                for url in urlCopy:
                    f.write('%s\n' % url)
            dto.publishLoggerInfo('Interupt by User')
            elapsedTime()
            os._exit(1)
            break

        except:
            dto.publishLoggerInfo('error at divideAndConquer list: ' + str(sys.exc_info()))

        finally:
            # will always be executed last, with or without exception
            with safer.open(file, 'w') as f:
                for url in urlCopy:
                    f.write('%s\n' % url)

    elapsedTime()


# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - #       wget-download   # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #

# ----- # ----- # wget
@main.command(help='Enter an URL')

# switch
@click.option('-sp', '--space', default=False, is_flag=True, help='check if old file are deletable')

# string
@click.option('-a', '--accept', default='', help='Comma Seprated List of Accepted extensions, like iso,xz')
@click.option('-r', '--reject', default='', help='Comma Seprated List of Rejected extensions, like iso,xz')

# arguments
@click.argument('wget', nargs=-1)
def wget(wget, space, accept, reject):
    dto.publishLoggerDebug('wget')
    dto.setSpace(space)

    repeat = True

    while repeat:
        if wget != '':
            for item in wget:
                if os.path.isfile(item):
                    wget_list(item, accept, reject)
                else:
                    download_wget(dto, item, accept, reject)

            wget = ''
            elapsedTime()

        else:
            try:
                url = input('\nPlease enter the Url:\n')
                dto.setTimeStart(datetime.now())
                download_wget(dto, url, accept, reject)

            except KeyboardInterrupt:
                pass

        try:
            answer = input('\nDo you wish another Turn? (y | n):\n')
            if ('y' in answer) :
                repeat = True
                wget = ''
            else:
                repeat = False

        except KeyboardInterrupt:
            repeat = False


# ----- # ----- #
def wget_list(itemList, accept, reject):
    with safer.open(itemList) as f:
        urlList = f.readlines()
        urlList = [x.strip() for x in urlList]

    urlCopy = urlList.copy()

    if dto.getSync():
        random.shuffle(urlList)

    for item in urlList:

        dto.publishLoggerDebug('wget list: ' + str(urlList))

        try:
            if item.startswith('#') or item == '':
                urlCopy.remove(item)
                continue

            dto.publishLoggerDebug('downloading: ' + str(item))

            if dto.getSync():
                download_wget(dto, str(item), accept, reject)
                dto.publishLoggerInfo('finished: ' + str(item))
            else:
                if download_wget(dto, str(item), accept, reject) == 0:
                    urlCopy.remove(item)
                    dto.publishLoggerDebug('removed: ' + str(item) + ' | rest list ' + str(urlCopy))

        except KeyboardInterrupt:
            if not dto.getSync():
                with safer.open(itemList, 'w') as f:
                    for url in urlCopy:
                        f.write('%s\n' % url)
            dto.publishLoggerInfo('Interupt by User')
            elapsedTime()
            os._exit(1)

        except:
            dto.publishLoggerInfo('error at wget list: ' + str(sys.exc_info()))

        finally:
            # will always be executed last, with or without exception
            if not dto.getSync():
                with safer.open(itemList, 'w') as f:
                    for url in urlCopy:
                        f.write('%s\n' % url)


# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - #   youtube-download    # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #

# ----- # ----- # single URL
@main.command(help='Enter an URL for YoutubeDL')

# arguments
@click.argument('url', nargs=-1)
def ydl(url):
    repeat = True

    while repeat:
        if url != '':
            for item in url:
                if os.path.isfile(item):
                    ydl_list(item)
                else:
                    ydl_extractor(dto, item)

            url = ''
            elapsedTime()

        else:
            try:
                url = input('\nPlease enter the Url:\n')
                dto.setTimeStart(datetime.now())
                ydl_extractor(dto, url)

            except KeyboardInterrupt:
                pass

        try:
            answer = input('\nDo you wish another Turn? (y | n):\n')
            if ('y' in answer) :
                repeat = True
                url = ''
            else:
                repeat = False

        except KeyboardInterrupt:
            repeat = False


# ----- # ----- # list
def ydl_list(itemList):
    with safer.open(itemList) as f:
        urlList = f.readlines()
        urlList = [x.strip() for x in urlList]

    urlCopy = urlList.copy()

    dto.publishLoggerDebug('youtube-dl')
    dto.publishLoggerDebug('ydl list: ' + str(urlCopy))

    for item in urlList:

        try:
            if item.startswith('#') or item == '':
                urlCopy.remove(item)
                continue

            dto.publishLoggerDebug('current Download: ' + item)

            if dto.getSync():
                ydl_extractor(dto, str(item))
                dto.publishLoggerDebug('finished: ' + str(item))
            else:
                if ydl_extractor(dto, str(item)) == 0:
                    urlCopy.remove(item)
                    dto.publishLoggerInfo('removed: ' + str(item) + ' | rest list ' + str(urlCopy))

        except KeyboardInterrupt:
            dto.publishLoggerInfo('Interupt by User')
            if not dto.getSync():
                with safer.open(itemList, 'w') as f:
                    for url in urlCopy:
                        f.write('%s\n' % url)
            elapsedTime()
            os._exit(1)

        except:
            dto.publishLoggerInfo('error at ydl list: ' + str(sys.exc_info()))

        finally:
            # will always be executed last, with or without exception
            if not dto.getSync():
                with safer.open(itemList, 'w') as f:
                    for url in urlCopy:
                        f.write('%s\n' % url)

    elapsedTime()


# - - - - - # - - - - - # - - - - - # - - - - - # main
if __name__ == '__main__':
    main()