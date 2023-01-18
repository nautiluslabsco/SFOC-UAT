import sample_data
import datetime
import pandas as pd
import numpy as np


def stl_finder2(feature_dataset):
    ftr_data = feature_dataset
    # configurables
    slope_lim = 2

    # Variable intialize
    slope = 0
    seg_start_new = 1
    n = 0
    seg_find = True
    seg_num = 1
    seg_report = np.array(['Segment ID', 'Start (ind.)', 'End (ind.)', 'Start(DT)', 'End (dt)'])
    data_remaining = True

    while data_remaining is True:
        #Run seg finder
        if ftr_data['means']['Shaft Power'][n] == 0:
            seg_find = False
            n = n + 1
        seg_find = True
        while seg_find is True:
            # Set Vars for net seg
            seg_start = seg_start_new
            n = n + 1
            print(n)
            if ftr_data['means']['Shaft Power'][n] == 0:
                seg_find = False
                n=n+1
            x1 = ftr_data['timestamps'][seg_start]
            y1 = ftr_data['means']['Shaft Power'][seg_start]
            if n == 734:
                print("Breakpoint at point:", n)
           #Breakpoint for loop when end of data
            if n+1 == len(ftr_data['timestamps']):
                print("Reached end of data....")
                if slope_func(x1, ftr_data['timestamps'][n], y1, ftr_data['means']['Shaft Power'][n]) >= slope_lim:
                    print("...")
                    print("Found matching segment!!!")
                    print("Segment # ", seg_num)
                    print("Start Point : ", datetime.datetime.fromtimestamp(x1))
                    print("Endpoint : ", datetime.datetime.fromtimestamp(xn))
                    seg_temp = np.array(
                        [seg_num, datetime.datetime.fromtimestamp(x1), datetime.datetime.fromtimestamp(xn)])
                    seg_report = np.vstack((seg_report, seg_temp))
                print("...")
                print("STL ANALYSIS COMPLETE...")
                data_remaining = False
                seg_find = False

            if n + 1 < len(ftr_data['timestamps']):
                # Find data for slope calc
                # TimeSpan in <time units>
                xn = ftr_data['timestamps'][n + 1]
                #xn_1 = ftr_data['timestamps'][n + 1]
                # Data Values at n
                yn = ftr_data['means']['Shaft Power'][n + 1]
                #yn_1 = ftr_data['means']['Shaft Power'][n + 2]
                #print(n)




                # Test slope of next point
            if slope_func(x1, xn, y1, yn) >= slope_lim:
                seg_start_new = n + 1
                print("...")
                print("Found matching segment!!!")
                print("Segment # ", seg_num)
                print("Start Point : ", datetime.datetime.fromtimestamp(x1))
                print("Endpoint : ", datetime.datetime.fromtimestamp(xn))
                seg_temp = np.array([seg_num, datetime.datetime.fromtimestamp(x1), datetime.datetime.fromtimestamp(xn)])
                seg_report = np.vstack((seg_report, seg_temp))
                print(ftr_data['means']['Shaft Power'][n])
                seg_find = False

    if len(seg_report) <= 3:
        print('     |-> ERROR: No STL segments identified in this data set')
        print('...')
        return [0, 0, 0, 0]

    else:
        print("     |-> Complete... returning results")
        return seg_report




def slope_func(x1, xn, y1, yn):
    # Conv timestamps to datetime
    x1_dt = datetime.datetime.fromtimestamp(x1)
    xn_dt = datetime.datetime.fromtimestamp(xn)
    # find time diff in hours
    x_delta = xn_dt - x1_dt
    x_delta_hrs = (x_delta.total_seconds()) / (60 * 60)

    # Calculate rise
    y_delta = yn - y1
    # Rise over run... right... cant remember, check this later, or right now
    slope = y_delta / x_delta_hrs
    # print(slope)
    # Change in
    return slope
