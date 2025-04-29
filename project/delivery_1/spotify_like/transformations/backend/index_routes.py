import textwrap

INDEX_ROUTES = {
	'mysql': {
		'requirements': ["mysql-connector-python"],
		'code': lambda target : textwrap.dedent(f"""
import mysql.connector

@app.route('/')
def hello():
	try:
		conn = get_db_connection()
		cursor = conn.cursor()
		cursor.execute("SELECT 1")
		cursor.close()
		conn.close()
		return jsonify({{"message": "Hello World from Backend", "database_connection": "success", "type": "MySQL"}})
	except Exception as e:
		return jsonify({{"message": "Hello World from Backend", "database_connection": "failed", "error": str(e)}})""")
	},
	'mongodb': {
		'requirements': ["pymongo"],
		'code': lambda target : textwrap.dedent(f"""
from pymongo import MongoClient

def get_db_connection():
	client = MongoClient('mongodb://{target}:27017/',
		username='root',
		password='root',
		authSource='admin')
	return client.app_db

@app.route('/')
def hello():
	try:
		db = get_db_connection()
		# Simple test query
		result = db.systems.find_one()
		return jsonify({{"message": "Hello World from Backend", "database_connection": "success", "type": "MongoDB", "data": result.get('name', 'No data')}})
	except Exception as e:
		return jsonify({{"message": "Hello World from Backend", "database_connection": "failed", "error": str(e)}})"""),
	},
	'postgresql': {
		'requirements': ["psycopg2-binary"],
		'code': lambda target : textwrap.dedent(f"""
import psycopg2

def get_db_connection():
	return psycopg2.connect(
		host='{target}',
		database='{target}',
		user='postgres',
		password='root'
	)

@app.route('/')
def hello():
	try:
		conn = get_db_connection()
		cursor = conn.cursor()
		cursor.execute("SELECT 1")
		cursor.close()
		conn.close()
		return jsonify({{"message": "Hello World from Backend", "database_connection": "success", "type": "PostgreSQL"}})
	except Exception as e:
		return jsonify({{"message": "Hello World from Backend", "database_connection": "failed", "error": str(e)}})""")
	},
	'elasticsearch': {
		'requirements': ["elasticsearch"],
		'code': lambda target : textwrap.dedent(f"""
from elasticsearch import Elasticsearch

def get_db_connection():
	return Elasticsearch([{{'host': '{target}', 'port': 9200}}])

@app.route('/')
def hello():
	try:
		es = get_db_connection()
		return jsonify({{"message": "Hello World from Backend", "database_connection": "success", "type": "Elasticsearch"}})
	except Exception as e:
		return jsonify({{"message": "Hello World from Backend", "database_connection": "failed", "error": str(e)}})""")
	},
}