QUERIES = {
	'mysql': {
		'file_name': 'init.sql',
		'content': """
			CREATE TABLE IF NOT EXISTS systems (
				id INT AUTO_INCREMENT PRIMARY KEY,
				name VARCHAR(255)
			);
		"""
	},
	'postgresql': {
		'file_name': 'init.sql',
		'content': """
			CREATE TABLE IF NOT EXISTS systems (
				id INT AUTO_INCREMENT PRIMARY KEY,
				name VARCHAR(255)
			);
		"""
	},
	'mongodb': {
		'file_name': 'init-mongo.js',
		'content': """
			db = db.getSiblingDB('admin');
			db.auth('root', 'root');
			db = db.getSiblingDB('app_db');
			
			db.createCollection('systems');
			db.systems.insertOne({ name: 'example_system' });
		"""
	},
	'elasticsearch': {
		'file_name': 'init-es.sh',
		'content': """
			#!/bin/bash
			sleep 20 # Wait for Elasticsearch to start
			curl -X PUT "localhost:9200/systems?pretty" -H 'Content-Type: application/json' -d '
			{
				"mappings": {
				"properties": {
					"name": { "type": "text" }
				}
				}
			}
			'
		"""
	}

}