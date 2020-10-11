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
from exitstatus import ExitStatus


# --------------- # help functions

# ----- # ----- # titleFormating
def getTitleFormated(title):
    newTitle = ""

    if title == "":
        now = datetime.now()
        newTitle = "dl_" + now.strftime("%m-%d-%Y_%H-%M-%S")
        return newTitle
    else:
        newTitle = title

    newTitle = newTitle.casefold().replace(" ", "-").replace("_","-").replace("/","").replace("`", "-").replace(".","").replace(":","")

    while newTitle.endswith('-'):
        newTitle = newTitle[:-1]

    while newTitle.startswith('-'):
        newTitle = newTitle[1:]

    return newTitle


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

    print("finished\n")


# ----- # ----- # updating moduls
def update():
    print('Updating Packages')

    path = os.path.join(pathToRoot, 'requirements.txt')
    command = ['pip3', 'install', '-r', path]

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
  req = urllib.request.Request(url, headers = {"User-Agent": "Mozilla/5.0"})
  try:
        conn = urllib.request.urlopen(req)
  except urllib.error.HTTPError as e:
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

    path = os.getenv('PATH').split(":")
    # print(path)
    for subPath in path:
        pathTest = subprocess.check_output(['find', subPath, '-name', 'dl.py']).decode('utf-8')
        if pathTest != "":
            pathToRoot = pathTest
            # print(pathToRoot)
            break

    pathToRoot = pathToRoot.replace("dl.py","").rstrip('\n')


# --------------- # main functions
@click.group()
@click.option("-a", "--axel", default=False, is_flag=True, help="Using Axel")
@click.option("--retries", default=5, help="Enter an Number for Retries")
@click.option("--min-sleep", default=2, help="Enter an Number for min-Sleep between retries/ downloads")
@click.option("--max-sleep", default=15, help="Enter an Number for max-Sleep between retries/ downloads")
@click.option("-bw","--bandwidth", default="0", help="Enter an Bandwidthlimit like 1.5M")
def main(retries, min_sleep, max_sleep, bandwidth, axel):
    getRootPath()
    # update()
    loadConfig()

    global parameters
    global wget_bandwidth

    wget_bandwidth = bandwidth

    parameters = "--retries {retries} --min-sleep-interval {min_sleep} --max-sleep-interval {max_sleep} -c".format(retries=retries, min_sleep=min_sleep, max_sleep=max_sleep)

    if bandwidth != "0":
        parameters = parameters + " --limit-rate {}".format(bandwidth)

    if axel:
        parameters = parameters + " --external-downloader axel"


# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - #       wget-download   # - - - - - #
# - - - - - #                       # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #
# - - - - - # - - - - - # - - - - - # - - - - - #


# ----- # ----- # single url
@main.command(help="Enter an URL")
@click.argument('wget', nargs=-1)
def wget(wget):
    repeat = True

    while repeat:
        if wget != "":
            for item in wget:
                print(item)
                download_wget_single(item)
            wget = ""
        else:
            try:
                url = input("\nPlease enter the Url:\n")
                download_wget_single(url)
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


# ----- # ----- # url list
@main.command(help="Enter an List with URL for wget Sync")
@click.argument("list_wget", nargs= -1)
@click.option("--bandwidth", default="0", help="Enter an Bandwidthlimit like 1.5M")
def list_wget(list_wget, bandwidth):
    for dList in list_wget:
        with safer.open(dList) as f:
            urlList = f.readlines()
            urlList = [x.strip() for x in urlList]

    urlCopy = urlList.copy()

    try:
        for item in urlCopy:
            if item != "" :
                print(item)

                if download_wget(str(item)) == 0:
                    urlList.remove(item)
                    print("removed: " + str(item) + " | rest list " + str(urlList))

    except KeyboardInterrupt:
        print("\nInterupt by User\n")
        with safer.open(dList, 'w') as f:
            for url in urlList:
                f.write("%s\n" % url)
        exit()

    except:
        print("error: " + sys.exc_info()[0])

    finally:
        # will always be executed last, with or without exception
        with safer.open(dList, 'w') as f:
            for url in urlList:
                f.write("%s\n" % url)
        sys.exit(ExitStatus.success)


# ----- # ----- # url list for livedisks
@main.command(help="Enter an List with URL for LiveDisk Sync")
@click.argument("list_livedisc", nargs= -1)
@click.option("--bandwidth", default="0", help="Enter an Bandwidthlimit like 1.5M")
def list_livedisk(list_livedisc, bandwidth):
    for dList in list_livedisc:
        with safer.open(dList) as f:
            urlList = f.readlines()
            urlList = [x.strip() for x in urlList]

    try:
        random.shuffle(urlList)
        for item in urlList:
            if item != "" :
                print("download: " + item)
                download_wget(str(item),bandwidth)

    except KeyboardInterrupt:
        print("\nInterupt by User\n")
        exit()

    except:
        print("error: " + sys.exc_info()[0])

    finally:
        sys.exit(ExitStatus.success)


# ----- # ----- # single download
# TODO
def download_wget_single(content):
    try:
        path = os.getcwd()
        wget = 'wget -P {dir} -r -c -w 5 --random-wait --no-http-keep-alive --limit-rate={bw} -e robots=off -np -nd -nH -A "*.iso" -A "*.raw.xz" {url}'.format(dir=path,url=content, bw=wget_bandwidth)

        # file size
        fileSize = subprocess.getoutput('wget "' + content + '" --spider --server-response -O - 2>&1| sed -ne "/Content-Length/{s/.*: //;p}"')
        # print(bytes2human(int(fileSize)))

        # free storage
        freeStorage = shutil.disk_usage(path).free
        # print(bytes2human(int(freeStorage)))

        if (int(freeStorage) >= int(fileSize)):

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
                        print("sleep for " + str(timer) + "s")
                        time.sleep(timer)

                        if i == 3:
                            print("This was the Command: \n%s" % wget)
                            return returned_value

                else:
                    removeFiles(path, file_count_prev)
                    return returned_value

        else:
            print("\nnot enough space")
            print("Directory size: " + bytes2human(int(fileSize)))
            print("free Space: " + bytes2human(int(freeStorage)))
            removeFiles(path, file_count_prev)
            return 507

    except KeyboardInterrupt:
        print("\nInterupt by User\n")
        exit()

    except:
        print("error: " + sys.exc_info()[0])


# ----- # ----- # multi download
def download_wget(content,bandwidth):
    try:
        if ";" in content:
            swap = content.split(";")
            content = swap[0]
            directory = swap[1]
        else:
            directory = ""

        path = os.path.join(os.getcwd(),directory)
        wget = 'wget -P {dir} -r -c -w 5 --random-wait --no-http-keep-alive --limit-rate={bw} -e robots=off -np -nd -nH -A "*.iso" -A "*.raw.xz" {url}'.format(dir=path,url=content, bw=bandwidth)

        # file count
        path, dirs, files = next(os.walk(path))
        file_count_prev = len(files)

        # dir size
        size = subprocess.check_output(['du','-s', path]).split()[0].decode('utf-8')

        # free storage
        freeStorage = shutil.disk_usage(path).free/1000

        if (int(freeStorage) >= int(size)):

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
                        print("sleep for " + str(timer) + "s")
                        time.sleep(timer)

                        if i == 3:
                            print("This was the Command: \n%s" % wget)
                            return returned_value

                else:
                    removeFiles(path, file_count_prev)
                    return returned_value

        else:
            print("\nnot enough space")
            print("Directory size: " + bytes2human(int(size)*1000))
            print("free Space: " + bytes2human(freeStorage*1000))
            removeFiles(path, file_count_prev)
            return 507

    except KeyboardInterrupt:
        print("\nInterupt by User\n")
        exit()

    except:
        print("error: " + sys.exc_info()[0])


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
@main.command(help="Enter an URL")
@click.argument('url', nargs=-1)
def url(url):
    repeat = True

    while repeat:
        if url != "":
            for item in url:
                print(url)
                print(item)
                extractor(item)
            url = ""
        else:
            try:
                url = input("\nPlease enter the Url:\n")
                extractor(url)
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
@main.command(help="Enter an List with URL for Youtube-DL")
@click.argument("list_youtube_dl", nargs= -1)
def list_youtube_dl(list_youtube_dl):
    for dList in list_youtube_dl:
        with safer.open(dList) as f:
            urlList = f.readlines()
            urlList = [x.strip() for x in urlList]

    urlCopy = urlList.copy()
    print("list: " + str(urlCopy))

    try:
        for item in urlCopy:
            if item != "" :
                print(item)

                if extractor(str(item)) == 0:
                    urlList.remove(item)
                    print("removed: " + str(item) + " | rest list " + str(urlList))

    except KeyboardInterrupt:
        print("\nInterupt by User\n")
        with safer.open(dList, 'w') as f:
            for url in urlList:
                f.write("%s\n" % url)
        exit()

    except:
        print("error: " + sys.exc_info()[0])

    finally:
        # will always be executed last, with or without exception
        with safer.open(dList, 'w') as f:
            for url in urlList:
                f.write("%s\n" % url)
        sys.exit(ExitStatus.success)


# ----- # ----- # extractors
def extractor(content):
    webpageResult = testWebpage(content)
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
    if ("anime-on-demand" in content) : return host_animeondemand(content)
    if ("vimeo" in content) : return host_vimeo(content)
    if ("cloudfront" in content) : return host_cloudfront(content)

    return host_default(content)


# --------------- # media hoster

# ----- # ----- # hosts
def host_default(content):
    output = '-f best -o "%(title)s.%(ext)s"'
    return download_youtube_dl(content, parameters, output)

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
    return download_youtube_dl(content, parameters, output)


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
    return download_youtube_dl(url, parameters, output)

# -----
def host_hanime(content):
    title = content.rsplit('?',1)[0].rsplit('/',1)[1]
    title = getTitleFormated(title)
    output = '-f best -o "{title}.%(ext)s"'.format(title=title)
    return download_youtube_dl(content, parameters, output)

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
    return download_youtube_dl(url, parameters, output)

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
    return download_youtube_dl(content, parameters, output)

# -----
def host_xvideos(content):
    title = content.rsplit("/",1)[1]
    title = getTitleFormated(title)
    output = '-f best -o "{title}.mp4"'.format(title=title)
    return download_youtube_dl(content, parameters, output)

# -----
def host_porngo(content):
    title = content.rsplit('/',1)[0].rsplit('/',1)[1]
    title = getTitleFormated(title)
    output = '-f best -o "{title}.%(ext)s"'.format(title=title)
    return download_youtube_dl(content, parameters, output)


# --------------- # Anime
def host_animeondemand(content):
    for p in data['animeondemand']:
        parameter = "-u " + p['username'] + " -p " + p['password'] + " " + parameters

    if "www." not in content:
        swap = content.split('/', 2)
        content = "https://www." + swap[2]

    output = "-f 'best[format_id*=ger-Dub]' -o '%(playlist)s/episode-%(playlist_index)s.%(ext)s'"
    return download_youtube_dl(content, parameter, output)

# -----
def host_wakanim(content):
    for p in data['wakanim']:
        parameter = "-u " + p['username'] + " -p " + p['password'] + " " + parameters

    if "www." not in content:
        swap = content.split('/', 2)
        content = "https://www." + swap[2]

    output = "-f 'best[format_id*=ger-Dub]' -o '%(playlist)s/episode-%(playlist_index)s.%(ext)s'"
    return download_youtube_dl(content, parameter, output)

# -----
def host_crunchyroll(content):
    for p in data['crunchyroll']:
        parameter = "-u " + p['username'] + " -p " + p['password'] + " " + parameters

    if "www." not in content:
        swap = content.split('/', 2)
        content = "https://www." + swap[2]

    output = "-f 'best[format_id*=ger-Dub]' -o '%(playlist)s/episode-%(playlist_index)s.%(ext)s'"
    return download_youtube_dl(content, parameter, output)


# --------------- # Plattformen
def host_udemy(content):
    for p in data['udemy']:
        parameter = "-u " + p['username'] + " -p " + p['password'] + " " + parameters

    title = content.split('/',4)[4].rsplit('/',5)[0]
    url = "https://www.udemy.com/" + title
    print(url)

    output = "-f best -o '%(playlist)s - {title}/%(chapter_number)s-%(chapter)s/%(playlist_index)s-%(title)s.%(ext)s'".format(title=title)
    return download_youtube_dl(url, parameter, output)

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
    return download_youtube_dl(content, parameters, output)

# -----
def host_cloudfront(content):
    if ";" in content:
        title = content.split(";",1)[1]
        content = content.split(";",1)[0]
    else:
        title = str(input("\nPlease enter the Title:\n"))

    title = getTitleFormated(title)
    output = '-f best -o "{title}.mp4"'.format(title=title)
    return download_youtube_dl(content, parameters, output)


# ----- # ----- # download
def download_youtube_dl(content, parameters, output):
    ydl = 'youtube-dl {parameter} {output} "{url}"'.format(parameter=parameters, output=output, url=content)

    i=0
    returned_value = ""

    while i < 3:

        print(ydl)
        returned_value = os.system(ydl)

        if returned_value > 0:
            i += 1
            timer = random.randint(200,1000)/100
            print("sleep for " + str(timer) + "s")
            time.sleep(timer)

            if i == 3:
                print("This was the Command: \n%s" % ydl)
                return returned_value
        else:
            return returned_value


# --------------- # main
if __name__ == "__main__":
    main()
