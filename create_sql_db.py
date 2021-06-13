import csv
import json
import pymysql
import string
import re
from stop_words import get_stop_words
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer
import Flask_web_app.Info.privateinfo as pv

#used to get data into ascii form
printable = set(string.printable)
def superclean(s):
    out = ''
    for char in s:
        if char in printable:
            out += char
    return out

def preprocess(s):
    #Remove any non alphabetical values
    s = re.sub("[^a-zA-Z]", " ", s)
    #lower case for uniformity
    words = s.lower().split()
    #lemmatize and stem
    lemmatizer = PorterStemmer()
    stemmed_words = []
    for word in words:
        word = lemmatizer.stem(word)
        stemmed_words.append(word)
        # converting list back to string
    return " ".join(stemmed_words)

def preprocess_subreddit(s):
    #lower case for uniformity
    words = s.lower().split()
    #lemmatize and stem
    lemmatizer = PorterStemmer()
    stemmed_words = []
    for word in words:
        word = lemmatizer.stem(word)
        stemmed_words.append(word)
        # converting list back to string
    return " ".join(stemmed_words)

csvfile = r'data_portfolio_21.csv'
jsonfile = r'data_portfolio_21_json.json'
 
# Function to convert a CSV to JSON
# Takes the file paths as arguments
def make_json(csvfile, jsonfile):

    data = []
    # Open a csv reader called DictReader
    fieldnames = ('author', 'posted_at', 'num_comments', 'score', 'selftext', 'subr_created_at', 'subr_description', 'subr_faved_by', 'subr_numb_members',
        'subr_numb_posts', 'title', 'total_awards_received', 'upvote_ratio', 'user_num_posts', 'user_registered_at', 'user_upvote_ratio')

    with open(csvfile, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        field = csvReader.fieldnames
        # Convert each row into a dictionary
        # and add it to data
        for row in csvReader:
            data.extend([{field[i]:row[field[i]] for i in range(len(field))}])

    with open(jsonfile, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))
         
# Call the make_json function
# changed to json to speed up run time
make_json(csvfile, r'data_portfolio_21_json.json')

#loading json data
reddit_data = json.load(open('data_portfolio_21_json.json'))
#declaring empty dictionary's
subreddit_map, user_map, subscriber_map, post_map, usersub_map = {}, {}, {}, {}, {}
#declaring empty lists
subredditList, userList, authorList, subscriberList, voteList, awardList, postList, postListprep, subscriber_to_subreddit_list = [], [], [], [], [], [], [], [], []

#looping through whole data set
for i in range(len(reddit_data)):

    #creating field lists based off column headers
    Author = reddit_data[i]['author']
    posted_at = reddit_data[i]['posted_at']
    num_comments = int(reddit_data[i]['num_comments'])
    score = int(reddit_data[i]['score'])
    selftext = reddit_data[i]['selftext']
    subr_created_at = reddit_data[i]['subr_created_at']
    subr_description = reddit_data[i]['subr_description']
    subscribers = reddit_data[i]['subr_faved_by'].split()
    subr_numb_members = int(reddit_data[i]['subr_numb_members'])
    subr_numb_posts = int(reddit_data[i]['subr_numb_posts'])
    subreddit = reddit_data[i]['subreddit']
    title = reddit_data[i]['title']
    total_awards_received = int(reddit_data[i]['total_awards_received'])
    upvote_ratio = float(reddit_data[i]['upvote_ratio'])
    user_num_posts = int(reddit_data[i]['user_num_posts'])
    user_registered_at = reddit_data[i]['user_registered_at']
    user_upvote_ratio = float(reddit_data[i]['user_upvote_ratio'])

    #gettings values in ascii form
    Author, posted_at, selftext, subr_created_at, subr_description, subreddit, title, user_registered_at = superclean(Author), superclean(posted_at), superclean(selftext), superclean(subr_created_at), superclean(subr_description), superclean(subreddit), superclean(title), superclean(user_registered_at)

    #preprocessing data which will later be used for classification
    selftext = preprocess(selftext)
    selftext = selftext[0:1000]
    title = preprocess(title)
    subreddit = preprocess_subreddit(subreddit)

    #adding subreddits to dictionary with increasing value for ID
    if not subreddit in subreddit_map: 
        subreddit_map[subreddit] = len(subreddit_map) + 1

    subredditID = subreddit_map[subreddit]

    #put in list form for mysql entry
    subredditList.append((subredditID, subreddit, subr_created_at, subr_description, subr_numb_posts, subr_numb_members))
    #removes all duplicates from list
    subredditList = list(dict.fromkeys(subredditList))

    #using author column to get some of the user names
    user_name = Author
    if not user_name in user_map:
        user_map[user_name] = len(user_map) + 1

    authorID = user_map[user_name]
    UserID = authorID

    authorList.append((authorID, UserID, user_num_posts, user_upvote_ratio, user_registered_at))
    #removes all duplicates from list (very inefficient approach for run time)
    authorList = list(dict.fromkeys(authorList))

    #creating postID
    postListprep.append(title) 
    for i in range(1, (len(postListprep) + 1)):
        postID = i

    #creating award and voteID
    awardID = voteID = postID
    #creating vote list. has no duplicates
    voteList.append((voteID, postID, score, upvote_ratio))

    selftext
    #creating post and award list
    postList.append((postID, title, posted_at, authorID, subredditID, selftext, num_comments))
    awardList.append((awardID, postID, total_awards_received))

    #removes empty bracket values. change to checking for alpha
    subscribers = [s for s in subscribers if re.search('[a-zA-Z]', s)]

    for sub in subscribers: 
        #removing junk from subscribers, keeping [***] used to blank out nsfw words
        sub = sub.replace(",", "")
        sub = sub.replace("'", "")
        if sub[0] == '[':
            if sub[1] != '*':
                sub = sub[1:]
        if sub[-1] == ']':
            if len(sub) > 2:
                if sub[-2] != '*':
                    sub = sub[:-1]
        #adding subscriber to dictionary's
        if not sub in subscriber_map:
            subscriber_map[sub] = len(subscriber_map) + 1
        if not sub in user_map:
            user_name = sub 
            user_map[user_name] = len(user_map) + 1
        subscriber_to_subreddit_list.append((sub, subredditID))

    subscribers = superclean(subscribers)

    userID = user_map[user_name]
    subscriberID = subscriber_map[sub]

    #creating user list and removing duplicates
    userList.append((userID, user_name))

userList = list(dict.fromkeys(userList))
#removes duplicates
subscriber_to_subreddit_list = list(dict.fromkeys(subscriber_to_subreddit_list))
#swap subscriber name for user ID
subscriber_to_subreddit_list = [(uValue, z) for (x, z) in subscriber_to_subreddit_list for uKey, uValue in user_map.items() if uKey == x]
#subscriber_to_subreddit_list used as subscriber table to avoid mulitvalue columns

# Connect to the database
connection = #### input sql connection here ####


try:
    with connection.cursor() as cur:
        q = """
            CREATE TABLE IF NOT EXISTS user(
            userID SMALLINT UNSIGNED NOT NULL,
            user_name NVARCHAR(100) NOT NULL,
            PRIMARY KEY (userID)
            );
            """
        cur.execute(q)
        connection.commit()

    with connection.cursor() as cur:
        q = """
            CREATE TABLE IF NOT EXISTS author(
            authorID SMALLINT UNSIGNED NOT NULL,
            userID SMALLINT UNSIGNED NOT NULL,
            total_posts INT UNSIGNED, 
            user_upvote_ratio FLOAT(10),
            registration_date DATE, 
            FOREIGN KEY (userID) REFERENCES user(userID) ON DELETE RESTRICT ON UPDATE CASCADE,
            PRIMARY KEY (authorID)
            );
            """
        cur.execute(q)
        connection.commit()

    with connection.cursor() as cur:
        q = """
            CREATE TABLE IF NOT EXISTS subreddit(
            subredditID SMALLINT UNSIGNED NOT NULL,
            subreddit_name NVARCHAR(100) NOT NULL,
            creation_date DATE NOT NULL,
            description NVARCHAR(500),
            subreddit_total_posts INT,
            subreddit_total_subscribers INT,
            PRIMARY KEY (subredditID)
            );
            """
        cur.execute(q)
        connection.commit()

    with connection.cursor() as cur:
        q = """
            CREATE TABLE IF NOT EXISTS subscriber(
            subscriberID SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
            userID SMALLINT UNSIGNED NOT NULL,
            subredditID SMALLINT UNSIGNED NOT NULL,
            PRIMARY KEY (subscriberID),
            FOREIGN KEY (userID) REFERENCES user(userID) ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (subredditID) REFERENCES subreddit(subredditID) ON DELETE RESTRICT ON UPDATE CASCADE
            );
            """
        cur.execute(q)
        connection.commit()

    with connection.cursor() as cur:
        q = """
            CREATE TABLE IF NOT EXISTS post(
            postID SMALLINT UNSIGNED NOT NULL,
            post_name NVARCHAR(400) NOT NULL, 
            posted_date DATE NOT NULL,
            authorID SMALLINT UNSIGNED NOT NULL,
            subredditID SMALLINT UNSIGNED NOT NULL,
            self_text NVARCHAR(1000), 
            total_comments INT,
            
            PRIMARY KEY (postID),
            FOREIGN KEY (authorID) REFERENCES author(authorID) ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (subredditID) REFERENCES subreddit(subredditID) ON DELETE RESTRICT ON UPDATE CASCADE
            );
            """
        cur.execute(q)
        connection.commit()

    with connection.cursor() as cur:
        q = """
            CREATE TABLE IF NOT EXISTS votes(
            voteID SMALLINT UNSIGNED NOT NULL,
            postID SMALLINT UNSIGNED NOT NULL,
            karma INT,
            upvote_ratio FLOAT(10),
            PRIMARY KEY(voteID),
            FOREIGN KEY (postID) REFERENCES post(postID) ON DELETE RESTRICT ON UPDATE CASCADE
            );
            """
        cur.execute(q)
        connection.commit()

    with connection.cursor() as cur:
        q = """
            CREATE TABLE IF NOT EXISTS awards(
            awardID SMALLINT UNSIGNED NOT NULL,
            postID SMALLINT UNSIGNED NOT NULL,
            awards_recieved INT UNSIGNED,
            PRIMARY KEY(awardID),
            FOREIGN KEY (postID) REFERENCES post(postID) ON DELETE RESTRICT ON UPDATE CASCADE
            );
            """
        cur.execute(q)
        connection.commit()

    with connection.cursor() as cur:
        q = """
                INSERT INTO subreddit(subredditID, subreddit_name, creation_date, description, subreddit_total_posts, subreddit_total_subscribers) VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.executemany(q, subredditList)
        connection.commit()

    with connection.cursor() as cur:
            q = """
                    INSERT INTO user(userID, user_name) VALUES (%s, %s)
            """
            cur.executemany(q, userList)
            connection.commit()
            
    with connection.cursor() as cur:
          q = """
                  INSERT INTO subscriber(userID, subredditID) VALUES (%s, %s)
          """
          cur.executemany(q, subscriber_to_subreddit_list)
          connection.commit()
         
  
    with connection.cursor() as cur:
          q = """
                  INSERT INTO author(authorID, userID, total_posts, user_upvote_ratio, registration_date) VALUES (%s, %s, %s, %s, %s)
          """
          cur.executemany(q, authorList)
          connection.commit()
         

    with connection.cursor() as cur:
          q = """
                  INSERT INTO post(postID, post_name, posted_date, authorID, subredditID, self_text, total_comments) VALUES (%s, %s, %s, %s, %s, %s, %s)
          """
          cur.executemany(q, postList)
          connection.commit()
         
    with connection.cursor() as cur:
          q = """
                  INSERT INTO votes(voteID, postID, karma, upvote_ratio) VALUES (%s, %s, %s, %s)
          """
          cur.executemany(q, voteList)
          connection.commit()

    with connection.cursor() as cur:
          q = """
                  INSERT INTO awards(awardID, postID, awards_recieved) VALUES (%s, %s, %s)
          """
          cur.executemany(q, awardList)
          connection.commit()



finally:
      connection.close()



