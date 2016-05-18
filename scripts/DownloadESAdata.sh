#!/bin/bash

#copyright Roelof Rietbroek 2016
#Contact:
#email:roelof@geod.uni-bonn.de 
#twitter: @r_rietje

# Distributed under the MIT license See LICENSE

##################################################################
##### Updater script to download the ESA Earth system data  ######
##################################################################

#Usage:
# 1 put this script in the directory where you want to store the data (e.g. ESAESM) and comment out the directories you want to download below
# 2 execute the script e.g. ESAESM/DownloadESAdata.sh

##WARNING this script downloads considerable amounts of data. for example the mtmshc directory only is about 34 Gb)

rootftp=ftp://ig2-dmz.gfz-potsdam.de/ESAESM/

#change to location where this script is stored
cd $(dirname ${BASH_SOURCE})


wget -nH -N -r --force-directories --cut-dirs=1 ${rootftp}/mtmshc


#wget -nH -N -r --force-directories --cut-dirs=1 ${rootftp}/mtmdeal

#wget -nH -N -r --force-directories --cut-dirs=1 ${rootftp}/mtm3h

#wget -nH -N -r --force-directories --cut-dirs=1 ${rootftp}/mtmmisc


#wget -nH -N -r --force-directories --cut-dirs=1 ${rootftp}/mtmnIB
