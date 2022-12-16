import feature_import as feature_import
import stl_finder
import SFOC_rule1

# Config
ship_id = 61
feature_name = 'SFOC'
sample_size= 31  # Days
results_file_name = "%s_test_ship_%s.csv" % (feature_name, ship_id)

##-----------     Feature Import    -------------------##
print("Importing features data from QA platform for specific SHIPID and time period....")
feature_dataset = feature_import.feature_import(ship_id, feature_name, sample_size)
# format = Datetime | speed thru water| Shaft Power | SFOC
print("Import Complete!")
#print(feature_dataset)

##-----------     STL Finder    -----------------------##
print("Identifying straight-line (stl) segments of the data (constant speed for ~36 hours)")
stl_data = stl_finder.stl_finder(feature_dataset)
# return format = SectionID | Start  | End
print("Segments Identified Successfully")

##-------------    SFOC Rules    ----------------------##
# Rule 1 - Test min max of stl sections
print("Running Rule 1")
sfoc_1_results=SFOC_rule1.SFOC_rule1(stl_data)  #format = SectionID | Start | End | pass/fail | reason
print("Rule One complete!")
##-----##
# Rule 2 - ....


##-------------    UAT Report    ---------------------##
# Assemble Results

##----##

# Print UAT Report

#print('SectionID | Start | End | pass/fail | reason')
