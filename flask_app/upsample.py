import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

class upsample:
	def binary_covid_label(self, training_data):
		#labels data relative to inclusion of below words
	    if "corona" in training_data:
	    	return 1
	    elif "covid" in training_data:
	        return 1
	    elif "china" in training_data:
	    	if "flu" in training_data:
	    		return 1
	    	else:
	    		return 0
	    else:
	    	return 0


	def upsample(self, training_data):
		#separating covid and non covid posts
		df_minority  = training_data[training_data['covid_or_not']==1]
		df_majority = training_data[training_data['covid_or_not']==0]
		#upsample covid posts
		df_minority = df_minority.sample(len(df_majority), random_state=0, replace=True)
		#rejoin covid and non covid posts
		df = pd.concat([df_majority,df_minority], ignore_index=True)
		training_data = df.sample(frac=1, random_state=0)
		return training_data


	#wanted to show even bar chart after upsampling but not used in the end
	def bar_chart(self, training_data):
		#bar chart showing balance of covid vs non-covid data
		plt.title("covid balance of training data")
		return plt.bar(dict(Counter(training_data['covid_or_not'])).keys(), dict(Counter(training_data['covid_or_not'])).values())
		# plt.show()

	def add_default(self, data):
		data.get('covid_or_not', default='none')
