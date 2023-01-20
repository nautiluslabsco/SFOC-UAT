import sample_data
import stl_finder2
import SFOC_rule1_dt
from datetime import datetime
import csv

feature_dataset= sample_data.sample_data()
#print(feature_dataset['means']['Shaft Power'])

stl_data = stl_finder2.stl_finder2(feature_dataset)

print (stl_data)

# Config
print(" ")
print("-------------------- Features Ruleset Engine--------------------")
ship_id = 61
feature_name = 'SFOC'
sample_size= 150  # Days
now=datetime.now()
current_time = now.strftime("%m%d%Y %H%M%S")
results_file_name = "%s_test_ship_%s %s.csv" % (feature_name, ship_id, current_time)

print("Compiling Results...")
print("")

##-----##
# Rule 2 - ....
print("Running Rule 2 over STL segments")
print("Compiling Results...")
print("")

##-------------    UAT Report    ---------------------##
# Assemble Results
print("-----------RESULTS-----------")
#print("*imagine this is formatted better")
##----##

#Print UAT Report

file=open(results_file_name, 'a+' , newline = '')

with file:
    write = csv.writer(file)
    write.writerows(' ')


#Close File
file.close()
print("")
print("-------------------- Goodbye --------------------")


