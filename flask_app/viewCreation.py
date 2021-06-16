from database import database
from upsample import upsample

def reset_views():
	print('running function reset views on view creation page')
	db = database()
	db.reset_the_views(db.connection())

def create_training_view():
	print('running function create_training_view on view creation page')
	db = database()
	train_d = db.training_data(db.connection())
	ups = upsample()
	train_d['covid_or_not'] = train_d['content'].apply(ups.binary_covid_label)
	even_train_d = ups.upsample(train_d)
	ups.add_default(even_train_d)
	return even_train_d

def create_test_view():
	print('running function create_test_view on view creation page')
	db = database()
	test_d = db.test_data(db.connection())
	ups = upsample()
	test_d['covid_or_not'] = test_d['content'].apply(ups.binary_covid_label)
	ups.add_default(test_d)
	return test_d

def check_sizes(even_train_d, test_d):
	print('running function check_sizes on view creation page')
	db = database()
	views_sizes = db.check_views(even_train_d, test_d)
	return views_sizes


reset = reset_views()
train_view = create_training_view()
test_view = create_test_view()
check_sizes = check_sizes(train_view, test_view)