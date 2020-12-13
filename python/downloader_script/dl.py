#!/usr/bin/env python3

import datetime
import os
import random
import re
import sys
import time
import urllib.request
import subprocess
import shutil
import click
import safer
import bs4
import json
import youtube_dl
import ffmpeg

from exitstatus import ExitStatus


# --------------- # help functions

# ----- # ----- # title
def getTitleFormated(title):
    newTitle = ""

    if title == "":
        now = datetime.now()
        newTitle = "dl_" + now.strftime("%m-%d-%Y_%H-%M-%S")
        return newTitle
    else:
        newTitle = title

    newTitle = formatingFilename(newTitle)

    while newTitle.endswith('-'):
        newTitle = newTitle[:-1]

    while newTitle.startswith('-'):
        newTitle = newTitle[1:]

    return newTitle


# ----- # ----- # format files
def formatingFilename(text):
    reg = re.compile(r"[^\w\d\s\-\_\/\.]")
    reg3 = re.compile(r"-{3,}")

    extensionsList = [
                        '.mp4', '.mkv', '.avi', '.m4a', '.mov',
                        '.flac', '.wav', '.mp3', '.aac',
                        '.py', '.txt', '.md', '.pdf', '.doc', 'docx',
                        '.iso', '.zip', '.rar',
                        '.jpg', '.jpeg', '.svg', '.png',
                        '.csv', '.html', '.ppt', '.pptx', '.xls', '.xlsx'
                    ]

    swap = text.casefold()

    swap = re.sub(reg, '', swap)

    if any(ext in swap for ext in extensionsList):
        fileSwap = swap.rsplit(".",1)
        swap = fileSwap[0].replace("/","").replace(".","") + '.' + fileSwap[1]
    else:
        swap = swap.replace("/","").replace(".","")

    swap = swap.replace(" ", "-").replace("_","-")

    swap = re.sub(reg3, "§", swap)
    swap = swap.replace("--", "-")
    swap = swap.replace("§", "---")

    return swap

# ----- # ----- # format folder
def formatingDirectories(text):
    reg = re.compile(r"[^\w\d\s\-\_\/\.]")
    reg3 = re.compile(r"-{3,}")

    swap = text.casefold()
    swap = re.sub(reg, '', swap)
    swap = swap.replace(" ", "-").replace("_","-")

    swap = re.sub(reg3, "§", swap)
    swap = swap.replace("--", "-")
    swap = swap.replace("§", "---")

    return swap


# ----- # ----- # human readable storage info
def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


# ----- # ----- # removing outdated files
def removeFiles(path, file_count_prev):
    if not booleanRemoveFiles:
        print("\nRemoving old files")

        # file count
        path, dirs, files = next(os.walk(path))
        file_count = len(files)

        print("files before: " + str(file_count_prev))
        print("files after: " + str(file_count))

        if (file_count > file_count_prev):
            files = []
            index = 0
            for f in os.listdir(path):
                index += 1
                if ( os.stat(os.path.join(path,f)).st_mtime < (datetime.datetime.now().timestamp() - (6 * 30 * 86400)) ):
                    files.append(os.path.join(path,f))

            print(files)
            print(index)

            if index > len(files):
                for i in files:
                    print("removing: " + i)
                    os.remove(os.path.join(path, i))

        else:
            files = []
            index = 0
            for f in os.listdir(path):
                index += 1
                if ( os.stat(os.path.join(path,f)).st_mtime < (datetime.datetime.now().timestamp() - (12 * 30 * 86400)) ):
                    files.append(os.path.join(path,f))

            print(files)
            print(index)

            if index > len(files):
                for i in files:
                    print("removing: " + i)
                    os.remove(os.path.join(path, i))

        print("finished Removing\n")


# ----- # ----- # updating moduls
def update():
    print('Updating Packages')

    path = os.path.join(pathToRoot, 'requirements.txt')
    command = ['pip3', 'install', '-U', '-r', path]

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    output, error = proc.communicate()

    print(output.decode('ascii'))
    print(error.decode('ascii'))


# ----- #
def loadConfig():
    global data

    path = os.path.join(pathToRoot, 'env')

    with open(path) as json_file:
        data = json.load(json_file)


# ----- #
def testWebpage(url):
    print(url)
    req = urllib.request.Request(url, headers = {"User-Agent": "Mozilla/5.0"})
    try:
        conn = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return 0

        print('HTTPError: {}'.format(e.code))
        return e.code
    except urllib.error.URLError as e:
        print('URLError: {}'.format(e.reason))
        return e.code
    else:
        return 0


# ----- #
def getRootPath():
    global pathToRoot
    pathToRoot = ""

    try:
        path = os.getenv('PATH').split(":")
        # print(path)
        for subPath in path:
            pathTest = subprocess.check_output(['find', subPath, '-name', 'dl.py']).decode('utf-8')
            if pathTest != "":
                pathToRoot = pathTest
                break

        pathToRoot = pathToRoot.replace("dl.py","").rstrip('\n')
    except:
        pathToRoot = os.getcwd()


# ----- #
def getUserCredentials(platform):
    credentialList = ['animeondemand', 'udemy']

    if platform in credentialList:
        for p in data['animeondemand']:
            parameter = "-u '" + p['username'] + "' -p '" + p['password'] + "' " + parameters

    if cookieFile:
        parameter = "--cookies '" + cookieFile + "' " + parameters

    return parameter


# ----- #
def getLanguage(platform):
    output = "--no-mark-watched --hls-prefer-ffmpeg --socket-timeout 30 "

    if platform == "crunchyroll":
        if subLang == "de": return output + "-f 'best[format_id*=adaptive_hls-audio-jpJP-hardsub-deDE]'"
        if dubLang == "de": return output + "-f 'best[format_id*=adaptive_hls-audio-deDE][format_id!=hardsub]'"


# ----- #
def elapsedTime():
    time_elapsed = datetime.datetime.now() - start_time
    print('\nTime elapsed (hh:mm:ss.ms): {}'.format(time_elapsed))


# ----- #
def renameEpisode(season, episode, title, seasonOffset):

    f = "s"
    if len(season) == 1:
        f += "0" + str( int(season) + int(seasonOffset))
    else:
        f += str( int(season) + int(seasonOffset))

    f += "e"
    if len(episode) == 1:
        f += "0" + episode
    else:
        f += episode
    f += "-" + title

    return f


# ----- #
def func_rename(filePath, platform, offset, cut):
    if os.path.isfile(filePath):
        old = os.path.join(os.getcwd(),filePath)
        new = os.path.join(os.getcwd(),formatingFilename(filePath))
        os.rename(old, new)
    else:
        try:
            path, dirs, files = next(os.walk(filePath))
        except:
            print("could the path be wrong?")

        for directory in dirs:
            func_rename(os.path.join(filePath, directory), platform, offset, cut)

        for f in os.listdir(path):
            old = os.path.join(path,f)
            f = f[offset:]
            # f = f[:cut]

            seasonOffset = 0
            if booleanSingle:
                seasonOffset = 1

            if platform == "crunchyroll":
                fSwap = formatingFilename(f).split("-", 4)
                f = renameEpisode(fSwap[1], fSwap[3], fSwap[4], 1)

            new = os.path.join(path,formatingFilename(f))
            os.rename(old, new)

        try:
            os.rename(filePath, formatingDirectories(filePath))
        except:
            pass


# ----- #
def func_replace(filePath, old, new):
    try:
        path, dirs, files = next(os.walk(filePath))
    except:
        print("could the path be wrong?")

    for directory in dirs:
        func_replace(os.path.join(filePath, directory), old, new)

    for f in os.listdir(path):
        oldFile = os.path.join(path,f)
        f = f.replace(old, new)
        newFile = os.path.join(path,formatingFilename(f))
        os.rename(oldFile, newFile)

    try:
        os.rename(filePath, formatingDirectories(filePath))
    except:
        pass


# ----- #
def convertFilesFfmpeg(fileName, newFormat, subPath):
    newFile = fileName.rsplit(".", 1)[0]
    output = ""

    if subPath:
        if "/" in newFile:
            newFile = newFile.rsplit("/", 1)
            path = newFile[0] + "/" + subPath

            if not os.path.exists(path):
                os.makedirs(path)

            output = path + "/" + newFile[1]
        else:
            if not os.path.exists(subPath):
                os.makedirs(subPath)

            output = subPath + "/" + newFile
    else:
        output = newFile

    ffmpeg.input(fileName).output(output + "." + newFormat).run()


# --------------- # main functions
@click.group()

# switch
@click.option("-a", "--axel", default=False, is_flag=True, help="Using Axel")
@click.option("-p", "--playlist", default=False, is_flag=True, help="Playlist")
@click.option("-nr", "--no-remove", default=False, is_flag=True, help="remove Files at wget")
@click.option("-up", "--update-packages", default=False, is_flag=True, help="updates packages listed in requirements.txt")

# int
@click.option("--retries", default=5, help="Enter an Number for Retries")
@click.option("--min-sleep", default=2, help="Enter an Number for min-Sleep between retries/ downloads")
@click.option("--max-sleep", default=15, help="Enter an Number for max-Sleep between retries/ downloads")
@click.option("-bw","--bandwidth", default="0", help="Enter an Bandwidthlimit like 1.5M")

# string
@click.option("-cf","--cookie-file", default="", help="Enter Path to cookie File")
@click.option("-sl","--sub-lang", default="", help="Enter language Code (de / en)")
@click.option("-dl","--dub-lang", default="", help="Enter language Code (de / en)")

def main(retries, min_sleep, max_sleep, bandwidth, axel, cookie_file, sub_lang, dub_lang, playlist, no_remove, update_packages):

    getRootPath()

    if update_packages:
        update()

    loadConfig()

    global parameters
    global floatBandwidth
    global cookieFile
    global subLang
    global dubLang
    global booleanPlaylist
    global booleanRemoveFiles

    floatBandwidth = bandwidth
    cookieFile = cookie_file
    subLang = sub_lang
    dubLang = dub_lang
    booleanPlaylist = playlist
    booleanRemoveFiles = no_remove

    parameters = "--retries {retries} --min-sleep-interval {min_sleep} --max-sleep-interval {max_sleep} -c".format(retries=retries, min_sleep=min_sleep, max_sleep=max_sleep)

    if bandwidth != "0":
        parameters = parameters + " --limit-rate {}".format(bandwidth)

    if axel:
        parameters = parameters + " --external-downloader axel"


# ----- # ----- # rename command
@main.command(help="Path for rename, not file")

# switch
@click.option("-os", "--offset", default=0, help="String Offset")
@click.option("-c", "--cut", default=0, help="Cut String")
@click.option("-cr", "--crunchyroll", default=False, is_flag=True, help="syntax Crunchyroll")
@click.option("-s", "--single", default=False, is_flag=True, help="series is only one Season")

# arguments
@click.argument('rename', nargs=-1)
def rename(rename, offset, cut, crunchyroll, single):
    platform = ""

    global booleanSingle
    booleanSingle = single

    if crunchyroll:
        platform = "crunchyroll"

    for itemPath in rename:
        func_rename(itemPath, platform, offset, cut)


# ----- # ----- # replace command
@main.command(help="Path, old String, new String")

# switch
@click.option("-o", "--old", default="", help="old String")
@click.option("-n", "--new", default="", help="new String")

# arguments
@click.argument('replace', nargs=-1)
def replace(replace, old, new):
    for itemPath in replace:
        func_replace(itemPath, old, new)


# ----- # ----- # convertFiles command
@main.command(help="Path for rename, not file")

# switch
@click.option("-f", "--ffmpeg", default=False, is_flag=True, help="ffmpeg")
@click.option("-sp", "--subpath", default="", help="Path which will contain the new Files")

# arguments
@click.argument("newformat", nargs=1)
@click.argument("path", nargs=-1)
def convertFiles(newformat, path, subpath, ffmpeg):
    if ffmpeg:
        for itemPath in path:
            sPath = formatingDirectories(itemPath)
            func_rename(itemPath, "", 0, 0)

            try:
                paths, dirs, files = next(os.walk(sPath))

                for f in os.listdir(paths):
                    old = os.path.join(paths,f)
                    convertFilesFfmpeg(old, newformat, subpath)
            except:
                if os.path.isfile(os.path.join(os.getcwd(),sPath)):
                    convertFilesFfmpeg(sPath, newformat, subpath)


# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - #       wget-download   # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #


# ----- # ----- # wget
@main.command(help="Enter an URL")

# switch
@click.option("-sp", "--space", default=False, is_flag=True, help="check if old file are deletable")
@click.option("-sy", "--sync", default=False, is_flag=True, help="")

# arguments
@click.argument('wget', nargs=-1)
def wget(wget, space, sync):
    global booleanSpace
    global booleanSync
    booleanSpace = space
    booleanSync = sync

    repeat = True

    while repeat:
        if wget != "":
            for item in wget:
                if os.path.isfile(item):
                    wget_list(item)
                else:
                    wget_download(item)

            wget = ""
            elapsedTime()

        else:
            try:
                url = input("\nPlease enter the Url:\n")
                wget_download(url)

            except KeyboardInterrupt:
                pass

        try:
            answer = input("\nDo you wish another Turn? (y | n):\n")
            if ("y" in answer) :
                repeat = True
                wget = ""
            else:
                repeat = False

        except KeyboardInterrupt:
            repeat = False


# -----
def wget_list(itemList):
    with safer.open(itemList) as f:
        urlList = f.readlines()
        urlList = [x.strip() for x in urlList]

    urlCopy = urlList.copy()

    if booleanSync:
        random.shuffle(urlCopy)

    try:
        for item in urlCopy:
            if item != "" :
                if item.startswith('#'):
                    urlList.remove(item)
                    continue

                print("download: " + item)

                if booleanSync:
                    wget_download(str(item))
                else:
                    if wget_download(str(item)) == 0:
                        urlList.remove(item)
                        print("\nremoved: " + str(item) + " | rest list " + str(urlList))
            else:
                urlList.remove(item)

    except KeyboardInterrupt:
        if booleanSync:
            print("\nInterupt by User\n")
            exit()
        else:
            print("\nInterupt by User\n")
            with safer.open(itemList, 'w') as f:
                for url in urlList:
                    f.write("%s\n" % url)
            exit()

    except:
        print("error: " + str(sys.exc_info()))

    finally:
        # will always be executed last, with or without exception
        with safer.open(itemList, 'w') as f:
            for url in urlList:
                f.write("%s\n" % url)

        elapsedTime()
        sys.exit(ExitStatus.success)


# -----
def wget_download(content):
    try:
        if ";" in content:
            swap = content.split(";")
            content = swap[0]
            directory = swap[1]
        else:
            directory = ""

        path = os.path.join(os.getcwd(),directory)

        wget = 'wget -P {dir} -c -w 5 --random-wait --limit-rate={bw} -e robots=off "{url}"'.format(dir=path,url=content, bw=floatBandwidth)

        # --no-http-keep-alive

        if booleanSync:
            wget = wget + ' -r --no-cache -np -nd -nH -A iso,xz'

        # file count
        path, dirs, files = next(os.walk(path))
        file_count_prev = len(files)

        # dir size
        dirSize = subprocess.check_output(['du','-s', path]).split()[0].decode('utf-8')

        # free storage
        freeStorage = shutil.disk_usage(path).free

        try:
            # file size
            fileSize = subprocess.getoutput('wget "' + content + '" --spider --server-response -O - 2>&1| sed -ne "/Content-Length/{s/.*: //;p}"')
            testSize = int(fileSize)
        except:
            testSize = dirSize

        if (int(freeStorage) >= int(testSize)):

            i=0
            returned_value = ""

            while i < 3:
                returned_value = os.system("echo \'" + wget + "\' >&1 | bash")

                if returned_value > 0:
                    if returned_value == 2048:
                        return returned_value
                    else:
                        print("Error Code: " + str(returned_value))
                        i += 1
                        timer = random.randint(200,1000)/100
                        print("\nsleep for " + str(timer) + "s")
                        time.sleep(timer)

                        if i == 3:
                            print("\nThe was the Command: \n%s" % wget)
                            return returned_value

                else:
                    if booleanSpace:
                        removeFiles(path, file_count_prev)
                    return returned_value

        else:
            print("\nnot enough space")
            print("Directory size: " + bytes2human(int(dirSize)*1000))
            print("free Space: " + bytes2human(freeStorage))

            if booleanSpace:
                removeFiles(path, file_count_prev)
            return 507

    except KeyboardInterrupt:
        print("\nInterupt by User\n")
        exit()

    except:
        print("error: " + str(sys.exc_info()))


# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - #   youtube-download    # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #

# ----- # ----- # single URL
@main.command(help="Enter an URL for YoutubeDL")

# arguments
@click.argument('url', nargs=-1)
def ydl(url):
    repeat = True

    while repeat:
        if url != "":
            for item in url:
                if os.path.isfile(item):
                    ydl_list(item)
                else:
                    ydl_extractor(item)

            url = ""
            elapsedTime()

        else:
            try:
                url = input("\nPlease enter the Url:\n")
                ydl_extractor(url)

            except KeyboardInterrupt:
                pass

        try:
            answer = input("\nDo you wish another Turn? (y | n):\n")
            if ("y" in answer) :
                repeat = True
                url = ""
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
    print("list: " + str(urlCopy))

    try:
        for item in urlCopy:
            if item != "" :
                if item.startswith('#'):
                    continue

                print("\ncurrent Download: " + item)

                if ydl_extractor(str(item)) == 0:
                    urlList.remove(item)
                    print("removed: " + str(item) + " | rest list " + str(urlList))
            else:
                urlList.remove(item)

    except KeyboardInterrupt:
        print("\nInterupt by User\n")
        with safer.open(itemList, 'w') as f:
            for url in urlList:
                f.write("%s\n" % url)
        exit()

    except:
        print("error: " + str(sys.exc_info()))

    finally:
        # will always be executed last, with or without exception
        with safer.open(itemList, 'w') as f:
            for url in urlList:
                f.write("%s\n" % url)
        sys.exit(ExitStatus.success)
        elapsedTime()


# ----- # ----- # download
def ydl_download(content, parameters, output):
    ydl = 'youtube-dl {parameter} {output} "{url}"'.format(parameter=parameters, output=output, url=content)

    i=0
    returned_value = ""

    while i < 3:

        returned_value = os.system(ydl)
        print(returned_value)

        if returned_value > 0:
            i += 1
            timer = random.randint(200,1000)/100
            print("\nsleep for " + str(timer) + "s")
            time.sleep(timer)

            if i == 3:
                print("\nThe was the Command: \n%s" % ydl)
                return returned_value
        else:
            return returned_value


# ----- # ----- # extractors
def ydl_extractor(content):
    webpageResult = testWebpage(content.split(";")[0].split("?")[0])
    if webpageResult != 0:
        return webpageResult

    mostly = ['fruithosted', 'oloadcdn', 'verystream', 'vidoza', 'vivo']

    for domain in mostly:
        if domain in content : return host_mostly(content)

    if ("animeholics" in content) : return host_animeholics(content)

    if ("haho.moe" in content) :
        if (len(content.rsplit("/",1)[1]) < 3):
            return host_hahomoe(content)
        else:
            i = 1
            while testWebpage(content+"/"+str(i)) == 0:
                extractor(content+"/"+str(i))
                i=i+1

            i = 1
            while testWebpage(content+"/s"+str(i)) == 0:
                extractor(content+"/s"+str(i))
                i=i+1

            return 0

    if ("sxyprn" in content) : return host_sxyprn(content)
    if ("porngo" in content) : return host_porngo(content)
    if ("xvideos" in content) : return host_xvideos(content)

    if ("udemy" in content) : return host_udemy(content)
    if ("crunchyroll" in content) : return host_crunchyroll(content)
    if ("anime-on-demand" in content) : return host_animeondemand(content)
    if ("vimeo" in content) : return host_vimeo(content)
    if ("cloudfront" in content) : return host_cloudfront(content)

    return host_default(content)


# --------------- # media hoster

# ----- # ----- # hosts
def host_default(content):
    if not booleanPlaylist:
        ydl_opts = {
            'outtmpl': '%(title)s',
            'restrictfilenames': True,
            'forcefilename':True
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(content, download=False)
                filename = ydl.prepare_filename(info)
                print(filename)

            filename = getTitleFormated(filename)

            output = '-f best --no-playlist -o "{title}.%(ext)s"'.format(title = filename)
            return ydl_download(content, parameters, output)
        except:
            output = '-f best --no-playlist -o "%(title)s.%(ext)s"'
            return ydl_download(content, parameters, output)

    else:
        output = '-i -f best -o "%(extractor)s--%(playlist_uploader)s_%(playlist_title)s/%(playlist_index)s_%(title)s.%(ext)s"'
        return ydl_download(content, parameters, output)


# -----
# fruithosted, oloadcdn, verystream, vidoza, vivo,
def host_mostly(content):
    if ";" in content:
        title = content.split(";",1)[1]
        content = content.split(";",1)[0]
    else:
        title = str(input("\nPlease enter the Title:\n"))

    title = getTitleFormated(title)
    output = '-f best -o "{title}.%(ext)s"'.format(title=title)
    return ydl_download(content, parameters, output)


# --------------- # ...
def host_animeholics(content):
    url=content
    webpage=""

    req = urllib.request.Request(url, headers = {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        webpage = response.read()

    url = str(webpage)[str(webpage).find("https://filegasm.com/watch/"):int(str(webpage).find("https://filegasm.com/watch/"))+43]

    x = re.search('/\d/$|/s\d/$', content)
    if x:
        serie = content.rsplit('/',1)[0].rsplit('/',2)[1]
        episode = content.rsplit('/',1)[0].rsplit('/',2)[2]
    else:
        serie = content.rsplit('/',1)[0].rsplit('/',1)[1]
        episode = content.rsplit('/',1)[1]

    title = getTitleFormated(serie + "-" + episode)
    output = '-f best -o "{title}.%(ext)s"'.format(title=title)
    return ydl_download(url, parameters, output)


# -----
def host_hanime(content):
    title = content.rsplit('?',1)[0].rsplit('/',1)[1]
    title = getTitleFormated(title)
    output = '-f best -o "{title}.%(ext)s"'.format(title=title)
    return ydl_download(content, parameters, output)


# -----
def host_hahomoe(content):
    url=content
    webpage=""

    req = urllib.request.Request(url, headers = {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        webpage = response.read()

    urlRegex = re.compile('<source data-fluid-hd="" src="(.*?)" title="720p" type="video/mp4"></source>')
    m = urlRegex.search(str(webpage))
    if m:
        url = m.group(1)

    titleRegex = re.compile('<title>(.*?)</title>')
    m = titleRegex.search(str(webpage))
    if m:
        title = m.group(1).rsplit(' ',4)[0]
    else:
        title = ""

    title = getTitleFormated(title)
    output = '-f best -o "{title}.mp4"'.format(title=title)
    return ydl_download(url, parameters, output)


# -----
def host_sxyprn(content):
    url=content
    webpage=""

    req = urllib.request.Request(url, headers = {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        webpage = response.read()

    title = str(webpage).split('<title>')[1].split('</title>')[0]
    title = title.rsplit('-', 1)[0]
    title = title.casefold().replace(" ", "-").replace(".","").rsplit('-', 1)[0]

    if "#" in title:
        title = title.split('-#',1)[0]

    title = getTitleFormated(title)
    output = '-f best -o "{title}.%(ext)s"'.format(title=title)
    return ydl_download(content, parameters, output)


# -----
def host_xvideos(content):
    title = content.rsplit("/",1)[1]
    title = getTitleFormated(title)
    output = '-f best -o "{title}.mp4"'.format(title=title)
    return ydl_download(content, parameters, output)


# -----
def host_porngo(content):
    title = content.rsplit('/',1)[0].rsplit('/',1)[1]
    title = getTitleFormated(title)
    output = '-f best -o "{title}.%(ext)s"'.format(title=title)
    return ydl_download(content, parameters, output)


# --------------- # Anime
def host_animeondemand(content):
    parameter = getUserCredentials("animeondemand")

    if "www." not in content:
        swap = content.split('/', 2)
        content = "https://www." + swap[2]

    output = "-f 'best[format_id*=ger-Dub]' -o '%(playlist)s/episode-%(playlist_index)s.%(ext)s'"
    return ydl_download(content, parameter, output)


# -----
def host_crunchyroll(content):
    parameter = getUserCredentials("crunchyroll")
    output = str(getLanguage("crunchyroll"))

    if "www." not in content:
        swap = content.split('/', 2)
        content = "https://www." + swap[2]

    output += " -i -o '%(playlist)s/season-%(season_number)s-episode-%(episode_number)s-%(episode)s.%(ext)s'"
    return ydl_download(content, parameter, output)


# -----
def host_wakanim(content):
    for p in data['wakanim']:
        parameter = "-u '" + p['username'] + "' -p '" + p['password'] + "' " + parameters

    if "www." not in content:
        swap = content.split('/', 2)
        content = "https://www." + swap[2]

    output = "-f 'best[format_id*=ger-Dub]' -o '%(playlist)s/episode-%(playlist_index)s.%(ext)s'"
    return ydl_download(content, parameter, output)


# --------------- # platformen
def host_udemy(content):
    for p in data['udemy']:
        parameter = "-u '" + p['username'] + "' -p '" + p['password'] + "' " + parameters

    title = content.split('/',4)[4].rsplit('/',5)[0]
    url = "https://www.udemy.com/" + title
    print(url)

    output = "-f best -o '%(playlist)s - {title}/%(chapter_number)s-%(chapter)s/%(playlist_index)s-%(title)s.%(ext)s'".format(title=title)
    return ydl_download(url, parameter, output)


# -----
def host_vimeo(content):
    if ";" in content:
        swap = content.split(";")
        content = swap[0]
        title = swap[1]
        reference = swap[2]
    else:
        reference = str(input("\nPlease enter the reference URL:\n"))
        title = str(input("\nPlease enter the Title:\n"))

    content = content.split("?")[0]
    title = getTitleFormated(title)
    output = '--referer "{reference}" -f best -o "{title}.%(ext)s"'.format(reference=reference, title=title)
    return ydl_download(content, parameters, output)


# -----
def host_cloudfront(content):
    if ";" in content:
        title = content.split(";",1)[1]
        content = content.split(";",1)[0]
    else:
        title = str(input("\nPlease enter the Title:\n"))

    title = getTitleFormated(title)
    output = '-f best -o "{title}.mp4"'.format(title=title)
    return ydl_download(content, parameters, output)


# --------------- # main
if __name__ == "__main__":

    global start_time
    start_time = datetime.datetime.now()

    main()
