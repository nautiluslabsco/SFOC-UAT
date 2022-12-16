import sample_data as sample_data
import numpy as np
import datetime

#Config


def stl_finder(feature_dataset):
    feature_name = "Shaft Power"
    slope_lim = 10
    i = 1
    n = 1
    flat_len = 10  # hrs
    #Sample data import
    print("     |-> Importing feature data to STL module...")
    dataset=feature_dataset
    feature_data = np.array(dataset['means'][feature_name])
    #print(len(feature_data))
    dt_data = np.array(dataset['timestamps'])
    #swtich features dict to array and append datetime
    ftr_data = np.stack((dt_data,feature_data))
    if len(ftr_data[1])<5:
        print("     |-> Import Failed...")
        print("     |-> Exiting!")
    else:
        print("     |-> Import Successful!")

    #Response
    #print("Identifying Zero(ish) slope segments...")
    #print(len(dataset["timestamps"]))


    #initialize vars
    seg_report = np.array(['Segment ID', 'Start', 'End'])
    seg_start=0
    curr_slope=0
    NoneType = type(None)
    seg_num=1
    n=1
    seg_inc=1
    seg_len_temp=0
    seg_end=0
    run_complete=False
    seg_start=0
    #print(NoneType)
    #y_dist_hrs=(ftr_data[0][2] - ftr_data[0][1])/(60*60*60)
    #print(y_dist_hrs)
    #n-1 case slope is okay
    #n case slope is okay
    #n+1 case slope is above limit
    #print(type(ftr_data[1][1]))


    def inst_slope(point_0, point_n, data):
        x_dist = ftr_data[1][point_n]-ftr_data[1][point_0]
        y_dist_hrs = (ftr_data[0][point_n] - ftr_data[0][point_0])/(60*60)
        i_slope = x_dist/y_dist_hrs
        return i_slope


    while i+1 < len(ftr_data[1]):
        if i+1 > len(ftr_data[1]):
            #End slop finder before end of data
            print("     |-> Reached end of Data....")
            break
        elif type(ftr_data[1][i]) is NoneType or type(ftr_data[1][i+1]) is NoneType:
            i = i+1
        else:
            #If data positions are valid, cont.
            #print('Analyzing Segment')
            #print(type(ftr_data[1][i+1]))
            seg_start = i
            n = i+1
            seg_complete=False
            seg_temp = np.array([0, 0, 0])
            while seg_complete is False and run_complete is not True:
                # data is not null and  next data is not null and slope is less than limit
                if len(ftr_data[1]) < n+2:
                    #print('Found end of Segment!!!!')
                    #print("(Arrived at end of data)")
                    seg_end=len(ftr_data[1])
                    seg_complete=1
                    run_complete = True
                elif type(ftr_data[1][n]) is NoneType or type(ftr_data[1][n+1]) is NoneType:
                    #print('Found end of Segment!!!!')
                    #print("(Next Datapoint is Null)")
                    seg_end = n
                    i = seg_end
                    seg_complete = True
                else:
                    #print('analysing slope')
                    slope_temp = inst_slope(seg_start, n + 1, ftr_data)
                    seg_end = n
                    i = seg_end
                    n = n + 1

            if seg_end-seg_start > flat_len:
                #record data to table
                seg_temp = np.array([seg_inc, seg_start, seg_end])
                seg_report_temp=np.vstack((seg_report, seg_temp))
                #print(seg_temp)
                seg_report=seg_report_temp
                #print(seg_report)
                seg_end = n
                i = seg_end
                seg_inc=seg_inc+1
                seg_complete = True
            else:
                i=n+i
                seg_complete = True
                seg_end = n
                i = seg_end


    if len(seg_report) <= 1:
        print('     |-> ERROR: No STL segments identified in this data set')
        print('...')
    else:
        print("     |-> Complete... returning results")
        return seg_report
    # return format = SectionID | Start  | End


