#!/usr/bin/env python
import os
import sys
import inspect
import nltk
from nltk.tag.hunpos import HunposTagger
db_script_path = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
sys.path.insert(0, db_script_path)
from DB_Scripts import GetReviews
#from get_reviews import GetReview
from textblob import TextBlob
import re


class ProcessingWithBlob:

	def __init__(self, text):
		"""
		THis class is used to process text on the basis of TextBlob library, For documentation refer to 
		http://textblob.readthedocs.org/en/dev/.text can either be a single string or a list of strings 
		depending upon the requirements

		"""
		self.text = text
		self.blob = TextBlob(self.text)

	
	def noun_phrase(self):
		return self.blob.noun_phrases

	def pos_tags(self):
		return self.blob.pos_tags

	def sentiment_polarity(self):
		return self.blob.sentiment.polarity

	def sentences(self):
		return self.blob.sentences

	def word_tokens(self):
		return self.blob.words


	@staticmethod
	def new_blob_polarity(text):
		blob = TextBlob(text)
		return blob.sentiment.polarity

	def polarity(self):
		polarised_sentences = list()
		#These nouns can be modified using nltk or pattern librabry or stanford pos tagging engine
		nouns = self.noun_phrases()
		for sentence in self.sentences():
			for noun in nouns:
				if bool(re.findall(noun, str(sentence))):
					result = (str(sentence), noun, new_blob_polarity())
					polarised_sentences.append(result)
		return polarised_sentences





class PosTags:
	def __init__(self, text):
		"""
		hunpos tagger only takes tokenize word for tagging
		Args:
			text: sentence
		"""
		self.text = text
		self.hunpos = ht = HunposTagger(path_to_model='/usr/local/bin/en_wsj.model', path_to_bin= '/usr/local/bin/trunk/tagger.native')
		self.blob = TextBlob(self.text)


	def hunpos_tagger(self):
		return 	self.hunpos.tag(nltk.word_tokenize(self.text))

	def blob_tagger(self):
		return self.blob.pos_tags


	def nltk_tagger(self):
		return	nltk.pos_tag(nltk.word_tokenize(self.text))



class CustomParsing:

	def __init__(self, sentences):
		"""
		sentences will be the list of tuples where first element is the sentence and the other element will the the pos
		tag of the same sentence, The other element can be pos tags with the hunpos_tags, nltk tags or TextBlob tags

		"""

		self.sentence = sentences
		self.grammer = r"""Noun_Phrases:{<JJ.*>?<NN>*<NN>}"""
		self.chunk_parser = nltk.RegexpParser(grammer)
