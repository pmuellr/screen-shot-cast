#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Copyright (c) 2010 Patrick Mueller
# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license.php
#-------------------------------------------------------------------------------

import os
import re
import sys
import json
import time
import sched
import urllib
import shutil
import numbers
import optparse
import threading
import datetime

PROGRAM = os.path.basename(sys.argv[0])
VERSION = "1.0.0"

Args           = None
Options        = None
ImageSourceDir = None
ImageTargetDir = None

ValidImageExtensions = ["JPG", "JPEG", "GIF", "PNG", "BMP"]

FileList = {}

#-------------------------------------------------------------------------------
# main program
#-------------------------------------------------------------------------------
def main(): 
    global Options, Args
    global ImageSourceDir, ImageTargetDir
    
    (Options, Args) = parseArgs()
    
    ImageSourceDir = Args[0]
    ImageTargetDir = Args[1]
    
    if not os.path.exists(ImageSourceDir): error("image source directory does not exist: %s" % ImageSourceDir)
    if not os.path.exists(ImageTargetDir): error("image target directory does not exist: %s" % ImageTargetDir)
    if not os.path.isdir( ImageSourceDir): error("image source directory not a dir: %s"      % ImageSourceDir)
    if not os.path.isdir( ImageTargetDir): error("image target directory not a dir: %s"      % ImageTargetDir)

    interval = Options.interval

    log("copying from %s to %s every %s seconds" % (ImageSourceDir, ImageTargetDir, interval))
    
    oFileName = "live.html"
    oFileName = os.path.join(ImageTargetDir,oFileName)
    with file(oFileName, "w") as oFile:
        oFile.write(getMainHtml())
        
    log("wrote main html to: %s" % oFileName)
    
    runTimerStep()

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def runTimerStep():
    threading.Timer(Options.interval, runTimerStep).start()

    (changes, fileRecords) = checkFiles()
    if not changes: return
    
    fileRecords = [
        {"name": record[0], "date": record[1], "dateString": isoDate(record[1])} 
        for record in fileRecords
    ]
    
    fileRecords.sort(reverse=True, cmp = lambda x,y: cmp(x["date"], y["date"]))
    fileRecords = json.dumps(fileRecords, indent=4)
    
    oFileName = os.path.join(ImageTargetDir, "index.json")
    with open(oFileName, "w") as oFile:
        oFile.write(fileRecords)
    
    log("%s: updated index: %s" % (isoDate(), oFileName))

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def checkFiles():
    verbose("%s: checking files" % isoDate())
    
    entries = os.listdir(ImageSourceDir)
    
    oldList = []
    newList = []
    
    for fEntry in entries:
        if fEntry.startswith("."): continue 
        ext = os.path.splitext(fEntry)[1][1:].upper()
        if ext not in ValidImageExtensions: continue
        
        tEntry = fEntry
        if Options.quoteURL: tEntry = urllib.quote_plus(fEntry)
        
        fEntryMTime = os.path.getmtime(os.path.join(ImageSourceDir, fEntry))
        
        if tEntry in FileList:
            cEntryMTime = FileList[tEntry]
            
            if fEntryMTime != cEntryMTime:
                copyFile(fEntry, tEntry, fEntryMTime, newList, "upd")
            else:
                oldList.append([tEntry, fEntryMTime])

            continue
        
        else:
            copyFile(fEntry, tEntry, fEntryMTime, newList, "new")
            continue

    changes = len(newList) != 0
    
    newList.extend(oldList)
    
    return (changes, newList)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def copyFile(srcName, tgtName, srcMTime, list, label):
    FileList[tgtName] = srcMTime
    list.append([tgtName, srcMTime])

    srcName = os.path.join(ImageSourceDir, srcName)
    tgtName = os.path.join(ImageTargetDir, tgtName)

    shutil.copyfile(srcName, tgtName)
    shutil.copystat(srcName, tgtName)
    log("%s: file copied    %s : %s" % (isoDate(), tgtName, label))

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def isoDate(dirName=None, fileName=None):
    if None == fileName:
        if None == dirName:
            return datetime.datetime.now().isoformat(" ")
            
        if isinstance(dirName, numbers.Number):
            return datetime.datetime.fromtimestamp(dirName).isoformat(" ")
            
        fileName = dirName
    else:
        fileName = os.path.join(dirName, fileName)
        
    return datetime.datetime.fromtimestamp(os.path.getmtime(fileName)).isoformat(" ")

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def parseArgs():
    usage        = "usage: %s [options] imageSourceDir imageTargetDir" % PROGRAM
    version      = "%s %s" % (PROGRAM,VERSION)
    description  = getHelp()

    parser = optparse.OptionParser(usage=usage, version=version, description=description)

    parser.add_option("-i", "--interval", dest="interval", metavar="MILLIS", default="1.0",
        help="# of seconds to wait before check for updated files(default: %default)"
    )

    parser.add_option("-q", "--quiet", dest="quiet", action="store_true", default=False,
        help="be quiet"
    )

    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,
        help="be noisy"
    )

    parser.add_option("-u", "--quoteURL", dest="quoteURL", action="store_true", default=False,
        help="escape file names using usual rules")
        
    (options, args) = parser.parse_args()

    help = False
    if len(args) <  2:   help = True
    elif args[0] == "?": help = True

    if help:
        parser.print_help()
        sys.exit(0)

    try:
        options.interval = float(options.interval)
    except ValueError:
        error("the interval option must be floating point number")

    return (options, args)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def verbose(message):
    if not Options.verbose: return

    print "%s: %s" % (PROGRAM, message)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def log(message):
    if Options.quiet: return

    print "%s: %s" % (PROGRAM, message)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def error(message):
    print "%s: %s" % (PROGRAM, message)
    exit(1)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def errorException(message):
    eType  = str(sys.exc_info()[0])
    eValue = str(sys.exc_info()[1])

    error("%s; exception: %s: %s" % (message, eType, eValue))

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def getHelp():
    return """
copys files from imageSourceDir to imageTargetDir, also
writing files 'live.html' and 'index.json' to imageTargetDir,
which together can be used to watch the live copied files
    """.strip()

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def getMainHtml():
    return """
###:::include web/live-screen-shot-cast.html
""".strip() % {"program": PROGRAM}

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == '__main__': main()

