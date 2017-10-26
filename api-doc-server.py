import sqlite3
import requests
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import Flask, g
from flask import Flask, redirect, url_for
from wtforms import Form, BooleanField, StringField, TextAreaField, HiddenField, validators

app = Flask(__name__)

SQLITE_DB_PATH = 'apidoc.db'
APIList = []
# The Endpoint of base URL
#kongurl = "http://10.12.0.10:8001"
kongurl = "http://172.17.0.3:8001"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(SQLITE_DB_PATH)
        # Enable foreign key check
        db.execute("PRAGMA foreign_keys = ON")
    return db

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
    method = StringField('method', [validators.Length(min=1, max=64)])
    uri = StringField('uri', [validators.Length(min=1, max=64)])
    host = StringField('host', [validators.Length(min=1, max=64)])
    group = StringField('Group', [validators.Length(min=1, max=64)])
    description = TextAreaField('Description', [validators.optional(), validators.length(max=2048)])
    params = TextAreaField('Params', [validators.optional(), validators.length(max=2048)])
    example = TextAreaField('Example', [validators.optional(), validators.length(max=2048)])
    success = TextAreaField('Success', [validators.optional(), validators.length(max=2048)])
    error = TextAreaField('Error', [validators.optional(), validators.length(max=2048)])

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
        cursor = db.execute("""select shortname, desc, apigroup from apis where apiid=?;""" , (apiID,))
        for row in cursor:
            apiShortName = row['shortname']
            apiDesc = row['desc']
            apiGroup = row['apigroup']
        
        apiListData = {'name':apiName, 'kongid':apiID, 'shortname':apiShortName, 'apidesc':apiDesc, 'apigroup':apiGroup, 'apiid':apiID}
        APIList.append(apiListData)
    return render_template('index.html', api_list = APIList)

@app.route("/updateAPI")
def updateAPI():
    form = apiForm(request.form)
    if request.method == 'GET':
        apiId = request.args.get('apiid')
        apidata = runApi(kongurl+'/apis/'+apiId)
        db = get_db()
        db.row_factory = dict_factory
        cursor = db.execute("""select shortname, desc, params, apigroup, example, success, error from apis where apiid=?;""" , (apiId,))
        for row in cursor:
            apidata['shortname'] = row['shortname']
            apidata['desc'] = row['desc']
            apidata['params'] = row['params']
            apidata['apigroup'] = row['apigroup']
            apidata['example'] = row['example']
            apidata['success'] = row['success']
            apidata['error'] = row['error']
        form.apiid.data = apiId
        form.version.data = ''
        form.name.data = apidata['name']
        form.shortname.data = apidata['shortname']
        #form.method.data = apidata['method']
        form.uri.data = apidata['uris'][0]
        form.host.data = apidata['hosts'][0]
        form.group.data = apidata['apigroup']
        form.description.data = apidata['desc']
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
        upstreamUrl = "http://"+form.host.data+"/"+form.uri.data
        updateApiData = {'name':form.name.data, 'hosts':form.host.data, 'upstream_url':upstreamUrl, 'uris':form.uri.data}
        api = runApi(updateApiUrl, 'patch', updateApiData)
        shortName = form.shortname.data
        apiDesc = form.description.data
        apiGroup = form.group.data
        db = get_db()
        db.execute("""update apis set shortname=?, desc=?, apigroup=? where apiid=?""" , (shortName, apiDesc, apiGroup, apiid))
        db.commit()
        return redirect(url_for('index'))
    
@app.route("/deleteAPI")
def deleteAPI():
    if request.method == 'GET':
        apiId = request.args.get('apiid')
        apidata = runApi(kongurl+'/apis/'+apiId, 'delete')
    return redirect(url_for('index'))

@app.route("/api")
@app.route("/displayAPI")
def displayAPI():
    if request.method == 'GET':
        apiId = request.args.get('apiid', '000')
        apidata = runApi(kongurl+'/apis/'+apiId)
        db = get_db()
        db.row_factory = dict_factory
        cursor = db.execute("""select shortname, desc, params, apigroup, example, success, error from apis where apiid=?;""" , (apiId,))
        for row in cursor:
            apidata['shortname'] = row['shortname']
            apidata['desc'] = row['desc']
            apidata['params'] = row['params']
            apidata['apigroup'] = row['apigroup']
            apidata['example'] = row['example']
            apidata['success'] = row['success']
            apidata['error'] = row['error']
        
        return render_template(
            'displayAPI.html', api = apidata
            )
    return redirect(url_for('index'))

@app.route('/addAPI', methods=['GET', 'POST'])
def addAPI():
    form = apiForm(request.form)
    if request.method == 'POST' and form.validate():
        #print("form data: %s", form.version.data)
        addApiUrl = kongurl+"/apis"
        upstreamUrl = "http://"+form.host.data+"/"+form.uri.data
        addApiData = {'name':form.name.data, 'hosts':form.host.data, 'upstream_url':upstreamUrl, 'uris':form.uri.data}
        api = runApi(addApiUrl, 'post', addApiData)
        print("API ADDED %s", api)
        apiID = api['id']
        #apiName = api['name']
        shortName = request.form.get('shortname', "")
        apiDesc = request.form.get('desccription', "")
        apiGroup = request.form.get('group', "")
        db = get_db()
        db.execute("""insert into apis(shortname, desc, apiid, apigroup) values (?,?,?,?);""" , (shortName, apiDesc, apiID, apiGroup))
        db.commit()
        return redirect(url_for('index'))
    
    return render_template('addAPI.html', form=form)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

