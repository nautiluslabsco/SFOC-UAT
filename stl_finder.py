import sample_data as sample_data

feature_name= "Shaft Power"
#def stl_finder(dataset):
dataset=sample_data.sample_data()
print("Identifying Zero(ish) slope segments")
#print(dataset["timestamps"])
if feature_name in dataset['means']:
    matching_feature_name = feature_name
    feature_data = dataset['means'][feature_name]
else:
    for feature_data_name in dataset['means']:
        if feature_name in feature_data_name:
            matching_feature_name = feature_data_name
            feature_data = dataset['means'][feature_data_name]
            break

shaft_power_dt = {dataset["timestamps"]:feature_data()}
print(shaft_power_dt)
#print(feature_data)


#print([dataset]["means"]["Shaft Power"])

#stl_segments= [0]



#    return stl_segments
# return format = SectionID | Start  | End
