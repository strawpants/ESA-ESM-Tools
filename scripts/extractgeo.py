#/usr/bin/python3

#copyright Roelof Rietbroek 2016
#Contact:
#email:roelof@geod.uni-bonn.de 
#twitter: @r_rietje

# Distributed under the MIT license (See LICENSE)

######################################################################################
## A python3 script to extract geocenter motion changes from the                   ###
## ESA Earth system model                                                          ###
## (http://www.gfz-potsdam.de/en/section/earth-system-modelling/services/esa-esm/) ###
######################################################################################


##Geocenter motion is defined here as the offset between the center of common mass of the Earth(CM)  and the center of surface figure (CF) 
## Note that the Stokes coefficients are provided in the Center of Surface figure frame


import glob
import tarfile
import re
import numpy
import math
from datetime import datetime


#declare a brief function which returns the epoch as a decimal year
def decyear(epoch):
    yrst=datetime(epoch.year,1,1)
    yrnd=datetime(epoch.year+1,1,1)
    return float(epoch.year)+((epoch-yrst).total_seconds())/((yrnd-yrst).total_seconds())


#set root directory of the data (change this to your situation)
rootdir='/net/data1/ESAESM/mtmshc/'

#Set some planetary constants as used in the ESA model
GM=0.39860050000000E+15
#Earth radius
RE=6378137.0000

#Conversion factor to geocenter motion (CM-CF) in meter (#note that this factor is OK here as the reference origin of the ESM is CF)
conv2geo=math.sqrt(3)*RE


#compile some regex to find degree 1 coefficients
d10regex=re.compile(b'gfc +1 +0 ')
d11regex=re.compile(b'gfc +1 +1 ')

#In this loop you may only select the contributions you're interested in
for tag in ['A','O','H','I','S','AOHIS']:
    #make a list of available tarballs in the rootdir
    tarballs=glob.glob(rootdir +'*_'+tag+'.tar.gz')

    stokesd1=[]
    epochs=[]

    for tb in tarballs:
        tf=tarfile.open(tb)
        print('Extracting from '+ tb)
        for member in tf.getmembers():
            if not member.isfile(): 
                continue
            #Awkward: extract epoch from filename (This should be provided as metadata if you ask me)
            spltfname=member.name.split('_')
            epochs.append(datetime.strptime(spltfname[2]+spltfname[3][0:2], '%Y%m%d%H'))
            
            #open file
            tfid=tf.extractfile(member)
            tmpstokes=[None]*3

            #find degree 1 Stokes coefficients
            deg1found=0
            while deg1found < 3:
                tfline=tfid.readline()
                if re.search(d10regex,tfline):
                    tfspl=tfline.split()
                    tmpstokes[2]=float(tfspl[3].replace(b'D',b'E'))
                    deg1found+=1
                if re.search(d11regex,tfline):
                    tfspl=tfline.split()
                    tmpstokes[0]=float(tfspl[3].replace(b'D',b'E'))
                    tmpstokes[1]=float(tfspl[4].replace(b'D',b'E'))
                    deg1found+=2

            #no need to read further in the file: close it
            tfid.close()
            stokesd1.append(tmpstokes)

    stokesd1=conv2geo*numpy.asarray(stokesd1)

    #write 6-hourly stuff to ascii file
    outputf='GeocenterCM-CF_'+tag+'_6hrly.txt'
    fileid=open(outputf,'w')
    print('#6-hourly Geocenter motion CM-CF  from the ESA earth system model. Columns denote',file=fileid)
    print('#Decimalyear isodate  x[m] y[m] z[m]',file=fileid)
    for ith in range(len(epochs)):
        print('%.8f %s %s'%(decyear(epochs[ith]),epochs[ith].isoformat(),' '.join(map(str,stokesd1[ith]))),file=fileid)
    fileid.close()


    #also write a monthly averaged version to ascii file
    outputf='GeocenterCM-CF_'+tag+'_monthly.txt'
    fileid=open(outputf,'w')
    print('#Monthly Geocenter motion CM-CF  from the ESA earth system model. Columns denote',file=fileid)
    print('#Decimalyear isodate  x[m] y[m] z[m]',file=fileid)
    monthprev=epochs[0].month
    monthav=numpy.zeros([3])
    days=0
    for ith in range(len(epochs)):
        if epochs[ith].month == monthprev:
            monthav+=stokesd1[ith]
            days+=1  
        else:  
            #write previous month to file (just take day 15 as the central day)
            centralepoch=datetime(epochs[ith-1].year,epochs[ith-1].month,15)
            print('%.8f %s %s'%(decyear(centralepoch),centralepoch.isoformat(),' '.join(map(str,monthav/days))),file=fileid)            
            #start a new monthly average 
            monthav=numpy.zeros([3])
            days=0
            monthprev=epochs[ith].month 
    #don't forget to print the final month
    centralepoch=datetime(epochs[ith].year,epochs[ith].month,15)
    print('%.8f %s %s'%(decyear(centralepoch),centralepoch.isoformat(),' '.join(map(str,monthav/days))),file=fileid)

    fileid.close()



