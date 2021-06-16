import string
import re
from stop_words import get_stop_words
from nltk.stem import WordNetLemmatizer, PorterStemmer, SnowballStemmer

class cleanInput:
	def superclean(self, s):
		printable = set(string.printable)
		out = ''
		for char in s:
		    if char in printable:
		        out += char
		return out

	def preprocess(self, s):
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