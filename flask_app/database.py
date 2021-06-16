import pymysql
import pandas as pd
from pandas import DataFrame

class database:
	def connection(self):
		#db connection sql
		con = pymysql.connect(####INPUT MYSQL SB CONNECTION HERE)
		cur = con.cursor()
		return cur

	def reset_the_views(self, cur):
		cur.execute("drop view  if exists TrainingView;")
		cur.execute("drop view  if exists TestView;")
		print('Successfully dropped training_data and test_data views', flush=True)


	def training_data(self, cur):
		# getting training view
		cur.execute("SET @sql := CONCAT( 'create VIEW TrainingView AS select post.post_name, subreddit.subreddit_name from post join subreddit on post.subredditID = subreddit.subredditID order by rand() limit ', (select round(count(*)*0.8) FROM post));")
		cur.execute("PREPARE stmt FROM @sql;")
		cur.execute("EXECUTE stmt;")
		cur.execute("select * from TrainingView;")
		result = cur.fetchall()
		data = []
		for x in result:
			data.append(x)
		#convert to dataframe format
		training_data = pd.DataFrame(data, columns = ['post', 'subreddit'])
		training_data['content'] = training_data["post"] + " " + training_data['subreddit']
		training_data = pd.DataFrame(training_data['content'], columns = ['content']) 
		print('Successfully created training_data view', flush=True)
		return training_data


	def test_data(self, cur):
		#getting test view
		cur.execute("create VIEW TestView AS select post.post_name, subreddit.subreddit_name from post join subreddit on post.subredditID = subreddit.subredditID WHERE (post_name, subreddit_name) not in (Select * from TrainingView);")
		cur.execute("select * from TestView;")
		result = cur.fetchall()
		data = []
		for x in result:
			data.append(x)
		#convert to dataframe format
		test_data = pd.DataFrame(data, columns = ['post', 'subreddit'])
		test_data['content'] = test_data["post"] + " " + test_data['subreddit']	
		test_data = pd.DataFrame(test_data['content'], columns = ['content']) 
		print('Successfully created test_data view', flush=True)
		return test_data

	def check_views(self, x, y):
		#gets the shape of the views
		return f'training data size: X = {x.shape[0]} and test data size: y = {y.shape[0]}'




