import sample_data
import stl_finder2
import SFOC_rule1_dt

feature_dataset= sample_data.sample_data()
#print(feature_dataset['means']['Shaft Power'])

stl_data = stl_finder2.stl_finder2(feature_dataset)

#print (stl_data)





sfoc_1_results=SFOC_rule1_dt.SFOC_rule1_dt(stl_data)  #format = SectionID | Start | End | pass/fail | reason
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

#Print UAT Report

file=open(results_file_name, 'a+' , newline = '')

with file:
    write = csv.writer(file)
    write.writerows(sfoc_1_results)


#Close File
file.close()
print("")
print("-------------------- Goodbye --------------------")


