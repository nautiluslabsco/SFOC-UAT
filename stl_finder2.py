import sample_data
import datetime
import pandas as pd
import numpy as np


def stl_finder2(feature_dataset):
    ftr_data = feature_dataset
    # configurables
    slope_lim = 20
    seg_min=20 # hrs

    # Variable intialize
    slope = 0
    seg_start_new = 1
    seg_start = 0
    seg_start_new = 1
    seg_end_temp = 1
    n = 1
    yn=50
    curr_slope=0
    last_slope=50
    seg_found = False
    seg_num = 1
    seg_end=1
    curr_delta_hrs=0
    seg_inc = 1
    stl_report = np.array(['Segment ID', 'Start (ind.)', 'End (ind.)', 'Start(DT)', 'End (dt)', 'slope'])
    seg_report = np.array(['Segment ID', 'Start (ind.)', 'End (ind.)', 'Start(DT)', 'End (dt)', 'slope'])
    data_remaining = True

    while data_remaining is True:
        #Run seg finder
        seg_found = False
        seg_start = seg_start_new
        print(n)
        while n+1 <= len(ftr_data['timestamps']):
            seg_start=seg_start_new
            if len(ftr_data['timestamps']) <= n + 1:
                seg_found = False
                print('Reached end of features data')
                data_remaining = False
                #seg_start_new = n+1
                n=n+1
                break
            else:
                x1 = ftr_data['timestamps'][seg_start]
                y1 = ftr_data['means']['Shaft Power'][seg_start]
                # if ftr_data['timestamps'][n+1]
                xn = ftr_data['timestamps'][n + 1]
                yn = ftr_data['means']['Shaft Power'][n + 1]
                x1_dt = datetime.datetime.fromtimestamp(x1)
                xn_dt = datetime.datetime.fromtimestamp(xn)
                curr_delta = xn_dt - x1_dt
                curr_delta_hrs = (curr_delta.total_seconds()) / (60 * 60)

            if len(ftr_data['means']['Shaft Power']) <= n+1:
                seg_found = False
                print('Reached end of features data')
                data_remaining = False
                n=n+1
                return stl_report
            else:
                checkdata(n,ftr_data,last_slope)
                checkdata(n+1,ftr_data,last_slope)


                #if no more data, stop
                if len(ftr_data['timestamps']) <= n+1:
                    seg_found = False
                    print('Reached end of features data')
                    data_remaining = False
                    n = n + 1
                    return stl_report
                else:
                    x1 = ftr_data['timestamps'][seg_start]
                    y1 = ftr_data['means']['Shaft Power'][seg_start]
                    #if ftr_data['timestamps'][n+1]
                    xn = ftr_data['timestamps'][n+1]
                    yn = ftr_data['means']['Shaft Power'][n+1]
                    x1_dt = datetime.datetime.fromtimestamp(x1)
                    xn_dt = datetime.datetime.fromtimestamp(xn)
                    curr_delta = xn_dt - x1_dt
                    curr_delta_hrs = (curr_delta.total_seconds()) / (60 * 60)
                    curr_slope=abs(slope_func(x1, xn, y1, yn, last_slope))
                    #print(curr_slope)
                    n=n+1
                #if n == 130:
                    #print(n)
                #slope is less than lim, set new start end and iterate
                if slope_func(x1, xn, y1, yn,last_slope) >= slope_lim:
                    seg_start_temp = n
                    n=n+1
                    #break
                seg_delta_hrs= curr_delta_hrs

                #if seg is longer than min, append to array
                if int(seg_delta_hrs) >= seg_min:
                    seg_temp = np.array([seg_inc, seg_start, seg_end, seg_start, seg_end, x1_dt, xn_dt, last_slope])


                    #print('restarted the variables for segment finder')

        if slope_func(x1, xn, y1, yn, last_slope) <= slope_lim:
            n=n+1
            seg_start_new = n + 1
    #Segment Found greater than minimum length
    if (curr_delta.total_seconds()/(60*60)) >= seg_min:
        stl_start=seg_start
        stl_end = n
        stl_start_dt = 0
        stl_end_dt = 0
        stl_slope=abs(slope_func(x1, xn, y1, yn, curr_slope))
        seg_temp = np.array([seg_inc, stl_start, stl_end, stl_start_dt, stl_end_dt, slope])
        l=0
        seg_start_new = n + 1
        while slope >= slope_lim:
            seg_temp = np.array([seg_inc, stl_start, stl_end, stl_start, stl_end, stl_slope])
            l=l+1
            curr_delta_hrs = 0
            curr_delta = 0
        seg_start = n + 1
        stl_start=n+1
        #record on table if the start point of the last seg is different
        #l=len(seg_report_temp)
        #seg_temp=seg_report_temp[l]
        stl_report_temp = np.vstack((seg_report, seg_temp))
        #stl_report = seg_report_temp
        seg_inc=seg_inc+1
        seg_temp_last = seg_temp
        curr_slope = slope_func(seg_start, seg_end, y1, yn, last_slope)
        print("segment found")
        return
    else:
        print('STL found... findiing end')
        seg_temp_last = seg_temp
        curr_slope = slope_func(x1, xn, y1, yn,last_slope)
        seg_start_last=seg_temp[5]
        seg_inc=seg_inc+1
        seg_start=n+1
        seg_found = False
        curr_delta_hrs=0
        curr_delta=0
        n=n+1



    return stl_report




def slope_func(x1, xn, y1, yn, last_slope):
    x1_dt = datetime.datetime.fromtimestamp(x1)
    xn_dt = datetime.datetime.fromtimestamp(xn)
    # find time diff in hours
    x_delta = xn_dt - x1_dt
    #print(x_delta)
    #print(x1_dt)
    #print(xn_dt)
    x_delta_hrs = (x_delta.total_seconds()) / (60 * 60)
    if yn is None or xn is None:
        return last_slope
        print('replaced null value')
    if x1 is None or y1 is None:
        return last_slope
        print('replaced null value')
    # Calculate rise
    y_delta = yn - y1
    # Rise over run... right... cant remember, check this later, or right now
    slope = y_delta / x_delta_hrs
    last_slope=slope
    #print(slope)
    # Change in
    #print("slope Found")
    return slope


def checkdata(n,ftr_data,last_slope):
    if len(ftr_data['means']['Shaft Power']) > n:
        if ftr_data['means']['Shaft Power'][n] == 0:
            curr_slope = abs(last_slope)
            return
        if ftr_data['means']['Shaft Power'][n] is None:
            curr_slope = abs(last_slope)
            return
        if ftr_data['timestamps'][n] is None:
            curr_slope = abs(last_slope)
            return
        if ftr_data['timestamps'][n] == 0:
            curr_slope = abs(last_slope)
            return
    else:
        curr_slope = abs(last_slope)
        return
