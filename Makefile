#-------------------------------------------------------------------------------
# Copyright (c) 2010 Patrick Mueller
# Licensed under the MIT license: 
# http://www.opensource.org/licenses/mit-license.php
#-------------------------------------------------------------------------------

RUN_SRC=~/Desktop
RUN_TGT=~/Sites/ssc
RUN_URL=http://localhost/~${USER}/ssc/live.html

#-------------------------------------------------------------------------------
# nothing to do for a normal build
#-------------------------------------------------------------------------------
all: help

#-------------------------------------------------------------------------------
# build development version
#-------------------------------------------------------------------------------
build-dev:
	@echo
	@echo ----------------------------------------------------------------------
	@echo make build-dev starting
	@echo ----------------------------------------------------------------------

	@# clean tmp dir
	@rm -rf tmp
	@mkdir  tmp

	@# clean build dir
	@rm -rf build
	@mkdir  build

	@# copy stuff over to build
	python scripts/build-screen-shot-cast.py

	@echo ----------------------------------------------------------------------
	@echo make build-dev finished on `date "+%Y-%m-%d at %H:%M:%S"`
	@echo ----------------------------------------------------------------------

#-------------------------------------------------------------------------------
# build release
#-------------------------------------------------------------------------------
build-release:
	@echo TBD

#-------------------------------------------------------------------------------
# get vendor resources
#-------------------------------------------------------------------------------
get-vendor:
	@rm -rf vendor
	@mkdir  vendor

	mkdir   vendor/run-when-changed
	curl -o vendor/run-when-changed/run-when-changed.py $(RUN_WHEN_CHANGED_URL)

#-------------------------------------------------------------------------------
# remove crap
#-------------------------------------------------------------------------------
clean:
	rm -rf tmp
	rm -rf build

#-------------------------------------------------------------------------------
# print some help
#-------------------------------------------------------------------------------
help:
	@echo make targets available:
	@echo "  build-dev       - build for development"
	@echo "  clean           - garbage collect"
	@echo "  clean-desktop   - rm screen shots from ~/Desktop"
	@echo "  watch           - run-when-changed make build-dev"
	@echo "  run             - run the app, open the built view"
	@echo "  install         - install the script into ~/bin"
	@echo "  get-vendor      - get external files"

#-------------------------------------------------------------------------------
# open the web page
#-------------------------------------------------------------------------------
open:
	open ${RUN_URL}

#-------------------------------------------------------------------------------
# clean the desktop images
#-------------------------------------------------------------------------------
clean-desktop:
	@-rm ~/Desktop/Screen\ shot*.png

#-------------------------------------------------------------------------------
# start the server
#-------------------------------------------------------------------------------

run:
	@-mkdir ${RUN_TGT}   2> /dev/null
	@-rm    ${RUN_TGT}/* 2> /dev/null

	python build/screen-shot-cast.py ${RUN_SRC} ${RUN_TGT}

#-------------------------------------------------------------------------------
# see: https://gist.github.com/240922
#-------------------------------------------------------------------------------
watch:
	make build-dev
	python vendor/run-when-changed/run-when-changed.py "make build-dev" $(SOURCE)
	
#-------------------------------------------------------------------------------
# copy built script to ~/bin
#-------------------------------------------------------------------------------
install:
	cp build/screen-shot-cast.py ~/bin
	echo installed ~/bin/screen-shot-cast.py
	
#-------------------------------------------------------------------------------
# vendor info
#-------------------------------------------------------------------------------

RUN_WHEN_CHANGED_URL   = https://gist.github.com/raw/240922/0f5bedfc42b3422d0dee81fb794afde9f58ed1a6/run-when-changed.py
