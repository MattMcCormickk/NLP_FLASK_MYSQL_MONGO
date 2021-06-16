# web (db and server) imports
from flask import Flask, render_template, request, url_for, jsonify, make_response
import pymysql 
import pymongo
from pymongo import MongoClient
# machine learning imports
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
# helpers
from collections import Counter
from datetime import datetime
# store binary files in mongo
import pickle
# json/bson handling
import json
from bson import ObjectId
#wordcloud
from io import BytesIO
import base64
#python pages
from database import database
import viewCreation
from upsample import upsample
from classifier import classifier
from cleanInput import cleanInput
from sklearn.feature_extraction.text import HashingVectorizer
#english dicitonary for covid or not prediciton
import enchant


# Connect to mongo
client = pymongo.MongoClient(#### INPUT YOUR MONGODB CONNECTION HERE####)
mdb = client.c2090152

app = Flask(__name__)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@app.route('/')
def home_page():
	return render_template('index.html')


@app.route('/views_created', methods=['GET','POST'])
def views_created():
	print('running function views_created on main page')
	# renders previously created views in the browser
	return render_template('index.html', train_d_html=viewCreation.train_view.head().to_html(), train_head="training data head", test_d_html=viewCreation.test_view.head().to_html(), test_head="test data head", views_sizes=viewCreation.check_sizes, views="data size")

@app.route('/experiment_done', methods=['GET','POST'])
def experiment_done():
	clsf = classifier()
	# fitting model
	fullmodel, nomodel = clsf.knn_classifier(viewCreation.train_view, viewCreation.test_view)
	# save models in mongodb
	mdb.fullModel.insert_one(fullmodel)
	mdb.noModel.insert_one(nomodel)
	return render_template('index.html', inserted_model=JSONEncoder().encode(nomodel), inserted_model_head="classification model report and time taken")

@app.route('/report', methods=['GET', 'POST'])
def retrieve_results():
	# return most recent model
	x = list(mdb.noModel.find().skip(mdb.noModel.count() - 1))

	# return quickest model 
	minmicroSeconds = list(mdb.noModel.find().sort('microseconds',1))
	# for some reason could not sort by seconds and microseconds hence below to find min second 
	minSeconds = min(minmicroSeconds, key=lambda x:x['seconds'])
	print(minSeconds['seconds'])
	for i in range(0, len(minmicroSeconds)):
	  if minmicroSeconds[i]['seconds'] == minSeconds['seconds']:
	    y = minmicroSeconds[i]
	    break

	# return most precise model
	z = list(mdb.noModel.find().sort('precision',-1).limit(1))
	return render_template('index.html', most_recent_head="Model most recently ran", most_recent=JSONEncoder().encode(x), quickest_head="Model that ran the quickest", quickest=JSONEncoder().encode(y), most_precise_head="Model with the highest precision", most_precise=JSONEncoder().encode(z))

@app.route('/submitted', methods=['POST'])
def submitted_form():
	#loading classifier and vector for most recent model
	classifier = pickle.loads(list(mdb.fullModel.find().skip(mdb.fullModel.count() - 1))[0]['model'])
	hashing = pickle.loads(list(mdb.fullModel.find().skip(mdb.fullModel.count() - 1))[0]['vector'])
	ci = cleanInput()
	print(request.form['input_text'])
	d = enchant.Dict("en_US") #most reddit comments will be in american-english
	word_list = []

	prediction_dict = {"input text": request.form['input_text'], "prediction": ""}

	for x in request.form['input_text'].split():
		word_list.append(d.check(x))

	#prevents model from making false positive prediction when there's no text in string that's a recognised word
	if True not in word_list:
		print('gibberish!')
		prediction_dict["prediction"] = "this text is NOT likely to be about coronavirus"
	else:
		print('words included')
		#preprocess text input
		text = ci.superclean(request.form['input_text'])
		text = ci.preprocess(text)

		#fit input to vector	 
		text = hashing.transform([text])
		y_prediction = classifier.predict(text)
		print(y_prediction)

		#return prediction
		for result in y_prediction:
		  if result == 1:
		    print("this text is likely about coronavirus")
		    prediction_dict["prediction"] = "this text is likely to be about coronavirus"
		  else:
		    print("this text is NOT likely to be about coronavirus")
		    prediction_dict["prediction"] = "this text is NOT likely to be about coronavirus"
	return render_template('index.html', predicition=prediction_dict)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)
