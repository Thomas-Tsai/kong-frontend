#!/bin/python 
# -*- coding: utf-8 -*- 
import requests
import json
import markdown
from flask import Flask
from flask import render_template
from flask import request
from flask import Flask, g
from flask import Flask, redirect, url_for
from wtforms import Form, BooleanField, StringField, TextAreaField, HiddenField, SelectField, validators
import os.path
import sys
import configparser
import apidb

app = Flask(__name__)
APIList = []

def get_db():
    idb = apidb.apidb(config_file)
    return idb

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class apiForm(Form):
    apiid = HiddenField('apiid')
    version = StringField('Version', [validators.Length(min=1, max=64)])
    name = StringField('name', [validators.Length(min=1, max=64)])
    shortname = StringField('short name', [validators.Length(min=1, max=64)])
    method = SelectField(u'method', choices=[('',''),('GET', 'GET'), ('POST', 'POST'),('DELETE', 'DELETE'), ('PATCH', 'PATCH'), ('PUT','PUT')])
    uri = StringField('uri', [validators.Length(min=1, max=64)])
    host = StringField('host', [validators.Length(min=1, max=64)])
    group = StringField('Group', [validators.Length(min=1, max=64)])
    description = TextAreaField('Description', [validators.optional(), validators.length(max=8192)])
    params = TextAreaField('Params', [validators.optional(), validators.length(max=2048)])
    example = TextAreaField('Example', [validators.optional(), validators.length(max=8192)])
    success = TextAreaField('Success', [validators.optional(), validators.length(max=8192)])
    error = TextAreaField('Error', [validators.optional(), validators.length(max=8192)])

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def runApi(url, method='get', data=''):
    print('method: ', method)
    if method == 'get':
        myResponse = requests.get(url, verify=True)
    elif method == 'post':
        myResponse = requests.post(url, data, verify=True) 
    elif method == 'patch':
        print("xx",url)
        print("xxdata",data)
        myResponse = requests.patch(url, data, verify=True) 
    elif method == 'delete':
        myResponse = requests.delete(url, verify=True) 
    print (myResponse.status_code)
    
    # For successful API call, response code will be 200 (OK)
    print("response ", myResponse.text)
    jData = {}
    if(myResponse.ok):

        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
        try:
            jData = json.loads(myResponse.text)
        except:
            jData = {}
        #print("The response contains {0} properties".format(len(jData)))
        #print("\n")
        #for key in jData:
        #    print(key , " : " , jData[key])
        jData['status'] = myResponse.ok
    else:
      # If response code is not ok (200), print the resulting http error code with description
        myResponse.raise_for_status()
        jData['status'] = myResponse.raise_for_status()

    return jData

@app.route('/')
@app.route("/index")
@app.route("/login")
def index():
    listurl = kongurl + "/apis"
    kongData = runApi(listurl)
    APIList = []
    apiData = kongData['data']
    for api in apiData:
        apiID = api['id']
        apiName = api['name']
        db = get_db()
        db.row_factory = dict_factory
        apiShortName=''
        apiDesc=''
        apiGroup=''
        apirows = db.get_apis(apiID)
        for row in apirows:
            apiShortName = row['shortname']
            apiDesc = row['description']
            apiGroup = row['apigroup']
        
        apiListData = {'name':apiName, 'kongid':apiID, 'shortname':apiShortName, 'apidesc':apiDesc, 'apigroup':apiGroup, 'apiid':apiID}
        APIList.append(apiListData)
    return render_template('index.html', api_list = APIList)

@app.route("/kong")
def kong():

    apidata = runApi(kongurl+'/')
    kongstr = json.dumps(apidata, indent=4)
    return render_template('kong.html', kong = kongstr)

@app.route("/updateAPI")
def updateAPI():
    form = apiForm(request.form)
    if request.method == 'GET':
        apiId = request.args.get('apiid')
        apidata = runApi(kongurl+'/apis/'+apiId)
        if 'methods' not in apidata: apidata['methods'] = ['GET']
        if 'uris' not in apidata: apidata['uris'] = ['']
        db = get_db()
        db.row_factory = dict_factory
        rows = db.get_api(apiId)
        apidata['shortname'] = ''
        apidata['version'] = ''
        apidata['desc'] = ''
        apidata['params'] = ''
        apidata['apigroup'] = ''
        apidata['example'] = ''
        apidata['success'] = ''
        apidata['error'] = ''
        for row in rows:
            apidata['shortname'] = row['shortname']
            apidata['version'] = row['version']
            apidata['desc'] = row['description']
            apidata['params'] = row['params']
            apidata['apigroup'] = row['apigroup']
            apidata['example'] = row['example']
            apidata['success'] = row['success']
            apidata['error'] = row['error']
        form.apiid.data = apiId
        form.version.data = ''
        form.name.data = apidata['name']
        form.shortname.data = apidata['shortname']
        form.method.data = apidata['methods'][0]
        form.uri.data = apidata['uris'][0]
        form.host.data = apidata['hosts'][0]
        form.group.data = apidata['apigroup']
        form.description.data = apidata['desc']
        form.version.data = apidata['version']
        form.params.data = apidata['params']
        form.example.data = apidata['example']
        form.success.data = apidata['success']
        form.error.data = apidata['error']
    return render_template('updateAPI.html', form=form)

@app.route("/saveAPI", methods=['POST'])
def saveAPI():
    form = apiForm(request.form)
    if request.method == 'POST' and form.validate():
        apiid = form.apiid.data
        updateApiUrl = kongurl+"/apis/"+apiid
        upstreamUrl = form.host.data+""+form.uri.data
        upstreamUrl = upstreamUrl.replace('//', '/')
        upstreamUrl = "http://"+upstreamUrl
        updateApiData = {'name':form.name.data, 'hosts':form.host.data, 'upstream_url':upstreamUrl, 'uris':form.uri.data, 'methods':form.method.data.upper()}
        api = runApi(updateApiUrl, 'patch', updateApiData)
        apidata={}
        apidata['shortName'] = form.shortname.data
        apidata['Desc'] = form.description.data
        apidata['Version'] = form.version.data
        apidata['Group'] = form.group.data
        apidata['Params'] = form.params.data
        apidata['Example'] = form.example.data
        apidata['Success'] = form.success.data
        apidata['Error'] = form.error.data
        apidata['apiid'] = apiid
        db = get_db()
        db.update_api(apidata)
        return redirect(url_for('index'))
    return render_template('updateAPI.html', form=form)
    
@app.route("/deleteAPI")
def deleteAPI():
    if request.method == 'GET':
        apiId = request.args.get('apiid')
        apidata = runApi(kongurl+'/apis/'+apiId, 'delete')
        db = get_db()
        db.delete_api(apiId)
    return redirect(url_for('index'))

@app.route("/api")
@app.route("/displayAPI")
def displayAPI():
    if request.method == 'GET':
        apiId = request.args.get('apiid', '000')
        apidata = runApi(kongurl+'/apis/'+apiId)
        if 'methods' not in apidata: apidata['methods'] = ['GET']
        if 'uris' not in apidata: apidata['uris'] = ['']
        db = get_db()
        db.row_factory = dict_factory
        rows = db.get_api(apiId)
        apidata['shortname'] = ''
        apidata['desc'] =  ''
        apidata['params'] =  ''
        apidata['version'] = ''
        apidata['apigroup'] = ''
        apidata['example'] =  ''
        apidata['success'] = ''
        apidata['error'] = ''
        for row in rows:
            apidata['shortname'] = row['shortname']
            apidata['desc'] = row['description']
            apidata['params'] = markdown.markdown(row['params'])
            apidata['version'] = row['version']
            apidata['apigroup'] = row['apigroup']
            apidata['example'] = row['example']
            apidata['success'] = row['success']
            apidata['error'] = row['error']

        return render_template(
            'displayAPI.html', api = apidata, kongapiurl=kongapiurl
            )
    return redirect(url_for('index'))

@app.route('/addAPI', methods=['GET', 'POST'])
def addAPI():
    form = apiForm(request.form)
    if request.method == 'POST' and form.validate():
        addApiUrl = kongurl+"/apis"
        upstreamUrl = form.host.data+""+form.uri.data
        upstreamUrl = upstreamUrl.replace('//', '/')
        upstreamUrl = "http://"+upstreamUrl
        addApiData = {'name':form.name.data, 'hosts':form.host.data, 'upstream_url':upstreamUrl, 'uris':form.uri.data, 'methods':form.method.data.upper()}
        api = runApi(addApiUrl, 'post', addApiData)
        apiID = api['id']
        apidata={}
        apidata['shortName'] = form.shortname.data
        apidata['Desc'] = form.description.data
        apidata['Group'] = form.group.data
        apidata['Params'] = form.params.data
        apidata['Version'] = form.version.data
        apidata['Example'] = form.example.data
        apidata['Success'] = form.success.data
        apidata['Error'] = form.error.data
        apidata['apiid'] = apiID
        db = get_db()
        db.add_api(apidata)
        return redirect(url_for('index'))
    
    return render_template('addAPI.html', form=form)

if __name__ == '__main__':

    if len(sys.argv) == 2:
        config_file = sys.argv[1]
    else:
        my_path = os.path.abspath(sys.argv[0])
        my_dir = os.path.dirname(my_path)
        config_file = my_dir+'/config.ini'
    
    print("load config file "+config_file)
    
    if os.path.isfile(config_file) == True:
        config = configparser.ConfigParser()
        config.read(config_file)
        if 'kong' not in config or 'db' not in config:
            print(config.sections())
            print("config file "+config_file+" error\n")
    else:
        print("config file "+config_file+" not found\n")
        sys.exit(0)
    
    # The Endpoint of base URL
    kong_admin_port = config['kong']['admin_port']
    kong_api_port = config['kong']['api_port']
    kong_base_url = config['kong']['host']
    kongurl = kong_base_url+":"+kong_admin_port
    kongapiurl = kong_base_url+":"+kong_api_port
    app.run(debug=True,host='0.0.0.0',port=7788)
