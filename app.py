###
### MUST USE FOR APP
###
from flask import Flask, render_template, request, redirect


###
### Extra shit
###
import os
import re
import json
import string
from pathlib import Path
import smtplib



app = Flask(__name__)

# Adding variables that I will need
subscribers = []

@app.route('/')
def index(): # {{ url_for('index')}}
	return render_template('index.html')

@app.route('/answer', methods = ['POST', 'GET'])
def answer():
    return render_template('answer.html')

@app.route('/recommendation', methods = ['POST', 'GET'])
def recommendation():
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
