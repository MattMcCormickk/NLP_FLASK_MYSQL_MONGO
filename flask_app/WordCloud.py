from wordcloud import WordCloud
import matplotlib.pyplot as plt

#wanted to show word cloud after views were created but had a had time getting it to render on the html page
class WordCloud:
	def create_wordcloud(self, training_data, test_data):
		worcloud_words = ''

		for arg in training_data:
			tokens = arg.split()
			worcloud_words += " ".join(tokens)+" "

		for arg in test_data:
			tokens = arg.split()
			worcloud_words += " ".join(tokens)+" "

		#cool word cloud thing
		wordcloud = WordCloud(width = 700, height= 700,
			                background_color ='white', 
		                min_font_size = 10).generate(worcloud_words) 
		# plt.figure(figsize = (5, 5), facecolor = None) 
		plt.imshow(wordcloud) 
		plt.axis("off") 
		plt.tight_layout(pad = 0) 
		return plt
