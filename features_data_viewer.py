
import sample_data as sample_data
import numpy

feature='SFOC'

features_dataset=sample_data.sample_data()
timestamps=features_dataset['timestamps']
features_data=features_dataset['means'][feature]

features_dt=numpy.vstack((timestamps,features_data))

print(features_dt[1][150])
