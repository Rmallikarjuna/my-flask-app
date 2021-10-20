import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import json
# import pandas as pd
import PyPDF2 


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'xlsx'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def readPdf(filename):
    # creating a pdf file object 
    pdfFileObj = open(filename, 'rb') 

    # creating a pdf reader object 
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 

    # printing number of pages in pdf file 
    pages = pdfReader.numPages
    print("number of pages in pdf file", pages)
    text = ""
    for i in range(0,pages):
        pageObj = pdfReader.getPage(i)
        print("page obje.....",pageObj.extractText())
        text += pageObj.extractText() + "\n"
        print(pageObj.extractText())        
    pdfFileObj.close() 
    print("text..... ", text)
    return text

def getDimensions(filename):
    result = {}
    xl = pd.ExcelFile(filename)
    print("xl......", xl)
    sheetnames = xl.sheet_names  # get sheetnames
    for sheet in sheetnames:
        df = xl.parse(sheet)
        dimensions = df.shape
        print('sheetname', ' --> ', sheet)
        print(f'row count on "{sheet}" is {dimensions[0]}')
        print(f'column count on "{sheet}" is {dimensions[1]}')
        result["rows"] = dimensions[0]
        result["columns"] = dimensions[1]
        return result
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# upload file
@app.route("/upload_file", methods=['POST'])
def uploadFile():
    print("request, .. ", request)
    file_data = {}
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        fileSplit = filename.rsplit('.', 1)
        name = fileSplit[0]
        extension = fileSplit[1]
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        size = os.path.getsize("uploads/"+filename)
        fileInfo = {}
        fileInfo["size"] = size
        fileInfo["name"] = name
        fileInfo["extension"] = extension
        if(extension == 'xlsx'):
            pass
            # fileInfo["dimensions"] = getDimensions("uploads/"+filename)
        if(extension == 'pdf'):
            fileInfo["content"] = readPdf("uploads/"+filename)
        file_data[name] = fileInfo
        file_json = json.dumps(fileInfo)
        data = {}
        with open('fileDetails.json') as f:
            data = json.load(f)
        data[name] = fileInfo
        print("file data......", data)
        with open('fileDetails.json', 'w') as json_file:
            json.dump(data, json_file)
        print(data)
        return "file uploaded successfully"

# Get file Info`
@app.route("/get_file_info", methods=['GET'])
def getFileInfo():
    filename = request.args.get('filename')
    with open('fileDetails.json') as f:
        data = json.load(f)    
    return data[filename]

# Get file content

@app.route("/get_file_content", methods=['GET'])
def getFileContent():
    filename = request.args.get('filename')
    with open('fileDetails.json') as f:
        data = json.load(f)    
    return data[filename]["content"]