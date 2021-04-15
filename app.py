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
import tensorflow_hub as hub

from functions import *

###    Loading model and data
# Defining embedder
module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
model = hub.load(module_url)

def embed(input):
  return model(input)

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

useless_list = embed(df['Title and Author'])
usefull_list = useless_list.numpy()

m, n = usefull_list.shape
complete_list = []

for i in range(m):
  temp = []
  for j in range(n):
    temp.append(usefull_list[i, j])
  complete_list.append(temp)

empty_df = df.card2vec
for i in range(len(empty_df)):
  empty_df.iloc[i] = complete_list[i]








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
		##
		##
		example = [inp]
		embedded_example = embed(example)
		usefull_example = embedded_example.numpy()
		closest = np.zeros((len(usefull_list), 2))
		for i in range(len(usefull_list)):
		  closest[i, 0] = i
		  closest[i, 1] = cos_sim(usefull_example[0], empty_df.iloc[i])


# doing this because the dataframe was sorted
# This was done to maintain the original order


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
			'title': df['title'].iloc[the_indices[i]],
			'author': df['authors'].iloc[the_indices[i]]
			}
			titles.append(dictionary)
		return render_template('answer.html', titles = titles )
	return render_template('answer.html', titles = titles )



@app.route('/recommendation', methods = ['POST', 'GET'])
def recommendation():
	if request.method == "POST":
		inp = request.form.get('selected_book')
		recommendation_title = df.title[df.isbn13 == int(inp)].iloc[0]
		recommendation_author = df.authors[df.isbn13 == int(inp)].iloc[0]
		recommendation_description = df.clean_text[df.isbn13 == int(inp)].iloc[0]
		useless_cover = cover(inp)
		recommendation_cover = useless_cover.get('thumbnail')# this is a link
# Recommendation Function
		theta = df3[inp].sort_values(ascending = False)

		useless_recommendation = []
		for i in range(6):
			johann = theta.index[i]
			temp_cover = cover(str(johann))
			temp = df.clean_text[df.isbn13 == johann].iloc[0]
			thresh = 150
			if len(temp) > thresh:
				temp = temp[:thresh] + '...'

			temp2 = df.title[df.isbn13 == johann].iloc[0]
			thresh2 = 66
			if len(temp2) >= thresh2:
				temp2 = temp2[:thresh2] + '...'
			recommendation = {
			'isbn': johann,
			'title': temp2,
			'author': df.authors[df.isbn13 == johann].iloc[0],
			'description': temp,
			'cover': temp_cover.get('thumbnail')
			}
			useless_recommendation.append(recommendation)

		return render_template('recommendation.html',
			recommendation_title= recommendation_title,
			recommendation_cover = recommendation_cover,
			recommendation_author = recommendation_author,
			recommendation_description = recommendation_description,
			book = inp,
			useless_recommendation = useless_recommendation
		)

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

	message = "Thanks for messaging Ron and Johann's bookstore. Thank you!"
	server = smtplib.SMTP("smtp.gmail.com" , 587)
	server.starttls()
	server.login(my_email, my_password)
	server.sendmail(my_email, EMAIL, message)

	if not firstNAME or not lastNAME or not EMAIL:
		error_statement = "All form fields required please. Dont be SNEAKY"
		return render_template("fail.html", error_statement = error_statement,  first_name = firstNAME, last_name = lastNAME, email = EMAIL, subscribers = subscribers)

	subscribers.append(f" {firstNAME} {lastNAME} | {EMAIL}")
	title = "Thank you!"
	return render_template('form.html', title = title, first_name = firstNAME, last_name = lastNAME, email = EMAIL, subscribers = subscribers)
