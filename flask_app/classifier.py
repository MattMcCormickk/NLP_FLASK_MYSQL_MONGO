import pandas as pd
from pandas import DataFrame
# numpy and a Counter class
import numpy as np
from collections import Counter
# sklearn!
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn import metrics
import datetime
import json
import pickle

class classifier:
	def knn_classifier(self, training_data, test_data):
		#setting the data splt
		X_train, X_test, y_train, y_test = training_data['content'], test_data['content'], training_data['covid_or_not'], test_data['covid_or_not']
		
		#vectorizing data
		hashing = HashingVectorizer()
		training_data = hashing.fit_transform(X_train)
		testing_data = hashing.transform(X_test)

		begin = datetime.datetime.now()

		###### originally used the turkish knn to find the optimum value of n but takes 2 minutes to run
		###### and i don't have any patience but I ran enough times to reliably say the most optimum value is 1 

		# knn = KNeighborsClassifier()
		# #create a dictionary of all values we want to test for n_neighbors
		# param_grid = {'n_neighbors': np.arange(1, 10)}
		# #use gridsearch to test all values for n_neighbors
		# knn_gscv = GridSearchCV(knn, param_grid, cv=5)
		# #fit model to data
		# knn_gscv.fit(training_data, y_train)
		# #check top performing n_neighbors value
		# optimal_k_value = knn_gscv.best_params_['n_neighbors']
		# print('The optimal k value is: ' + str(optimal_k_value.item()))
		# classifier = KNeighborsClassifier(n_neighbors= optimal_k_value.item())

		#fitting data to model
		classifier = KNeighborsClassifier(1)
		classifier.fit(training_data,y_train)
		
		#generating report
		y_pred = classifier.predict(testing_data)
		report = metrics.classification_report(y_test, y_pred, output_dict=True)

		#format report for mongo stroage
		report_df = pd.DataFrame(report).transpose()
		report_df = report_df.to_dict()
		#took average of precision so I can easily find the most precise model
		report_df['precision'] = sum(list(report_df['precision'].values())) / 5
		report_df['recall'] = list(report_df['recall'].values())
		report_df['f1-score'] = list(report_df['f1-score'].values())
		report_df['support'] = list(report_df['support'].values())

		#time taken for model to run
		end = datetime.datetime.now()
		time_taken = end - begin

		#for time_taken for mongo stroage
		time_taken_json = {
			'days' : time_taken.days,
			'seconds' : time_taken.seconds,
			'microseconds' : time_taken.microseconds,
		}

		
		#pickling model and vector to store in mongo
		pickle_vector = pickle.dumps(hashing)
		pickle_vector_dict = {'vector': pickle_vector} 
		pickle_model = pickle.dumps(classifier)
		pickle_model_dict = {'model': pickle_model}

		full_model = {}
		no_model = {}
		#inserting model/vector/report/time into collections
		for d in pickle_model_dict, pickle_vector_dict, report_df, time_taken_json:
		  full_model.update(d)
		for d in report_df, time_taken_json:
			no_model.update(d)
		# print(no_model)
		return full_model, no_model



