import sqlite3
import requests
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import Flask, g
from flask import Flask, redirect, url_for

app = Flask(__name__)

SQLITE_DB_PATH = 'apidoc.db'
APIList = []
# The Endpoint of base URL
#kongurl = "http://10.12.0.6:8001"
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

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def runApi(url):
    myResponse = requests.get(url, verify=True)
    print (myResponse.status_code)
    
    # For successful API call, response code will be 200 (OK)
    print("response ", myResponse.text)
    jData = {}
    if(myResponse.ok):

        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
        jData = json.loads(myResponse.text)
    
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
    print(kongData)
    APIList = []
    apiData = kongData['data']
    for api in apiData:
        apiID = api['id']
        db = get_db()
        db.row_factory = dict_factory
        apiShortName=''
        apiDesc=''
        apiGroup=''
        #(apiShortName, apiDesc, apiGroup) = db.execute("""select (name, description, group_name) from apis where apiID=?;""" , (apiID)).fetchone()
        cursor = db.execute("""select name, description, group_name from apis where apiID=?;""" , (apiID,))
        for row in cursor:
            apiShortName = row['name']
            apiDesc = row['description']
            apiGroup = row['group_name']
        
        apiName = api['name']
        apiListData = {'apiname':apiName, 'apiid':apiID, 'apishortname':apiShortName, 'apidesc':apiDesc, 'apigroup':apiGroup}
        APIList.append(apiListData)
    return render_template('index.html', api_list = APIList)

@app.route('/addAPI', methods=['GET', 'POST'])
def addAPI():
    params = None
    if request.method == 'GET':
        apiId = request.args.get('apiid', '000')
        return render_template(
            'addAPI.html',
            apiid=apiId,
            )
    if request.method == 'POST':
        apiID = request.form.get('apiid', "000")
        apiName = request.form.get('name', "")
        apiDesc = request.form.get('desc', "")
        apiGroup = '0'
        db = get_db()
        db.execute("""insert into apis(name, description, apiID, group_name) values (?,?,?,?);""" , (apiName, apiDesc, apiID, apiGroup))
        db.commit()
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

