import json
import os
import re
import subprocess
from datetime import datetime

import requests

from dto import dto


# ----- # ----- #
def getRootPath(dto):
    pathToRoot = ''

    try:
        path = os.getenv('PATH').split(':')

        for subPath in path:
            pathTest = subprocess.check_output(['find', subPath, '-name', 'dl.py']).decode('utf-8')
            if pathTest != '':
                pathToRoot = pathTest
                break

        pathToRoot = pathToRoot.replace('dl.py','').rstrip('\n')
    except:
        pathToRoot = os.getcwd()


    dto.publishLoggerDebug('rootpath is: ' + pathToRoot)
    return pathToRoot


def update(dto, pathToRoot):
    dto.publishLoggerInfo('Updating Packages')

    path = os.path.join(pathToRoot + 'docs/', 'requirements.txt')
    command = ['pip3', 'install', '-U', '-r', path]

    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    output, error = proc.communicate()

    dto.publishLoggerDebug(output.decode('ascii'))
    dto.publishLoggerError(error.decode('ascii'))


def loadConfig(pathToRoot):
    path = os.path.join(pathToRoot, 'env')

    with open(path) as json_file:
        data = json.load(json_file)

    return data


# ----- # ----- #
def testWebpage(dto, url):
    if not dto.getSkipChecks():
        dto.publishLoggerDebug('webpage test for: ' + url)

        req = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})

        if req.status_code > 300:
            dto.publishLoggerDebug('HTTP Error: ' + str(req.status_code))
            return req.status_code

    return 0


# ----- # ----- # help
def getTitleFormated(title):
    newTitle = ''

    if title == '':
        now = datetime.now()
        newTitle = 'dl_' + now.strftime('%m-%d-%Y_%H-%M-%S')
        return newTitle
    else:
        newTitle = title

    newTitle = formatingFilename(newTitle)

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

    return '%sB' % n


def human2bytes(n):
    size = n[-1]

    switcher = {
        'B': 1,
        'K': 1000,
        'M': pow(1000,2),
        'G': pow(1000,3),
    }

    swapSize = float(n[:-1]) * switcher.get(size, 0)

    return '%s' % swapSize


# ----- # ----- # formating
def formatingDirectories(text):
    if text.startswith('.'):
        return

    reg = re.compile(r'[^\w\d\s\-\_\/\.\|]')
    reg3 = re.compile(r'-{3,}')

    swap = text.casefold()
    swap = re.sub(reg, '', swap)
    swap = swap.replace(' ', '-').replace('_','-').replace('+','-').replace('|', '-')

    swap = re.sub(reg3, '§', swap)
    swap = swap.replace('--', '-')
    swap = swap.replace('§', '---')

    return swap


def formatingFilename(text):
    reg = re.compile(r'[^\w\d\s\-\_\/\.+|]')
    reg3 = re.compile(r'-{3,}')

    extensionsList = [
                        '.mp4', '.mkv', '.avi', '.m4a', '.mov',
                        '.flac', '.wav', '.mp3', '.aac',
                        '.py', '.txt', '.md', '.pdf', '.doc', 'docx',
                        '.iso', '.zip', '.rar',
                        '.jpg', '.jpeg', '.svg', '.png',
                        '.csv', '.html', '.ppt', '.pptx', '.xls', '.xlsx',
                    ]

    swap = text.casefold()

    swap = re.sub(reg, '', swap)

    if any(ext in swap for ext in extensionsList):
        fileSwap = swap.rsplit('.',1)
        swap = fileSwap[0].replace('/','').replace('.','') + '.' + fileSwap[1]
    else:
        swap = swap.replace('/','').replace('.','')

    swap = swap.replace(' ', '-').replace('_','-').replace('+','-').replace('|','-')

    swap = re.sub(reg3, '§', swap)
    swap = swap.replace('--', '-')
    swap = swap.replace('§', '---')

    if any(ext in swap for ext in extensionsList):
        fileSwap = swap.rsplit('.',1)
        swap = getTitleFormated(fileSwap[0]) + '.' + fileSwap[1]

    return swap


# ----- # ----- # time measurement
def elapsedTime(dto):
    time_elapsed = datetime.now() - dto.getTimeStart()
    dto.publishLoggerInfo('Time elapsed (hh:mm:ss.ms): {}'.format(time_elapsed))
