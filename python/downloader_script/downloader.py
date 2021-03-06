import logging
import random
import time
import urllib.request

import youtube_dl

from functions import *
from ioutils import *


# ----- # ----- #
def getEchoList(stringList):
    listString = ''
    for item in stringList:
        if item.startswith('#') or item == '':
            continue
        listString +=('%s\n' % item)
    return listString


# ----- # ----- #
def download_wget(dto, content, accept, reject):
    dto.publishLoggerDebug('download wget')

    try:
        if ';' in content:
            swap = content.split(';')
            content = swap[0]
            directory = swap[1]
            title = swap[2]
        else:
            directory = ''
            title = ''

        path = os.path.join(os.getcwd(),directory)

        wget = 'wget -c -w 5 --random-wait --limit-rate={bw} -e robots=off'.format(bw = dto.getBandwidth())

        if directory != '':
            wget += ' -P {dir}'.format(dir = path)

        if title != '':
            wget += ' -O {title}'.format(title = getTitleFormated(title))

        if accept != '':
            wget += ' --accept {extention}'.format(extention = accept)

        if reject != '':
            wget += ' --reject {extention}'.format(extention = reject)

        # --no-http-keep-alive --no-clobber

        if dto.getSync():
            wget = wget + ' -r -N -np -nd -nH'

        wget += ' "{url}"'.format(url = content)

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

        dto.publishLoggerDebug('wget command: ' + wget)

        if (int(freeStorage) >= int(testSize)):

            download(dto, wget, 'wget', content)
            # i = 0
            # returned_value = ''

            # while i < 3:
            #     returned_value = os.system('echo \'' + wget + '\' >&1 | bash')

            #     if returned_value > 0:
            #         if returned_value == 2048:
            #             return returned_value
            #         else:
            #             dto.publishLoggerDebug('Error Code: ' + str(returned_value))
            #             i += 1
            #             timer = random.randint(200,1000)/100
            #             dto.publishLoggerDebug('sleep for ' + str(timer) + 's')
            #             time.sleep(timer)

            #             if i == 3:
            #                 dto.publishLoggerInfo('the Command was: %s' % wget)
            #                 os.system('echo "{wget}" >> dl-error-wget.txt'.format(wget = content))
            #                 return returned_value

            #     else:
            #         if dto.getSpace():
            #             func_removeFiles(dto, path, file_count_prev)
            #         return returned_value

        else:
            dto.publishLoggerWarn('wget - not enough space')
            dto.publishLoggerInfo('Directory size: ' + bytes2human(int(dirSize)*1000))
            dto.publishLoggerInfo('free Space: ' + bytes2human(freeStorage))

            if dto.getSpace():
                func_removeFiles(dto, path, file_count_prev)
            return 507

    except KeyboardInterrupt:
        dto.publishLoggerWarn('Interupt by User')
        os.system('echo "{wget}" >> dl-error-wget.txt'.format(wget = content))
        os._exit(1)

    except:
        dto.publishLoggerError('wget - error at download: ' + str(sys.exc_info()))


def download_ydl(dto, content, parameters, output, stringReferer):
    if dto.getBandwidth() != '0':
        parameters += ' --limit-rate {}'.format(dto.getBandwidth())

    if dto.getAxel():
        parameters += ' --external-downloader axel'

        if dto.getBandwidth() != '0':
            parameters += ' --external-downloader-args "-s {}"'.format(human2bytes(dto.getBandwidth()))

    if stringReferer != '':
        parameters += ' --referer "{reference}"'.format(reference = stringReferer)

    if dto.getVerbose():
        parameters += ' --verbose'

    ydl = 'youtube-dl {parameter} {output} "{url}"'.format(parameter = parameters, output = output, url = content)

    return download(dto, ydl, 'ydl', content)


def download_aria2c(dto, content, dir):
    links = getEchoList(content)

    dl = 'echo ' + links + ' | '

    dl += 'aria2c -i - -x 8 -j 16 --continue --min-split-size=1M --optimize-concurrent-downloads'

    if dto.getBandwidth() != '0':
        dl += ' --max-overall-download-limit={}'.format(dto.getBandwidth())

    if dir != '':
        dl += ' --dir="{}"'.format(dir)

    return download(dto, dl, 'aria2c', content)


def download_aria2c_magnet(dto, content, dir):
    dl = 'aria2c --seed-time=0'

    if dir != '':
        dl += ' --dir="{}"'.format(dir)

    if dto.getBandwidth() != '0':
        dl += ' --max-overall-download-limit={}'.format(dto.getBandwidth())

    dl += ' "{}"'.format(content)

    return download(dto, dl, 'aria2c-magnet', content)


def download(dto, command, platform, content):
    try:
        dto.publishLoggerDebug(platform + ' command is: ' + command)

        i = 0
        returned_value = ''

        while i < 3:
            returned_value = os.system('echo \'' + command + '\' >&1 | bash')

            if returned_value > 0:
                if returned_value == 2048:
                    return returned_value
                else:
                    dto.publishLoggerDebug('Error Code: ' + str(returned_value))
                    i += 1
                    timer = random.randint(200,1000)/100
                    dto.publishLoggerInfo('sleep for ' + str(timer) + 's')
                    time.sleep(timer)

                    if i == 3:
                        dto.publishLoggerWarn('the Command was: %s' % command)
                        os.system('echo "' + content + '" >> dl-error-' + platform + '.txt')
                        return returned_value

            else:
                return returned_value

    except KeyboardInterrupt:
        dto.publishLoggerDebug('Interupt by User')
        os.system('echo "' + content + '" >> dl-error-' + platform + '.txt')
        os._exit(1)

    except:
        dto.publishLoggerError(platform + ' - error at downloading: ' + str(sys.exc_info()))
