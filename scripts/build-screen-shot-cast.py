#!/usr/bin/env python

import os
import re

# read the base python script

iFileName = os.path.join("server", "screen-shot-cast.py")
with open(iFileName) as iFile:
    contents = iFile.read()
    
screenShotCastContents = contents

# read the base html file

iFileName = os.path.join("web", "live-screen-shot-cast.html")
with open(iFileName) as iFile:
    contents = iFile.read()

liveScreenShotCastContents = contents

# jam the html file in the python script

tag = "###:::include web/live-screen-shot-cast.html"

contents = screenShotCastContents.replace(tag, liveScreenShotCastContents)

# write the output file

oFileName = os.path.join("build", "screen-shot-cast.py")
with open(oFileName, "w") as oFile:
    oFile.write(contents)

print "wrote: %s" % oFileName