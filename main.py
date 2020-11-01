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
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
app = Flask(__name__)
UPLOAD_FOLDER = 'C:/Users/m.zhukov/Desktop/project/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/multiple-files-upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'files[]' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	
	files = request.files.getlist('files[]')
	errors = {}
	success = False
	with ZipFile('output.zip', 'w') as zipObj:
         for file in files:	
             if file and allowed_file(file.filename):
                 filename = secure_filename(file.filename)
                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                 os.chdir(app.config['UPLOAD_FOLDER'])
                 zipObj.write(filename)
                 success = True   
             else:
                 errors[file.filename] = 'File type is not allowed'                 		
	
	if success and errors:
		errors['message'] = 'File(s) successfully uploaded'
		resp = jsonify(errors)
		resp.status_code = 500
		return resp
	if success:
		resp = jsonify({'message' : 'Files successfully uploaded'})
		resp.status_code = 201
		return resp
	else:
		resp = jsonify(errors)
		resp.status_code = 500
		return resp

if __name__ == "__main__":
    app.run()