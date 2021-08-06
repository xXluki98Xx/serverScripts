#!/usr/bin/env python3

import os
import random
import sys
from datetime import datetime

import bs4
import click
import requests
import safer

import downloader
import functions
import ioutils
import workflow_ydl
import workflow_wget
import workflow_animescrapper
from dto import dto


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

# - - - - - # - - - - - # main
@click.group()

# switch
@click.option('-a', '--axel', default=False, is_flag=True, help='Using Axel')
@click.option('-p', '--playlist', default=False, is_flag=True, help='Playlist')
@click.option('-nr', '--no-remove', default=False, is_flag=True, help='remove Files at wget')
@click.option('-up', '--update-packages', default=False, is_flag=True, help='updates packages listed in requirements.txt')
@click.option('-sy', '--sync', default=False, is_flag=True, help='')
@click.option('-v', '--verbose', default=False, is_flag=True, help='Verbose mode')
@click.option('-cr', '--credentials', default=False, is_flag=True, help='Need Credentials')
@click.option('-s', '--single', default=False, is_flag=True, help='close after finish')
@click.option('-sc', '--skip-checks', default=False, is_flag=True, help='skip checks')

# int
@click.option('--retries', default=5, help='Enter an Number for Retries')
@click.option('--min-sleep', default=2, help='Enter an Number for min-Sleep between retries/ downloads')
@click.option('--max-sleep', default=15, help='Enter an Number for max-Sleep between retries/ downloads')
@click.option('-bw','--bandwidth', default='0', help='Enter an Bandwidthlimit like 1.5M')

# string
@click.option('-cf','--cookie-file', default='', help='Enter Path to cookie File')
@click.option('-sl','--sub-lang', default='', help='Enter language Code (de / en)')
@click.option('-dl','--dub-lang', default='', help='Enter language Code (de / en)')
@click.option('-d', '--debug', default='', help='Using Logging mode')

def main(retries, min_sleep, max_sleep, bandwidth, axel, cookie_file, sub_lang, dub_lang, playlist, no_remove, update_packages, debug, sync, verbose, single, credentials, skip_checks):
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
    dto.setSingle(single)
    dto.setSingle(False)
    dto.setSkipChecks(skip_checks)
    dto.setPathToRoot(ioutils.getRootPath(dto))
    # dto.setBreak(break)
    # dto.setCredentials(credentials)

    if update_packages:
        ioutils.update(dto, dto.getPathToRoot())

    dto.setData(ioutils.loadConfig(dto.getPathToRoot()))

    parameters = '--retries {retries} --min-sleep-interval {min_sleep} --max-sleep-interval {max_sleep} --continue'.format(retries = retries, min_sleep = min_sleep, max_sleep = max_sleep)
    dto.setParameters(parameters)


# - - - - - # - - - - - # rename command
@main.command(help='Path for rename, not file')

# string
@click.option('-os', '--offset', default=0, help='String Offset')
@click.option('-c', '--cut', default=0, help='Cut String')
@click.option('-p', '--platform', default='', help='Platform')

# switch
@click.option('-s', '--single', default=False, is_flag=True, help='series is only one Season')

# arguments
@click.argument('rename', nargs=-1)

def rename(rename, offset, cut, platform, single):
    dto.setSingle(single)

    for itemPath in rename:
        functions.func_rename(dto, itemPath, offset, cut)


# - - - - - # - - - - - # replace command
@main.command(help='Path, old String, new String')

# string
@click.option('-o', '--old', default='', help='old String')
@click.option('-n', '--new', default='', help='new String')

# arguments
@click.argument('replace', nargs=-1)
def replace(replace, old, new):
    for itemPath in replace:
        functions.func_replace(dto, itemPath, old, new)


# - - - - - # - - - - - # convertFiles command
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
                    functions.func_convertFilesFfmpeg(dto, itemPathComplete, newformat, subpath, vcodec, acodec, no_fix)


                if os.path.isdir(itemPathComplete):
                    dto.publishLoggerDebug('is Dir: ' + str(os.path.isdir(itemPathComplete)))
                    functions.func_convertDirFiles(dto, itemPathComplete, newformat, subpath, vcodec, acodec, no_fix)

                    if not no_renaming:
                        try:
                            os.rename(itemPath, ioutils.formatingDirectories(itemPath))
                        except:
                            pass


        except:
            dto.publishLoggerError('convertfiles - error at ffmpeg: ' + str(sys.exc_info()))

    ioutils.elapsedTime(dto)


# - - - - - # - - - - - #
@main.command(help='Path for fileMerging, not file')

# arguments
@click.argument('newformat', nargs=1)
@click.argument('paths', nargs=-1)

def mergeFiles(paths, newformat):
    for path in paths:
        functions.func_ffmpegDirMerge(dto, path, newformat)


# - - - - - # - - - - - # divideAndConquer command
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
            if downloader.download_aria2c(dto, itemList, dir) == 0:
                for i in itemList:
                    urlCopy.remove(i)

                dto.publishLoggerDebug('removed: ' + str(itemList) + ' | rest list ' + str(urlCopy))

        except KeyboardInterrupt:
            with safer.open(file, 'w') as f:
                for url in urlCopy:
                    f.write('%s\n' % url)
            dto.publishLoggerWarn('Interupt by User')
            ioutils.elapsedTime(dto)
            os._exit(1)
            break

        except:
            dto.publishLoggerError('divideAndConquer - error at list: ' + str(sys.exc_info()))

        finally:
            # will always be executed last, with or without exception
            with safer.open(file, 'w') as f:
                for url in urlCopy:
                    f.write('%s\n' % url)

    ioutils.elapsedTime(dto)


# - - - - - # - - - - - # wget
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

    workflow_wget.wget(dto, wget)


# - - - - - # - - - - - # youtube-dl
@main.command(help='Enter an URL for YoutubeDL')

#String
@click.option('-os', '--offset', default=0, help='String Offset')

# arguments
@click.argument('url', nargs=-1)
def ydl(url, offset):
    dto.setOffset(offset)

    workflow_ydl.ydl(dto, url)


# - - - - - # - - - - - # Anime
@main.command(help='Enter an URL for YoutubeDL')

#String
@click.option('-g', '--group', default='re', help='Sub Group')
@click.option('-s', '--show', default='', help='Anime Show')
@click.option('-q', '--quality', default='1080', help='Video Quality')
@click.option('-a', '--start', default='1', help='first Episode')
@click.option('-z', '--end', default='12', help='last Episode')
@click.option('-d', '--dir', default='', help='Path to be downloaded')

#Switch
@click.option('-f', '--file', default=False, is_flag=True, help='download .torrent files')

def anime(group, show, quality, start, end, file, dir):
    workflow_animescrapper.anime(dto, group, show, quality, start, end, file, dir)


# - - - - - # - - - - - # main
if __name__ == '__main__':
    main()