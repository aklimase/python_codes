#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 13:37:49 2017

@author: escuser
"""


def cut_swave(infile, cutfile):#input an instrument corrected sac file, full path
    #reads in a sac file and cuts at the s wave arrival time and 120 s after
    #set up for HH sampling rate
    import matplotlib.pyplot as plt
    from obspy import read    
    import dread
    import datetime
    
   # out = open(cutfile,'w')
    
    velocity = 3.5 #km/s, check and update with paper
    
    stream = read(infile)
    tr = stream[0]
    
    #df = tr.stats.sampling_rate
    origin_hour = tr.stats.sac.nzhour
    origin_min = tr.stats.sac.nzmin
    origin_sec = tr.stats.sac.nzsec
    origin_msec = tr.stats.sac.nzmsec
    
    trace_starttime = tr.stats.starttime
    #trace_endtime = tr.stats.endtime

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
    #print(tr.stats.sac.dist)
    
    s_travel_time = dist/velocity # in sec
    #s_arrival_time = origin_time + s_travel_time
    cuttime = origin_time_UTC + datetime.timedelta(seconds = s_travel_time)#add travel time or utc origin time
    
#    cut_xval = (cuttime - trace_starttime)/0.01#using HH sampling rate, convert cut time into x value on plot
    
#    data = tr.data
#    plt.figure(figsize = (25,6))
#    plt.plot(data, color='black')
#    plt.xlim(0, len(data))
#    plt.axvline(x=cut_xval, c = 'r')#first cut
#    plt.axvline(x=cut_xval + 120/0.01, c = 'r')#second cut
#    plt.show()

    cut_trace = tr.slice(cuttime,cuttime + datetime.timedelta(seconds = 120), nearest_sample=True)#make a new trace by slicing
#    data2 = cut_trace.data

#    plt.figure(figsize = (25,6))
#    plt.plot(data2, color='black')
#    plt.xlim(0, len(data2))
#    plt.show()
    
    cut_trace.write(cutfile, format = 'sac')

    return cuttime

def bin(data, frequency, num_bins):
    import numpy as np
    import matplotlib.pyplot as plt
    #takes in linear frequency and square of NE spectra

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
    #    y1 = data[int(lower[i])]
    #    y2 = data[int(upper[i])]
        y1 = binned_data[i]
        y2 = binned_data[i]
        plt.plot((x1,x2),(y1,y2), color = 'red')
        
    plt.scatter(c, binned_data, color = 'black', zorder = 2, marker = 'o')
    plt.plot(c, binned_data, color = 'black')
    plt.xlabel('frequency (Hz)')
    plt.ylabel('velocity spectrum (NE^2)')
        
    plt.show()
    
    return c, binned_data
    
    













