Project:
A web application that predicts if user text entry is likely to be about covid-19 based on a knn classification model,
trained on data scraped from Reddit. 

create_sql_db Script:
1. cleans and prepares data scraped from Reddit for data insertion
2. inserts data into mysql DB in 3NF

Flask Application:
1. Retrieves MySQL data to train a classification model 
2. Implements model on test data and stores model/results in MongoDB
3. Retrieves results from experiment done so far (quickest, most precise, most recent)
4. Predicts classification based on text input

Add database connections:
- main.py line 35 (add mongoDB connection)
- database.py line 8 (add mysql connection)
- create_sql_db line 186 (add mysql connection)

Run Flask application with following terminal commands:
- export FLASK_APP=main.py
- python -m flask run


N.B.1. CSS seems to work better in Chrome

