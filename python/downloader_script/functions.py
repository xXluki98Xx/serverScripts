#!/usr/bin/env python3

import grp
import logging
import os
import pwd
import re
import shutil
import stat
import sys
from datetime import datetime
from pathlib import Path

import ffmpeg


# ----- # ----- # help functions
def getTitleFormated(title):
    newTitle = ''

    if title == '':
        now = datetime.now()
        newTitle = 'dl_' + now.strftime('%m-%d-%Y_%H-%M-%S')
        return newTitle
    else:
        newTitle = title

    newTitle = func_formatingFilename(newTitle)

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
def func_formatingDirectories(text):
    if text.startswith('.'):
        return

    reg = re.compile(r'[^\w\d\s\-\_\/\.]')
    reg3 = re.compile(r'-{3,}')

    swap = text.casefold()
    swap = re.sub(reg, '', swap)
    swap = swap.replace(' ', '-').replace('_','-').replace('+','-')

    swap = re.sub(reg3, '§', swap)
    swap = swap.replace('--', '-')
    swap = swap.replace('§', '---')

    return swap


def func_formatingFilename(text):
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


def func_renameEpisode(season, episode, title, seasonOffset):
    f = 's'
    if len(season) == 1:
        f += '0' + str( int(season) + int(seasonOffset))
    else:
        f += str( int(season) + int(seasonOffset))

    f += 'e'
    if len(episode) == 1:
        f += '0' + episode
    else:
        f += episode
    f += '-' + title

    return f


# ----- # ----- # file operations
def func_rename(dto, filePath, platform, offset, cut):
    if os.path.isfile(filePath):
        if filePath.startswith('.'):
            return
        old = os.path.join(os.getcwd(),filePath)
        new = os.path.join(os.getcwd(),func_formatingFilename(filePath))
        os.rename(old, new)
    else:
        try:
            path, dirs, files = next(os.walk(filePath))
        except:
            dto.publishLoggerInfo('error at func_rename: could the path be wrong?')

        for directory in dirs:
            func_rename(dto, os.path.join(filePath, directory), platform, offset, cut)

        for f in os.listdir(path):
            old = os.path.join(path,f)
            f = f[offset:]
            # f = f[:cut]

            if platform == 'crunchyroll':
                fSwap = func_formatingFilename(f).split('-', 4)
                f = func_renameEpisode(fSwap[1], fSwap[3], fSwap[4], 1)

            new = os.path.join(path,func_formatingFilename(f))
            os.rename(old, new)

        try:
            os.rename(filePath, func_formatingDirectories(filePath))
        except:
            pass


def func_replace(dto, filePath, old, new):
    try:
        path, dirs, files = next(os.walk(filePath))
    except:
        dto.publishLoggerInfo('could the path be wrong?')

    for directory in dirs:
        func_replace(dto, os.path.join(filePath, directory), old, new)

    for f in os.listdir(path):
        oldFile = os.path.join(path,f)
        f = f.replace(old, new)
        newFile = os.path.join(path,func_formatingFilename(f))
        os.rename(oldFile, newFile)

    try:
        os.rename(filePath, func_formatingDirectories(filePath))
    except:
        pass


def func_removeFiles(dto, path, file_count_prev):
    if not dto.getRemoveFiles():
        dto.publishLoggerInfo('Removing old files')

        # file count
        path, dirs, files = next(os.walk(path))
        file_count = len(files)

        dto.publishLoggerDebug('files before: ' + str(file_count_prev))
        dto.publishLoggerDebug('files after: ' + str(file_count))

        if (file_count > file_count_prev):
            files = []
            index = 0
            for f in os.listdir(path):
                index += 1
                if ( os.stat(os.path.join(path,f)).st_mtime < (datetime.now().timestamp() - (6 * 30 * 86400)) ):
                    files.append(os.path.join(path,f))

            if index > len(files):
                for i in files:
                    dto.publishLoggerInfo('removing: ' + i)
                    os.remove(os.path.join(path, i))

        else:
            files = []
            index = 0
            for f in os.listdir(path):
                index += 1
                if ( os.stat(os.path.join(path,f)).st_mtime < (datetime.now().timestamp() - (12 * 30 * 86400)) ):
                    files.append(os.path.join(path,f))

            if index > len(files):
                for i in files:
                    dto.publishLoggerInfo('removing: ' + i)
                    os.remove(os.path.join(path, i))

        dto.publishLoggerInfo('finished Removing')


# ----- # ----- # convert files
def func_convertDirFiles(dto, path, newformat, subpath, vcodec, acodec, fix):
    try:
        paths, dirs, files = next(os.walk(path))

        pathList = [
            'fix', 'abort', 'swap', 'orig', subpath,
        ]

        dto.publishLoggerDebug('convertDirFiles')
        dto.publishLoggerDebug('path: ' + path)
        dto.publishLoggerDebug('dirs: ' + str(dirs))
        dto.publishLoggerDebug('file count: ' + str(len(files)))

        for f in files:
            if f.startswith('.'):
                continue

            filePath = os.path.join(path, f)

            dto.publishLoggerDebug('filePath: ' + filePath)
            dto.publishLoggerDebug('file: ' + f)

            func_convertFilesFfmpeg(dto, filePath, newformat, subpath, vcodec, acodec, fix)

        for d in dirs:
            if d.startswith('.'):
                continue

            if any(paths in d for paths in pathList):
                continue

            nextPath = os.path.join(paths, d)

            dto.publishLoggerDebug('newformat: ' + newformat)
            dto.publishLoggerDebug('nextPath: ' + nextPath)
            dto.publishLoggerDebug('ffmpeg: ' + str(ffmpeg))

            func_convertDirFiles(dto, nextPath, newformat, subpath, vcodec, acodec, fix)
    except:
        dto.publishLoggerInfo('error at func_convertDirFiles: ' + str(sys.exc_info()))


def func_convertFilesFfmpeg(dto, fileName, newFormat, subPath, vcodec, acodec, fix):
    if fileName.find('.') != -1:

        prePath = fileName.rsplit('/', 1)[0] + '/'

        fileOrig = fileName.rsplit('/', 1)[1]
        fileTarget = ''
        sourceFile = prePath + fileOrig

        pathAbort = prePath + 'abort/'
        pathFix = prePath + 'fix/'
        pathSwap = prePath + 'swap/'
        pathFinish = prePath + 'orig/'

        try:
            output = ''
            newFile = fileOrig.rsplit('.', 1)[0]
            title = getTitleFormated(newFile)

            if subPath:
                dto.publishLoggerDebug('create subPath')
                dto.publishLoggerDebug('subPath: ' + subPath)
                dto.publishLoggerDebug('newFile: ' + newFile)
                dto.publishLoggerDebug('subPath: ' + str(prePath + subPath))
                dto.publishLoggerDebug('subPath exist: ' + str(os.path.exists(prePath + subPath)))

                path = prePath + subPath

                if not os.path.exists(path):
                    os.makedirs(path)

                output = subPath + '/' + title

            else:
                output = title

            fileTarget = output + '.' + newFormat

            dto.publishLoggerDebug('originalFile: ' + fileOrig)
            dto.publishLoggerDebug('output: ' + fileTarget)
            dto.publishLoggerDebug('fix: ' + str(not fix))

            if os.path.isfile(prePath + fileTarget):
                dto.publishLoggerInfo('file exist already, move original to abort folder')

                if not os.path.isdir(pathAbort):
                    os.mkdir(pathAbort)

                try:
                    shutil.move(prePath + fileOrig, pathAbort + fileOrig)
                except:
                    pass

                return
            
            if not fix:
                try:
                    dto.publishLoggerDebug('fixing')
                    dto.publishLoggerDebug('fileOrig: ' + prePath + fileOrig)
                    dto.publishLoggerDebug('fileFix: '+ pathFix + fileOrig)
                    dto.publishLoggerDebug('exist?: ' + str(os.path.isfile(pathFix + fileOrig)))

                    if not os.path.isdir(pathFix):
                        os.mkdir(pathFix)

                    ffmpeg.input(prePath + fileOrig).output(pathFix + fileOrig, vcodec='copy', acodec='copy', map='0', **{'bsf:v': 'mpeg4_unpack_bframes'}).run()

                except KeyboardInterrupt:
                    os._exit(1)

                except:
                    dto.publishLoggerInfo('error at func_convertFilesFfmpeg at fixing: ' + str(sys.exc_info()))
                    try:
                        os.remove(pathFix + fileOrig)
                    except:
                        pass

            if os.path.isfile(pathFix + fileOrig):
                sourceFile = pathFix + fileOrig

            if vcodec != '':
                try:
                    ffmpeg.input(sourceFile).output(prePath + fileTarget, vcodec=vcodec, acodec=acodec, map='0').run()

                except KeyboardInterrupt:
                    os._exit(1)

                except:
                    dto.publishLoggerInfo('error at func_convertFilesFfmpeg with vcodec first try: ' + str(sys.exc_info()))

                    # Posible data lose
                    fileSwap = newFile + '.' + newFormat
                    
                    dto.publishLoggerDebug('swapFile: ' + fileSwap)
                    dto.publishLoggerDebug('fileTarget: ' + fileTarget)

                    os.remove(prePath + fileTarget)
                    
                    if not os.path.isdir(pathSwap):
                        os.mkdir(pathSwap)

                    try:
                        ffmpeg.input(sourceFile).output(pathSwap + fileSwap, map='0', scodec='copy').run()
                        ffmpeg.input(pathSwap + fileSwap).output(prePath + fileTarget, map='0', vcodec=vcodec, acodec=acodec, scodec='copy').run()

                    except:
                        dto.publishLoggerInfo('error at func_convertFilesFfmpeg with vcodec second try with swapping: ' + str(sys.exc_info()))
                        dto.publishLoggerInfo('broken file: ' + sourceFile)

                        try:
                            dto.publishLoggerDebug('pathAbort: ' + pathAbort)
                            dto.publishLoggerDebug('fileOrig: ' + prePath+fileOrig)
                            dto.publishLoggerDebug('swapFile: ' + prePath+fileSwap)
                            dto.publishLoggerDebug('fileTarget: ' + prePath+fileTarget)

                            if not os.path.isdir(pathAbort):
                                os.mkdir(pathAbort)
                            
                            shutil.move(prePath + fileOrig, pathAbort + fileOrig)
                            
                            os.remove(prePath + fileSwap)
                            os.remove(prePath + fileTarget)
                        except:
                            dto.publishLoggerInfo('error at func_convertFilesFfmpeg with vcodec second try with swapping at swap removing: ' + str(sys.exc_info()))


            else:
                try:
                    dto.publishLoggerInfo('fileTarget: ' + fileTarget)
                    ffmpeg.input(sourceFile).output(prePath + fileTarget).run()

                except KeyboardInterrupt:
                    os._exit(1)
                
                except:
                    dto.publishLoggerInfo('error at func_convertFilesFfmpeg at simple converting: ' + str(sys.exc_info()))

            dto.publishLoggerDebug('Permissions: ' + oct(stat.S_IMODE(os.lstat(prePath + fileOrig).st_mode)))
            dto.publishLoggerDebug('owner: ' + Path(prePath + fileOrig).owner() + ' | ' + str(pwd.getpwnam(Path(prePath + fileOrig).owner()).pw_uid))
            dto.publishLoggerDebug('group: ' + Path(prePath + fileOrig).group() + ' | ' + str(grp.getgrnam(Path(prePath + fileOrig).group()).gr_gid))

            dto.publishLoggerInfo('changing permission on: ' + prePath+fileTarget)
            Path(prePath + fileTarget).chmod(stat.S_IMODE(os.lstat(prePath + fileOrig).st_mode))
            os.chown(prePath + fileTarget, pwd.getpwnam(Path(prePath + fileOrig).owner()).pw_uid, grp.getgrnam(Path(prePath + fileOrig).group()).gr_gid)

            try:
                dto.publishLoggerDebug('pathFinish: ' + pathFinish)
                dto.publishLoggerDebug('sourceFile: ' + sourceFile)
                dto.publishLoggerDebug('origFile: ' + prePath + fileOrig)

                if not os.path.isdir(pathFinish):
                    os.mkdir(pathFinish)
                
                shutil.move(prePath + fileOrig, pathFinish + fileOrig)
            except:
                dto.publishLoggerInfo('error at func_convertFilesFfmpeg finish at orig directory')

        except KeyboardInterrupt:
            os._exit(1)

        except:
            dto.publishLoggerInfo('error at func_convertFilesFfmpeg: ' + str(sys.exc_info()))

        finally:
            if os.path.isdir(pathSwap):
                shutil.rmtree(pathSwap)

            if os.path.isdir(pathFix):
                shutil.rmtree(pathFix)