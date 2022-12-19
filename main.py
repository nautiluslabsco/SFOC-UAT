import feature_import as feature_import
import stl_finder
import SFOC_rule1

# Config
print(" ")
print("-------------------- Features Ruleset Engine--------------------")
ship_id = 61
feature_name = 'SFOC'
sample_size= 30  # Days
results_file_name = "%s_test_ship_%s.csv" % (feature_name, ship_id)
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
stl_data = stl_finder.stl_finder(feature_dataset)
# return format = SectionID | Start  | End
print("Segments Identified Successfully!")
print("")

##-------------    SFOC Rules    ----------------------##
# Rule 1 - Test min max of stl sections
print("Running Rule 1 over STL segments")
sfoc_1_results=SFOC_rule1.SFOC_rule1(stl_data)  #format = SectionID | Start | End | pass/fail | reason
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
print(sfoc_1_results)
#print("*imagine this is formatted better")
##----##
print("")
# Print UAT Report

#print('SectionID | Start | End | pass/fail | reason')
print("-------------------- Goodbye --------------------")
