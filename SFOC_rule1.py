from typing import List
import numpy as np
import sample_data


def SFOC_rule1(stl_data):
    feature_dataset= sample_data.sample_data()
    feature='SFOC'
    SFOC_min = 100
    SFOC_max = 550
    NoneType = type(None)
    #temp_array=[]
    results = np.array(["Segment ID", "start_pt", "end_pt", "Result", "Reason"])
    n=1
    #print(stl_data)
    #print(len(stl_data[1]))
    print("     |-> SFOC Rule 1 check")
    while n < len(stl_data[1])-1:
        #print(n)
        start_pt = int(stl_data[n][1])
        #print(start_pt)
        end_pt = int(stl_data [n][2])
        #print(end_pt)
        temp_array= np.array(feature_dataset['means'][feature][start_pt:end_pt])
        #mod_array = [i for i in temp_array if i is not None]
        conv = lambda i: i or 0
        mod_array = [conv(i) for i in temp_array]
        #print(temp_array)
        #print (mod_array)
        #temp_array[temp_array == None] = 0
        #np.place(temp_array, temp_array == NoneType, 0)
        #print(type(mod_array))
        #print(min(mod_array))
        #print(max(mod_array))
        print('          |-> Analyzing Segment ' , start_pt, ' -> ' , end_pt , ' ')
        #temp_min=
        #temp_max=
        print( '          | Min = ', min(mod_array), ', Max = ', max(mod_array),'|' )
        #print(temp_array)
        #print(n)
        if min(mod_array) < SFOC_min:
            results_temp = np.array([n, start_pt, end_pt, "FAIL", "Reason, SFOC < Min"])
            results_temp_append = np.vstack((results, results_temp))
            results=results_temp_append
        elif max(mod_array) > SFOC_max:
            results_temp = np.array([n, start_pt, end_pt, "FAIL", "Reason, SFOC < Max"])
            results_temp_append = np.vstack((results, results_temp))
            results=results_temp_append
        n=n+1
    print("     |-> SFOC Rule 1 check COMPLETE")
    print("     |-> Returning Results...")
    #print(results)

    return results