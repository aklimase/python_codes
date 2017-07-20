#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 16:20:24 2017

@author: escuser

inputs: path to raw data sac files

cuts for S waves based off arrival time calculated from 3.5 km/s velocity.
add 2 seconds to beginning of sample so that the taper doesn't clip data and cuts 120 seconds after the s arrival time

outputs: writes to cutdata_s directory
"""

from spec_func import cut_swave
import glob
import os.path as path
import os

location = '*'
tsunit = 'VEL'
channel = 'HH*'

#box = 'Imperial_Valley_PFO_TPFO_PMD'
#box = 'Imperial_Valley_SWS_ERR'
#box = 'Riverside_FRD_RDM'
box = 'Salton_Trough_SWS_ERR'

boxpath = '/Users/escuser/project/boxes/' + box
event_dirs = glob.glob(boxpath + '/corrected/Event_*')

eventpaths = glob.glob(boxpath + '/corrected/Event_*/*.SAC')#full path
print 'Number of files: ', len(eventpaths)

cut_dir = boxpath + '/cutdata_s/'

events = [os.path.basename(x) for x in event_dirs]

#make a directory for each event
for i in range(len(events)):
    if not path.exists(cut_dir + '/' + events[i]):
        os.makedirs(cut_dir + '/' + events[i])


#loop through event directories
for i in range(len(event_dirs)):
    #loop through all sac files in directory
    files = glob.glob(event_dirs[i] + '/*.SAC')
    for j in range(len(files)):
        base = path.basename(files[j])
        network, stn, channel, space, yyyy, month, day, hh, mm, sssac =  base.split('_')
        ss = sssac.split('.')[0]
        cutfile = cut_dir + events[i] + '/' + network + '_' + stn + '_' + channel + '__' + yyyy + '_'  + month + '_' +  day + '_' +  hh + '_' + mm + '_' + ss + '.SAC'
        print(files[j])
        #calling cut function
        #cuts 2 sec before s wave arrival and 120 seconds after
        cuttime = cut_swave(files[j], cutfile, 2, 120)


