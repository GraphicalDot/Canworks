#!/usr/bin/env python
#-*- coding: utf-8 -*-

import nltk
import numpy
import random
import sys
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from CustomSentenceTokenizer import SentenceTokenizer 
from  trained_punkt_sentences_tokenizer import 	SentenceTokenization
directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(directory + "/trainers")


class ForTestingClassifier:
	def __init__(self, text, tokenizer=None):
		self.text = text
		self.tokenizer = tokenizer
		if not self.tokenizer:
			self.sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
		
			self.ambience_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "ambience"), "rb").read(), realign_boundaries=True)
			self.services_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "service"), "rb").read(), realign_boundaries=True)
			self.costing_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "cost"), "rb").read(), realign_boundaries=True)
			self.food_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "food"), "rb").read(), realign_boundaries=True)
			self.null_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "null"), "rb").read(), realign_boundaries=True)
			self.overall_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "overall"), "rb").read(), realign_boundaries=True)
		if self.tokenizer == "text-sentence":
			self.sent_tokenizer = SentenceTokenization()
			self.ambience_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "ambience"), "rb").read())
			self.services_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "service"), "rb").read())
			self.costing_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "cost"), "rb").read())
			self.food_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "food"), "rb").read())
			self.null_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "null"), "rb").read())
			self.overall_data = self.sent_tokenizer.tokenize(open("{0}/valid_{1}.txt".format(path, "overall"), "rb").read())
		
		#self.ambience_documents = [(nltk.wordpunct_tokenize(sent), "ambience") for sent in self.ambience_data if sent != ""]
		self.ambience_documents = [(sent, "ambience") for sent in self.ambience_data if sent != ""]
		self.services_documents = [(sent, "service") for sent in self.services_data if sent != ""]
		self.costing_documents = [(sent, "cost") for sent in self.costing_data if sent != ""]
		self.food_documents = [(sent, "food") for sent in self.food_data if sent != ""]
		self.null_documents = [(sent, "null") for sent in self.null_data if sent != ""]
		self.overall_documents = [(sent, "overall") for sent in self.overall_data if sent != ""]
		self.whole_set = self.ambience_documents + self.services_documents + self.costing_documents + self.food_documents + self.null_documents + self.overall_documents
		random.shuffle(self.whole_set)

	def document_features(document):
		document_words = set(document) [3]
		features = {}
		for word in word_features:
			features['contains(%s)' % word] = (word in document_words)
		return features

	def naive_bayes_classifier(self):
		pass

	def multinomial_nb_classifier(self):
		"""
		This method returns a claqssfier trained with multinomial naive bayes using cost, services and ambience as three categories

		"""
		count_vect = CountVectorizer()
		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])

		#dictionary of features and transform documents to feature vectors:
		data_counts = count_vect.fit_transform(data)

		#Occurrence count is a good start but there is an issue: longer documents will have higher average count values than shorter documents, 
		#even though they might talk about the same topics.
		#To avoid these potential discrepancies it suffices to divide the number of occurrences of each word in a document by the total number 
		#of words in the document: these new features are called tf for Term Frequencies.
		#Another refinement on top of tf is to downscale weights for words that occur in many documents in the corpus and are therefore less 
		#informative than those that occur only in a smaller portion of the corpus.
		
		tfidf_transformer = TfidfTransformer()
		data_tfidf = tfidf_transformer.fit_transform(data_counts)

		classifier = MultinomialNB().fit(data_tfidf, target)
		return classifier

	
	def performance_with_multinb(self):
		"""
		This measures the performance with multinomial naive bayes
		"""
		
		count_vect = CountVectorizer()
		data_train = numpy.array([element[0] for element in self.whole_set[0: 4300]])
		data_test = numpy.array([element[0] for element in self.whole_set[4301: ]])
		
		target_train = numpy.array([element[1] for element in self.whole_set[0: 4300]])
		target_test = numpy.array([element[1] for element in self.whole_set[4301: ]])

		data_counts = count_vect.fit_transform(data_train)
		tfidf_transformer = TfidfTransformer()
		data_tfidf = tfidf_transformer.fit_transform(data_counts)

		classifier = MultinomialNB().fit(data_tfidf, target_train)

		data_test_counts = count_vect.transform(data_test)
		data_test_tfidf = tfidf_transformer.transform(data_test_counts)
		predicted = classifier.predict(data_test_tfidf)

		return numpy.mean(predicted == target_test)



	def with_multinb(self):
		"""
		This with the help of self.multinomial_nb classify the self.text and returns an numpy array with predicted tags
		"""
		count_vect = CountVectorizer()
		new_data = self.sent_tokenizer.tokenize(self.text)
		print new_data
		X_new_counts = count_vect.transform(numpy.array(new_data))
		X_new_tfidf = tfidf_transformer.transform(X_new_counts)
		
		classifier = self.multinomial_nb_classifier()

		predicted = classifier.predict(X_new_tfidf)

		return zip(new_data, predicted)



	def svm_classifier(self):
		classifier = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), 
			('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5)),])

		data = numpy.array([element[0] for element in self.whole_set])
		target = numpy.array([element[1] for element in self.whole_set])
		
		classifier.fit(data, target)
		return classifier

	def with_svm(self):

		classifier = self.svm_classifier()
		#new_data = self.sent_tokenizer.tokenize(self.text, realign_boundaries= True)
		
		##With the new class created in CustomSentenceTokenizer , the new sentence tokenizer
		#tokenizer = SentenceTokenizer()
		#new_data = [" ".join(word_tokenized_sentence) for word_tokenized_sentence in tokenizer.segment_text(self.text)]

		#With the new class made from text-sentence library
	
		tokenizer = SentenceTokenization()
		new_data = tokenizer.tokenize(self.text)
		print new_data		
		predicted = classifier.predict(new_data)

		return zip(new_data, predicted)

