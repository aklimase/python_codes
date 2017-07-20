#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 13:37:49 2017

@author: escuser
"""


def cut_swave(infile, cutfile, t1, t2):
    #reads in a sac file
    #full path to output file
    #cuts at t1 sec before s arrival and t2 seconds after
    from obspy import read    
    import dread
    import datetime
    
    velocity = 3.5 #km/s
    
    stream = read(infile)
    tr = stream[0]
    
    origin_hour = tr.stats.sac.nzhour
    origin_min = tr.stats.sac.nzmin
    origin_sec = tr.stats.sac.nzsec
    origin_msec = tr.stats.sac.nzmsec
    
    trace_starttime = tr.stats.starttime

    origin_time = (origin_hour*60*60 + origin_min*60 + origin_sec + origin_msec/1000.)# in seconds after start of day
    trace_starttime_sec = tr.stats.sac.b #sec
    
    #difference between origin time and when the trace starts
    delta =  origin_time - trace_starttime_sec # in sec
    origin_time_UTC = trace_starttime + datetime.timedelta(seconds=delta)#convert origin time to UTC
    
    evlon =  tr.stats.sac.evlo #deg
    evlat =  tr.stats.sac.evla #deg
    evdepth = tr.stats.sac.evdp #km
    stlon = tr.stats.sac.stlo #deg
    stlat = tr.stats.sac.stla #deg
    stdepth = tr.stats.sac.stdp #km
    
    #find distance between event and station
    dist =  dread.compute_rrup(evlon, evlat, evdepth, stlon, stlat, stdepth) #in km
    
    s_travel_time = dist/velocity # in sec
    cuttime = origin_time_UTC + datetime.timedelta(seconds = s_travel_time)#add travel time or utc origin time

    cut_trace = tr.slice(cuttime - datetime.timedelta(seconds = t1),cuttime + datetime.timedelta(seconds = t2), nearest_sample=True)#make a new trace by slicing

    cut_trace.write(cutfile, format = 'sac')

def bin_spec(data, frequency, num_bins):
    import numpy as np
    import matplotlib.pyplot as plt
    #takes in linear frequency and NE velocity spectra (not power!)

    fstart = frequency[1]
    fend = frequency[-1]
    
    #index array for bins
    c = np.logspace(np.log10(fstart), np.log10(fend), num_bins)
    l = len(c)
    binned_data = np.zeros(num_bins)
    lower = np.zeros(num_bins)
    upper = np.zeros(num_bins)
    #first point
    #mean of first point and index of point with f less than or equal to c(1)
    index = (frequency <= c[1]).argmin()
    upper[0] = index
    lower[0] = 0
    binned_data[0] = np.mean(data[0:index])
    #index = (frequency >= c[l-2]).argmax()
    upper[-1] = -1
    index = (frequency >= c[l-2]).argmax()
    lower[-1] = index
    binned_data[l-1] = np.mean(data[index:-1])
    for i in range(1,l-1):
        lb = (frequency >= c[i-1]).argmax()
        ub = (frequency <= c[i+1]).argmin()
        lower[i] = lb
        upper[i] = ub
        #add an if statement if lower = upper
        if lb == ub:
            binned_data[i] = data[lb]
        else:
            binned_data[i] = np.mean(data[lb:ub])
    
    #make plot to check
    plt.figure(figsize = (10,8))
    plt.loglog(frequency, data, color='cornflowerblue', zorder = 1)#linear so plot in logspace
    
    for i in range(0,l):
        x1 = frequency[int(lower[i])]
        x2 = frequency[int(upper[i])]
        y1 = binned_data[i]
        y2 = binned_data[i]
        plt.plot((x1,x2),(y1,y2), color = 'red')
        
    plt.scatter(c, binned_data, color = 'black', zorder = 2, marker = 'o')
    plt.plot(c, binned_data, color = 'black')
    plt.xlabel('frequency (Hz)')
    plt.ylabel('velocity spectrum (NE)')
        
    plt.show()
    
    return c, binned_data

def L1norm(record_paths):
    import os.path as path
    import dread
    from obspy import read
    import numpy as np

    N = len(record_paths)
    L1  = np.zeros((N, 50)) #50 bands, number of recordings
    for i in range(N):
    #for the list of records compute L2 norm in each f band
            base = path.basename(record_paths[i])
            eventid, network, station, channel, extn = base.split('.')
            raw_file = '/Users/escuser/Documents/Alexis_Data/cut_sac_files/rawdata/' + eventid + '.' + network + '.' +  station + '.HHN.sac'
            event_dir =  '/Users/escuser/Documents/Alexis_Data/cut_sac_files/event_site_spectra/'
            station_dir =  '/Users/escuser/Documents/Alexis_Data/cut_sac_files/event_site_spectra/'
            stream = read(raw_file)
            tr = stream[0]

            evlon =  tr.stats.sac.evlo #deg
            evlat =  tr.stats.sac.evla #deg
            evdepth = tr.stats.sac.evdp #km
            stlon = tr.stats.sac.stlo #deg
            stlat = tr.stats.sac.stla #deg
            stdepth = tr.stats.sac.stdp #km

            #find distance between event and station
            dist =  dread.compute_rrup(evlon, evlat, evdepth, stlon, stlat, stdepth) #in km
            #km to cm
            dist = dist*100000
            #record spectra
            record_data = np.genfromtxt(record_paths[i], dtype = float, comments = '#', delimiter = None, usecols = (0,1))#only read in first two cols
            record_spec = record_data[:,1]*dist

            #event spectra
            event_data = np.genfromtxt(event_dir + eventid + '.out', dtype = float, comments = '#', delimiter = None, usecols = (0,1))
            event_spec = event_data[:,1]
            #station spectra
            station_data = np.genfromtxt(station_dir + station + '.out', dtype = float, comments = '#', delimiter = None, usecols = (0,1))
            station_spec = station_data[:,1]
            
            calc_record_spec = station_spec*event_spec
            residual = (record_spec - calc_record_spec)
            #set recording row equal to residual array
            L1[i:,] = residual
    return L1
            









