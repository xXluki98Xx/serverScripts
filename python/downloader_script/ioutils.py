import json
import logging
import os
import subprocess
import urllib.request

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

    dto.publishLoggerInfo(output.decode('ascii'))
    dto.publishLoggerDebug(error.decode('ascii'))


def loadConfig(pathToRoot):
    path = os.path.join(pathToRoot, 'env')

    with open(path) as json_file:
        data = json.load(json_file)

    return data


# ----- # ----- #
def testWebpage(dto, url):
    dto.publishLoggerDebug('webpage test for: ' + url)

    req = urllib.request.Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
    try:
        conn = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        if e.code == 403:

            dto.publishLoggerDebug('HTTP Error: ' + str(e.reason))
            return 0

        dto.publishLoggerDebug('HTTP Error: ' + str(e.reason))
        return e.code
    except urllib.error.URLError as e:
        
        dto.publishLoggerDebug('URL Error: ' + str(e.reason))
        return 0
    else:
        return 0
