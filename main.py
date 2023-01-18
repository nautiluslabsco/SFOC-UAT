import SFOC_rule1_dt
import feature_import as feature_import
import stl_finder
import stl_finder2
import SFOC_rule1
from datetime import datetime
import time
import csv
import sys

# Config
print(" ")
print("-------------------- Features Ruleset Engine--------------------")
ship_id = 61
feature_name = 'SFOC'
sample_size= 30  # Days
now=datetime.now()
current_time = now.strftime("%m%d%Y %H%M%S")
results_file_name = "%s_test_ship_%s %s.csv" % (feature_name, ship_id, current_time)

print("Date: ", now.strftime("%m/%d/%Y"))
print("Time: ", now.strftime("%H:%M:%S"))
print(" ")
print("      Configuration: ")
print("       |->Ship ID:", str(ship_id))
print("       |->Sample Size:", str(sample_size))
print("       |->Target Feature:", feature_name)

print("")
print("Beginning Analysis...")
##-----------     Feature Import    -------------------##
print("Requesting features data from QA env....")
feature_dataset = feature_import.feature_import(ship_id, feature_name, sample_size)
# format = Datetime | speed thru water| Shaft Power | SFOC
print("Data Import Complete!")
print("")
#print(feature_dataset)

##-----------     STL Finder    -----------------------##
print("Identifying straight-line (stl) segments of the data (constant speed for configured time)")
#stl_data = stl_finder.stl_finder(feature_dataset)
stl_data = stl_finder2.stl_finder2(feature_dataset)
# return format = SectionID | Start  | End
print("STL Finder Ran Successfully!")
print("")

print(stl_data)

##--QUIT IF NO STL--##
if len(stl_data)<=2:
    sys.exit("ERROR:NO STRAIGHT LINE SEGMENTS FOUND IN DATA... \n exiting program...")

##-------------    SFOC Rules    ----------------------##
# Rule 1 - Test min max of stl sections
print("Running Rule 1 over STL segments")
#sfoc_1_results=SFOC_rule1_dt.SFOC_rule1_dt(stl_data)  #format = SectionID | Start | End | pass/fail | reason
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
#print(sfoc_1_results)
#print("*imagine this is formatted better")
##----##

#Print UAT Report

file=open(results_file_name, 'a+' , newline = '')

with file:
    write = csv.writer(file)
    #write.writerows(sfoc_1_results)


#Close File
file.close()
print("")
print("-------------------- Goodbye --------------------")


