###
### MUST USE FOR APP
###
from flask import Flask, render_template, request, redirect

###
### Extra shit
###
import pandas as pd
import numpy as np
from numpy import linalg as lg
import os
import re
import json
import string
from pathlib import Path
import smtplib

from isbnlib import *
import texthero as hero
from texthero import preprocessing
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

from functions import *

###    Loading model and data

# Final DataFrame (For EDA & Topic Modeling, Refer to Personal Notebook)
df = pd.read_csv('Our_Dataset.csv')
df = df.drop(['Unnamed: 0', 'index'], axis = 1)

# JSON loading in order to avoid loading vectors as strings
for i in range(len(df.ta2vec)):
	temp = df.ta2vec.iloc[i]
	df.ta2vec.iloc[i] = json.loads(temp)

# DataFrame of the Cosine Similarities Between Book Descriptions
df3 = pd.read_csv('Our_Cosines.csv')
df3 = df3.drop('isbn13', axis = 1)
df3.index = df.isbn13

# model = Doc2Vec.load('my_doc2vec_model.bin')

# Creating a custom pipeline for text cleaning
custom_pipeline = [preprocessing.fillna,
                   preprocessing.remove_whitespace,
                   preprocessing.remove_diacritics
                  ]
# TextHERO! Pre-Processing
ta = hero.clean(df['Title and Author'], custom_pipeline)

ta = [n.replace('{','') for n in ta]
ta = [n.replace('}','') for n in ta]
ta = [n.replace('(','') for n in ta]
ta = [n.replace(')','') for n in ta]

ta_docs = [TaggedDocument(doc.split(' '), [i])
            for i, doc in enumerate(ta)]

# Building a model to get the embeddings of book titles
model = Doc2Vec(vector_size = 64, window = 2, min_count = 1, workers = 8, epochs = 40)
model.build_vocab(ta_docs)

model.train(ta_docs,
           total_examples=model.corpus_count,
           epochs=model.epochs)


ta2vec = [model.infer_vector((df['Title and Author'][i].split(' ')))
           for i in range(0, len(df['Title and Author']))]

gensim_ta = np.array(ta2vec).tolist()
df['ta2vec'] = gensim_ta



###
###
###



app = Flask(__name__)

# Adding variables that I will need
subscribers = []

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/answer', methods = ['POST', 'GET'])
def answer():
	if request.method == "POST":
		###
		inp = request.form.get('initial_book')
		test = inp
		##
		##

		new_title = pd.DataFrame([inp])

		title_example = [model.infer_vector((new_title.iloc[0][0].split(' ')))]
		gensim_example = np.array(title_example).tolist()

		closest = np.zeros((len(df['ta2vec']), 2))

# doing this because the dataframe was sorted
# This was done to maintain the original order
		for i in range(len(df['ta2vec'])):
			closest[i, 0] = i
			closest[i, 1] = cos_sim(gensim_example[0], df['ta2vec'].iloc[i])

		df_closest = pd.DataFrame(closest)
		df_closest.columns = ['index', 'cos_sim']
		df_closest['index'] = df_closest['index'].astype(int)

		temp = df_closest['cos_sim'].sort_values(ascending = False)
		most_similar = temp[:10]
		the_indices = most_similar.index

		titles = []
		for i in range(len(the_indices)):
			dictionary = {
			'isbn': df['isbn13'].iloc[the_indices[i]],
			'title': df['title'].iloc[the_indices[i]].encode('utf-8'),
			'author': df['authors'].iloc[the_indices[i]].encode('utf-8')
			}
			titles.append(dictionary)
		return render_template('answer.html', titles = titles, test = test )
	return render_template('answer.html', titles = titles )



@app.route('/recommendation', methods = ['POST', 'GET'])
def recommendation():
	if request.method == "POST":
		inp = request.form.get('selected_book')

		return render_template('recommendation.html')

# inp is the isbn13 number.... we should be able to use that to retrieve
# title
# author
# description
# get the image of the bookstore

# then we need to make a list with 6 index of the recommendations

	return render_template('recommendation.html')


@app.route('/about')
def about(): # {{ url_for('about')}}
	names = ["Johann", "Ron", "Valery","Loay", "Zarak", "Ava", "Daniel", "Zeb", "Jay", "Jonatas", "Amir"]
	return render_template('about.html', names = names)


@app.route('/contact')
def contact(): # {{ url_for('index')}}
	return render_template('contact.html')

@app.route('/form', methods =['POST'])
def form(): # {{ url_for('index')}}
	firstNAME = request.form.get("first_name")
	lastNAME = request.form.get('last_name')
	EMAIL =  request.form.get('email')

	# SETTING UP EMAIL STUFF
	my_email = 'johannpiedras.email@gmail.com'
	my_password = 'testingEMAIL1995'

	message = "You have been contacted Online Science Tutor bu Johann Piedras. Thank you!"
	server = smtplib.SMTP("smtp.gmail.com" , 587)
	server.starttls()
	server.login(my_email, my_password)
	server.sendmail(my_email, EMAIL, message)
	# my_email has my email
	# EMAIL is what was given by the user

	if not firstNAME or not lastNAME or not EMAIL:
		error_statement = "All form fields required please. Dont be SNEAKY"
		return render_template("fail.html", error_statement = error_statement,  first_name = firstNAME, last_name = lastNAME, email = EMAIL, subscribers = subscribers)

	subscribers.append(f" {firstNAME} {lastNAME} | {EMAIL}")
	title = "Thank you!"
	return render_template('form.html', title = title, first_name = firstNAME, last_name = lastNAME, email = EMAIL, subscribers = subscribers)
