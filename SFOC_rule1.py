from typing import List
import numpy as np
import sample_data


def SFOC_rule1(stl_data):
    feature_dataset= sample_data.sample_data()
    feature='SFOC'
    NoneType = type(None)
    temp_array=[]
    n=1
    #print(stl_data)
    #print(len(stl_data[1]))
    while n < len(stl_data[1]):
        #print(n)
        start_pt = int(stl_data[n][1])
        end_pt = int(stl_data [n][2])
        temp_array= np.array(feature_dataset['means'][feature][start_pt:end_pt])
        np.place(temp_array, temp_array == NoneType, 0)
        print('          |-> Analyzing ' , start_pt, ' -> ' , end_pt , ' ')
        print( '                 Max = ', max(temp_array), '| Min = '. min(temp_array))
        #print(temp_array)
        n=n+1

    print("     |-> SFOC Rule 1 check")

    results=0

    return results