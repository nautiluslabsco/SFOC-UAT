import sample_data as sample_data
import numpy as np
import datetime

#Config
feature_name= "SFOC"
flat_lim= 10
i=1
n=1
flat_len=20 #hrs


#Sample data import
print("Importing feature data to STL module...")
dataset=sample_data.sample_data()
feature_data = np.array(dataset['means'][feature_name])
#print(len(feature_data))
dt_data = np.array(dataset['timestamps'])
#swtich features dict to array and append datetime
ftr_data = np.stack((dt_data,feature_data))
if len(ftr_data[1])<5:
    print("Import Failed...")
    print("Exiting!")
else:
    print("Import Successful!")

#Response
print("Identifying Zero(ish) slope segments...")
#print(len(dataset["timestamps"]))


#initialize vars
seg_flat=[],[],[]
seg_start=0
curr_slope=0
NoneType = type(None)
seg_num=1
n=1
seg_inc=1
seg_len_temp=0
#print(NoneType)
#y_dist_hrs=(ftr_data[0][2] - ftr_data[0][1])/(60*60*60)
#print(y_dist_hrs)
#n-1 case slope is okay
#n case slope is okay
#n+1 case slope is above limit
#print(type(ftr_data[1][1]))


def inst_slope(point_0, point_n, data):
    #print('x v y')
    #print(ftr_data[0][point_n])
    #print(ftr_data[1][point_n])
    x_dist = ftr_data[1][point_n]-ftr_data[1][point_0]
    y_dist_hrs = (ftr_data[0][point_n] - ftr_data[0][point_0])/(60*60)
    i_slope = x_dist/y_dist_hrs
    #i_slope = 0
    print('  |-> Slope Found....' + str(i_slope) + '')
    #print(i_slope)
    return i_slope


while i < len(ftr_data[1]):
    if i+1 > len(ftr_data[1]):
        #End slop finder before end of data
        print("Reached end of Data....")
        break
    else:
        #If data positions are valid, cont.
        if type(ftr_data[1][i]) is NoneType:
            #Filter out null data
            status = 3
        elif type(ftr_data[1][i+1]) is NoneType:
            #filter out null data of future slope
            status = 4
            #print("No slope for " + str(i) + "")
            #print("  |-> Datatype is: " + str(type(ftr_data[1][i])))
            #print(i)
            #print("----------------")
            #print("i")
            #print(type((ftr_data[1][i])))
            #print("i+1")
            #print(type((ftr_data[1][i+1])))
        else:
            slope_temp=inst_slope(i, i + 1, ftr_data) < flat_lim:
            if slope_temp < flat_lim:
                #Find inst slope of current segment if under slope lim
                status = 2
                print("Calculating slope!")
                seg_slope = inst_slope(i, i + 1, ftr_data)
                seg_end = i
                seg_start = n
                seg_temp = [seg_inc, seg_start, seg_end ]
                #seg_end = i
                #seg_flat[1][n] = seg_num
                #seg_flat[2][seg_num] = [seg_start, seg_end]
                    n = n+1
                seg_len_temp = seg_len_temp + 1
            else
                seg_inc = seg_inc + 1
                seg_len_temp = 0
        #else:
            #status = 1
            #print('Finding slope for: ' + str(i) + '...')
            #curr_slope = inst_slope(i, i+1, ftr_data)

    #Finding next slope
    i = i + 1

print(seg_flat)

#print(shaft_power_dt)
#print(feature_data)


#print([dataset]["means"]["Shaft Power"])

#stl_segments= [0]
stl_results=[0,0]
#print(len(stl_results['seg']))

if len(stl_results) <= 1:
    print('ERROR: No STL segments identified in this data set')
    print('...')
else:
    print("Complete... returning results")
#    return stl_segments
# return format = SectionID | Start  | End


