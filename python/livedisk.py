#!/bin/env python3

import os
import random
import re
import shutil
import subprocess
import sys
import time
import datetime

import click
import safer
from exitstatus import ExitStatus


@click.group()
def main():
    print("Starting Syncing")

@main.command(help="Enter an List with URL for LiveDisk Sync")
@click.argument("list_livedisc", nargs= -1)
@click.option("--bandwidth", default="0", help="Enter an Bandwidthlimit like 1.5M")
def ld_list(list_livedisc, bandwidth):
    for dList in list_livedisc:
        with safer.open(dList) as f:
            urlList = f.readlines()
            urlList = [x.strip() for x in urlList]

    try:
        random.shuffle(urlList)
        for item in urlList:
            if item != "" :
                print("download: " + item)
                download_livedisk(str(item),bandwidth)

    except KeyboardInterrupt:
        print("\nInterupt by User\n")
        exit()

    except:
        print("error: " + sys.exc_info()[0])

    finally:
        sys.exit(ExitStatus.success)

# --------------- # helper # --------------- #
def getTitleFormated(title):
    newTitle = ""

    if title == "":
        now = datetime.now()
        newTitle = "livedisk_" + now.strftime("%m-%d-%Y_%H-%M-%S")
        return newTitle
    else:
        newTitle = title

    newTitle = newTitle.casefold().replace(" ", "-").replace("_","-").replace("/","")

    while newTitle.endswith('-'):
        newTitle = newTitle[:-1]

    while newTitle.startswith('-'):
        newTitle = newTitle[1:]

    return newTitle

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

# --------------- # download # --------------- #
def download_livedisk(content,bandwidth):
    try:
        if ";" in content:
            swap = content.split(";")
            content = swap[0]
            directory = swap[1]
        else:
            directory = ""

        path = os.path.join(os.getcwd(),directory)
        wget = 'wget -P {dir} -r -c -w 5 --random-wait --no-http-keep-alive --limit-rate={bw} -e robots=off -np -nd -nH -A "*.iso" -A "*.raw.xz" {url}'.format(dir=path,url=content, bw=bandwidth)
        regex = re.compile('[^0-9.]')

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

# --------------- # download # --------------- #
if __name__ == "__main__":
    main()
