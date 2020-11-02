
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 17:06:13 2020
@author: m.zhukov
"""

import os
import urllib.request
from zipfile import ZipFile
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
from flask import send_file
import pymongo
from pymongo import MongoClient
import sys
import configparser
import datetime
import time
import os.path
from urllib.parse import quote_plus
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','docx'])

def get_timestamp():
    return datetime.datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

def getNextSequence(collection,name):  
    return collection.find_and_modify(query= { "_id": name },update= { '$inc': {'seq': 1}}, new=True ).get('seq');

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
app = Flask(__name__)
UPLOAD_FOLDER = 'C:/Users/m.zhukov/Desktop/project/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/multiple-files-upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
    files = request.files.getlist('files[]') 
    errors = {}
    success = False  
    if 'files[]' not in request.files:
    	resp = jsonify({'message' : 'No file part in the request'})
    	resp.status_code = 400
    	return resp	
  	  
    if len(files)>10:
        errors["The number of incoming files"] = 'out of range'
    else:
        #connecting to Mongodb
        config = configparser.RawConfigParser()
        config.read('./config.txt')
        details = dict(config.items('mongodb'))
        username=details['user']
        password=details['password']
        host=details['host']
        port=details['port']
        host=host+":"+port
        uri = "mongodb://%s:%s@%s"%(quote_plus(username), quote_plus(password),host)
        client = MongoClient(uri) 
        mydb = client["Files_task"]
        collist = mydb.list_collection_names()
        mycol= mydb["first"] 
        counter=mydb["counters"]
        if counter.count() == 0:
            counter.insert({'_id': "result_id", 'seq': 0})                  
        with ZipFile('output.zip', 'w') as zipObj:
            for file in files:	
                if file and allowed_file(file.filename):
                    num=getNextSequence(counter,"result_id").__str__()
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    os.chdir(app.config['UPLOAD_FOLDER'])
                    zipObj.write(filename)
                    entry={'DATETIME': get_timestamp(),'RESULT_ID':num,'File_name':filename,'Creation_time':time.ctime(os.path.getctime(filename)),'ZIPname':'output.zip'}
                    mycol.insert(entry)
                    success = True   
                else:
                    errors[file.filename] = 'File type is not allowed'                 			
    if success and errors:
    	errors['message'] = 'File(s) successfully uploaded'
    	resp = jsonify(errors)
    	resp.status_code = 500
    	return resp
    if success:
        resp = jsonify({'Link for zip download' : 'http://localhost:5000/download'})
        resp.status_code = 201       
        return resp
        #return send_file('output.zip', as_attachment=True)
    else:
    	resp = jsonify(errors)
    	resp.status_code = 500
    	return resp
    
@app.route('/download')
def downloadFile ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "output.zip"
    return send_file(path, as_attachment=True)
if __name__ == "__main__":
    app.run()
