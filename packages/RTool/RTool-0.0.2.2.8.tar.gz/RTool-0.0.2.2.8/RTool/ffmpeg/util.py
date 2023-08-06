'''RTool/ffmpeg/util.py

'''

import subprocess, os, sys

from RTool.util.importer import ImportHandler
exec(ImportHandler(["imageio"]))

def downloadPath():
    dirList = None; ffmpegFile = None
    ffmpegPath = ("C:\\Users\\%s\\AppData\\Local\\imageio\\ffmpeg"
                  %(os.environ["USERNAME"]))

    while True:
        dirList = sorted(os.listdir(ffmpegPath))
        if dirList == []:
            imageio.plugins.ffmpeg.download()
        else:
            break

    print(dirList)
    if len(dirList) > 1:
        for i in range(1,len(dirList)):
            ffmpegFile = dirList[-i]
            if "ffmpeg" in ffmpegFile:
                break
    else:
        ffmpegFile = dirList[0]

    ffmpegExtension = ffmpegFile[-4:]
    ffmpegFile = ffmpegFile[:len(ffmpegFile)-4]

    ffmpegPath = os.path.join(ffmpegPath, ffmpegFile)

    return ffmpegPath

print(downloadPath())



