
from datetime import datetime


#configurables
slope_lim=1

#Variable intialize
slope = 0
seg_start_new = 1
n = 0

while slope >= slope_lim:
    #Set Vars for net seg
    seg_start=seg_start_new
    n = n+1

    #Find data for slope calc
    #TimeSpan in <time units>
    xn = ftr_data[1][n]
    x1 = ftr_data[1][seg_start]

    #Data Values at n
    yn = ftr_data[1][n]
    y1 = ftr_data[1][seg_start]

    slope = slope_func(x1,xn,y1,yn)

    seg_start_new = n + 1


def slope_func(x1,xn,y1,yn):
    #conv timestamps to datetime
    x1_dt = datetime.datetime.fromtimestamp(x1 / 1e3)
    xn_dt = datetime.datetime.fromtimestamp(xn / 1e3)
    #find time diff in hours
    x_delta = (xn_dt-x1_dt).total.hours



    return slope


def inst_slope(point_0, point_n, data):
    x_dist = ftr_data[1][point_n]-ftr_data[1][point_0]
    y_dist_hrs = (ftr_data[0][point_n] - ftr_data[0][point_0])/(60*60)
    i_slope = x_dist/y_dist_hrs
    return i_slope
