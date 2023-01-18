import sample_data
import datetime
import pandas as pd
import numpy as np


def stl_finder2(feature_dataset):
    ftr_data = feature_dataset
    # configurables
    slope_lim = 2
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
    last_slope=0
    seg_found = False
    seg_num = 1
    seg_end=1
    seg_temp=[0,2,0,0,0,0]
    seg_temp_last=[0,1,0,0,0,1]
    seg_report_temp= [0,4,0,0,0,1]
    curr_delta_hrs=0
    seg_report = np.array(['Segment ID', 'Start (ind.)', 'End (ind.)', 'Start(DT)', 'End (dt)', 'slope'])
    seg_report_temp = np.vstack((seg_report, seg_temp))
    seg_report=seg_report_temp
    data_remaining = True

    while data_remaining is True:
        #Run seg finder
        seg_found = False
        seg_inc=1
        seg_start = seg_start_new
        if n == 713:
            print(n)

        while n+1 <= len(ftr_data['timestamps']):
            if len(ftr_data['timestamps']) <= n + 1:
                seg_found = True
                print('Reached end of features data')
                data_remaining = False
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

            if len(ftr_data['means']['Shaft Power']) < n+1:
                seg_found = True
                print('Reached end of features data')
                data_remaining = False
            else:
                if ftr_data['means']['Shaft Power'][n] == 0:
                    curr_slope=abs(last_slope)
                if ftr_data['means']['Shaft Power'][n] is None:
                    curr_slope=abs(last_slope)
                if ftr_data['timestamps'][n] is None:
                    curr_slope=abs(last_slope)
                if ftr_data['timestamps'][n] == 0:
                    curr_slope=abs(last_slope)
            # feature data is not null is segment is not found
            #print('Continue looking for segment if features data is not null')

                if len(ftr_data['timestamps']) <= n+1:
                    seg_found= True
                    print('Reached end of features data')
                    data_remaining = False
                    break
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
                    curr_slope=slope_func(x1, xn, y1, yn, last_slope)

                #slope is less than lim
                if slope_func(x1, xn, y1, yn,last_slope) <= slope_lim:
                    #print('test if seg is long enough')
                    #'Segment ID', 'Start (ind.)', 'End (ind.)', 'Start(DT)', 'End (dt)'
                    if int(curr_delta_hrs) >= seg_min:
                        seg_temp = np.array([seg_inc, seg_start, seg_start+curr_delta_hrs , seg_start, seg_end, curr_delta_hrs])
                        #seg_report_temp = np.vstack((seg_report, seg_temp))
                        #seg_report=seg_report_temp
                        n=n+1
                        #print('restarted the variables for segment finder')
                        curr_slope = slope_func(x1, xn, y1, yn,last_slope)


                seg_end=seg_end+1
                if slope_func(x1, xn, y1, yn,last_slope) >= slope_lim:
                    n=n+1
                    seg_start=n
            curr_slope=slope_func(x1, xn, y1, yn,last_slope)
            n=n+1

    #Segment Found greater than minimum length
    if seg_temp[5] >= seg_min:
        seg_temp = np.array([seg_inc, seg_start, seg_end, seg_start, seg_end, curr_delta_hrs])
        #record on table
        if seg_temp[2] != seg_temp_last[2]:
            seg_report_temp = np.vstack((seg_report, seg_temp))
            seg_report = seg_report_temp
            seg_inc=seg_inc+1
        else:
            print('STL found... findiing end')
        n=n+1
        seg_temp_last = seg_temp
        curr_slope = slope_func(x1, xn, y1, yn,last_slope)



        seg_start_last=seg_temp[5]
        seg_inc=seg_inc+1
        seg_start=n+1
        seg_found = False
        #if seg_end-seg_start <= seg_min:
         #   n=n+1



        if slope_func(x1, xn, y1, yn, last_slope) <= slope_lim:
            n=n+1
        #print(curr_slope)
        seg_start_new = seg_start
        n=n+1

    n=n+1
    return seg_report




def slope_func(x1, xn, y1, yn,last_slope):
    # Conv timestamps to datetime
    x1_dt = datetime.datetime.fromtimestamp(x1)
    xn_dt = datetime.datetime.fromtimestamp(xn)
    # find time diff in hours
    x_delta = xn_dt - x1_dt
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
    return slope
