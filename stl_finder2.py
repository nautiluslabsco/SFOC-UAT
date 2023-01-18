import sample_data
import datetime
import pandas as pd
import numpy as np


def stl_finder2(feature_dataset):
    ftr_data = feature_dataset
    # configurables
    slope_lim = 200
    seg_min=20 # hrs

    # Variable intialize
    slope = 0
    seg_start_new = 1
    seg_start = 0
    seg_start_new = 1
    seg_end_temp = 1
    n = 2
    yn=50
    curr_slope=0
    last_slope=50
    seg_found = False
    seg_num = 1
    seg_end=1
    curr_delta_hrs=0
    stl_report = np.array(['Segment ID', 'Start (ind.)', 'End (ind.)', 'Start(DT)', 'End (dt)', 'slope'])
    seg_report = np.array(['Segment ID', 'Start (ind.)', 'End (ind.)', 'Start(DT)', 'End (dt)', 'slope'])
    data_remaining = True

    while data_remaining is True:
        #Run seg finder
        seg_found = False
        seg_inc=1
        seg_start = seg_start_new
        seg_start=n
        print(n)
        if n == len(ftr_data['timestamps'])-8:
            print('hello')

        while n+1 <= len(ftr_data['timestamps']):
            if len(ftr_data['timestamps']) <= n + 1:
                seg_found = True
                print('Reached end of features data')
                data_remaining = False
                n=n+1
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

            if len(ftr_data['means']['Shaft Power']) <= n:
                seg_found = True
                print('Reached end of features data')
                data_remaining = False
                n=n+1
                return stl_report
            else:
                checkdata(n,ftr_data,last_slope)
                checkdata(n+1,ftr_data,last_slope)


            # feature data is not null is segment is not found
            #print('Continue looking for segment if features data is not null')

                if len(ftr_data['timestamps']) < n+1:
                    seg_found = True
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
                #if n == 130:
                    #print(n)
                #slope is less than lim
                if slope_func(x1, xn, y1, yn,last_slope) >= slope_lim:
                    n=n+1
                    break
                seg_delta_hrs= curr_delta_hrs
                if int(seg_delta_hrs) >= seg_min:
                    seg_end=n
                    curr_slope = abs(slope_func(x1, xn, y1, yn, last_slope))
                    x1_dt = datetime.datetime.fromtimestamp(x1)
                    xn_dt = datetime.datetime.fromtimestamp(xn)
                    seg_temp = np.array([seg_inc, seg_start, seg_end, seg_start, seg_end, x1_dt, xn_dt, last_slope])
                    if seg_inc > 1:
                        seg_report_temp = np.vstack((seg_report, seg_temp))
                        seg_report=seg_report_temp
                    n=n+1
                    break
                    #print('restarted the variables for segment finder')

            if slope_func(x1, xn, y1, yn,last_slope) <= slope_lim:
                seg_end = n
                curr_slope=slope_func(x1, xn, y1, yn,last_slope)
                n=n+1
    #Segment Found greater than minimum length
    if seg_temp[5] >= seg_min:
        seg_temp = np.array([seg_inc, seg_start, seg_end, seg_start, seg_end, slope_func(ftr_data['timestamps'], xn, y1, yn)])
        #record on table if the start point of the last seg is different
        if seg_temp[2] != seg_temp_last[2]:
            l=len(seg_report_temp)
            seg_temp=seg_report_temp[l]
            seg_start_last = seg_temp[5]
            stl_report_temp = np.vstack((seg_report, seg_temp))
            stl_report = seg_report_temp
            seg_inc=seg_inc+1
            seg_temp_last = seg_temp
            curr_slope = slope_func(x1, xn, y1, yn, last_slope)
            seg_start_last = seg_temp[5]
            seg_start = n + 1
            curr_delta_hrs = 0
            curr_delta = 0
            print("segment found")
            #break
        else:
            print('STL found... findiing end')
            n=n+1
        seg_temp_last = seg_temp
        curr_slope = slope_func(x1, xn, y1, yn,last_slope)
        seg_start_last=seg_temp[5]
        seg_inc=seg_inc+1
        seg_start=n+1
        seg_found = False
        curr_delta_hrs=0
        curr_delta=0


    if slope_func(x1, xn, y1, yn, last_slope) <= slope_lim:
        n=n+1
    #print(curr_slope)
    seg_start_new = seg_start
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
