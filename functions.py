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

# Cosine Similarity
def cos_sim(a, b):
  return np.inner(a,b)/(lg.norm(a)*lg.norm(b))

 # Use API Calls to Get Information of a User Selected Book
def selected_book(recommendation):
  try:
    result = meta(recommendation)
    print('\nYou Selected:\n')
    print(result)
  except:
    print('\nYou Selected:\n')
    print(df.title[df.isbn13 == int(recommendation)].iloc[0])

  result_desc = desc(recommendation)

  print('\nDescription:\n')
  print(result_desc)
  print('\nRating:\n')
  print(df.average_rating[df.isbn13 == int(recommendation)].iloc[0])


  # Allow Users to Get Information for Different Books Until they are Done
def recursively_ask_for_book():
  print('\nYou may type another ISBN to learn more about a different book. If you don\'t need anymore information type \"Done\".\n')
  response = input()
  if response.lower() != 'done':
    recommendation = response
    selected_book(recommendation)
    recursively_ask_for_book()

# Recommendation Function
def get_me_a_book(inp):
  test = str(inp)
  if test.lower() == 'no':
    print('\nWe apoligize, but it appears your book is not in our store. Please try again if you wish to continue.\n')
    reco_system()
    return
  try:
    given = meta(test)
    print('\nYour Book:\n')
    print(given)
  except:
    print('\nYour Book:\n')
    print(df.title[df.isbn13 == int(inp)].iloc[0])
  given_desc = desc(test)

  print('\nDescription:\n')
  print(given_desc)
  print('\nRating:\n')
  print(df.average_rating[df.isbn13 == int(inp)].iloc[0])
  print('')

  print('Here are some books you might like. Enter the ISBN number to find out more about a specific book.\n')
  theta = df3[test].sort_values(ascending = False)
  for i in range(10):
    print('ISBN: {} ----- Rating: {:.2f} ----- Title: {}'.format(theta.index[i],
                                                             df.average_rating[df.isbn13 == theta.index[i]].iloc[0],
                                                             df.title[df.isbn13 == theta.index[i]].iloc[0]))
  print('')
  recommendation = input()
  selected_book(recommendation)
  recursively_ask_for_book()



# Function to take book title and get the isbn
def clean_user_input():

  new_title = pd.DataFrame([inp])
  title_example = [model.infer_vector((new_title.iloc[0][0].split(' ')))]
  gensim_example = np.array(title_example).tolist()

  closest = np.zeros((len(df['ta2vec']), 2))
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
    dictionary = {'isbn': df['isbn13'].iloc[the_indices[i]],
                    'title': df['title'].iloc[the_indices[i]].encode('utf-8'),
                    'author': df['authors'].iloc[the_indices[i]].encode('utf-8')}
    titles.append(dictionary)
  return titles


# Calling all of the functions for the interactive recommender system
def reco_system():
  titles = clean_user_input()
  print('\nThe following are some books with similar titles as your input. Please type the ISBN number of the book you wish to search.\n')
  for i in range(len(titles)):
    print('ISBN: {} ----- Rating: {:.2f} ----- Title: {}'.format(titles[i, 1].astype(str),
                                                             df.average_rating[df.isbn13 == titles[i, 1].astype(int)].iloc[0],
                                                             titles[i, 0].decode('utf-8')))
  print('\nIf you do not see your book, please type \"No\".\n')
  alpha = input()
  get_me_a_book(alpha)

def satisfaction():
  print('\nAre you satisfied with the recommendations? (Yes/No)\n')
  gamma = input()
  if gamma.lower() == 'no':
    print('\nI apologize for the poor recommendations. Please enter another book if you wish to try again.\n')
    reco_system()
    print('\nAre you satisfied with the recommendations? (Yes/No)\n')
    theta = input()
    if theta.lower() == 'no':
      print('\nI apologize for not being able to find you a good recommendation. I hope you have a nice day!')
    else:
      print('\nThank You! I hope you enjoy the new book!')
  else:
    print('\nThank You! I hope you enjoy the new book!')
