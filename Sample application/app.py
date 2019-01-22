from flask import Flask, render_template,request,redirect,url_for # For flask implementation
from pymongo import MongoClient # Database connector
import mongodbutil as ml


def start_database():
	client=ml.mongoclient('localhost')
	ml.csv2mongo(client,'TSDB','TYX','TVX.csv')
	df=ml.mongo2df(client,'TSDB','TYX')
	print(df)
	return client

@app.route('/')
def mainapge():
	df=ml.mongo2df(client,'TSDB','TYX')
	return render_template('mainpage.html')



app = Flask(__name__)

if __name__ == "__main__":
	client=start_database()
    app.run(host='127.0.0.1', debug=True)
	# Careful with the debug mode..