#-*- coding=UTF-8 -*-
#!/bin/python 
import requests
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import Flask, g
from flask import Flask, redirect, url_for, Response, abort
from flask import session
from wtforms import Form, BooleanField, StringField, TextAreaField, HiddenField, SelectField, validators
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from wtf_tinymce import wtf_tinymce
from wtf_tinymce.forms.fields import TinyMceField
import os.path
import sys
import configparser
import base64
import apidb
import nchciam

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
wtf_tinymce.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

APIList = []

def get_db():
    idb = apidb.apidb(app.config_file)
    return idb

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = base64.b64decode(id).decode('utf-8')
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name)

    def is_authenticated(self):
        return True
    def is_anonymous(self):
        return False
    def is_active(self):
        return True

class apiForm(Form):

    apiid = HiddenField('apiid')
    version = StringField('* Version', [validators.Length(min=1, max=64)])
    name = StringField('* Name', [validators.Length(min=1, max=64)])
    shortname = StringField('* Short description', [validators.Length(min=1, max=64)])
    method = SelectField('* Method', choices=[('',''),('GET', 'GET'), ('POST', 'POST'),('DELETE', 'DELETE'), ('PATCH', 'PATCH'), ('PUT','PUT')])
    uri = StringField('* URI', [validators.Length(min=1, max=64)])
    host = StringField('* Host', [validators.Length(min=1, max=64)])
    group = SelectField(u'* Servic/Group', choices=[('','0')])
    description = TinyMceField('Description', tinymce_options={'toolbar': 'insert | undo redo |  formatselect | bold italic backcolor  | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help'})
    params = TinyMceField('Params', tinymce_options={'toolbar': 'insert | undo redo |  formatselect | bold italic backcolor  | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help'})
    example = TinyMceField('Example', tinymce_options={'toolbar': 'insert | undo redo |  formatselect | bold italic backcolor  | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help'})
    success = TinyMceField('Success', tinymce_options={'toolbar': 'insert | undo redo |  formatselect | bold italic backcolor  | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help'})
    error = TinyMceField('Error', tinymce_options={'toolbar': 'insert | undo redo |  formatselect | bold italic backcolor  | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help'})


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


def is_admin():
    cun = current_user.name
    if cun == 'ckan':
        return True
    return False

def is_myapi(apiid):
    db = get_db()
    row = db.get_uid(apiid)
    apiuid=row[0]['uid']
    if apiuid == session['uid']:
        return True
    return False

@app.context_processor
def inject_data():
    groups = {}
    db = get_db()
    get_group = db.get_group()
    
    for group in get_group:
        name = group['name']
        id = group['id']
        groups[id]=name
    return dict(groups=groups)

@app.route('/')
@app.route('/index')
@app.route("/all")
def index():
    print("read config from "+app.config_file)
    listurl = app.kongurl + "/apis"
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


@app.route("/group", methods=['GET','POST'])
def group():
    
    listurl = app.kongurl + "/apis"
    groupid = request.args.get('groupid')
    if groupid == '':
        groupid='0'
    
    APIList=[]
    db = get_db()
    apis_in_group = db.get_group_apis(groupid)
    for api in apis_in_group:
        apiid = api['apiid']
        kongData = runApi(listurl+"/"+apiid)
        apiName = kongData['name']
        apiShortName = api['shortname']
        apiDesc = api['description']
        apiGroup = api['apigroup']
        groupName = db.name_of_group(apiGroup)
        apiListData = {'name':apiName, 'shortname':apiShortName, 'apidesc':apiDesc, 'apigroup':apiGroup, 'apiid':apiid, 'groupname':groupName}
        APIList.append(apiListData)
        
    return render_template('group.html', api_list = APIList)

@app.route("/kong")
def kong():

    apidata = runApi(app.kongurl+'/')
    kongstr = json.dumps(apidata, indent=4)
    return render_template('kong.html', kong = kongstr)

@app.route("/updateAPI")
@login_required
def updateAPI():
    db = get_db()
    form = apiForm(request.form)
    groups = []
    group_row = db.get_group()
    for g in group_row:
        gdata={}
        gdata['id'] = g['id']
        gdata['name'] = g['name'].replace(" ", "")
        groups.append(gdata)
    form.group.choices = [(str(g['id']), str(g['name'])) for g in groups]

    if request.method == 'GET':
        apiId = request.args.get('apiid')
        if is_admin() == True or is_myapi(apiId):
            apidata = runApi(app.kongurl+'/apis/'+apiId)
            if 'methods' not in apidata: apidata['methods'] = ['GET']
            if 'uris' not in apidata: apidata['uris'] = ['']
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
                apidata['uid'] = session.get('uid', 'uid error')
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
    return redirect(url_for('.index'))

@app.route("/saveAPI", methods=['POST'])
@login_required
def saveAPI():
    db = get_db()
    form = apiForm(request.form)
    groups = []
    group_row = db.get_group()
    for g in group_row:
        gdata={}
        gdata['id'] = g['id']
        gdata['name'] = g['name'].replace(" ", "")
        groups.append(gdata)
    form.group.choices = [(str(g['id']), str(g['name'])) for g in groups]

    if request.method == 'POST' and form.validate():
        apiid = form.apiid.data
        if is_admin() == True or is_myapi(apiid):
            updateApiUrl = app.kongurl+"/apis/"+apiid
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
            apidata['uid'] = session.get('uid', 'uid error')
            db = get_db()
            db.update_api(apidata)
            return redirect(url_for('.index'))
        else:
            return redirect(url_for('.index'))
    return render_template('updateAPI.html', form=form)
    
@app.route("/deleteAPI")
@login_required
def deleteAPI():

    if request.method == 'GET':
        apiId = request.args.get('apiid')
        if is_admin() == True or is_myapi(apiId):
            apidata = runApi(app.kongurl+'/apis/'+apiId, 'delete')
            db = get_db()
            db.delete_api(apiId)
        return redirect(url_for('index'))

@app.route("/api")
@app.route("/displayAPI")
def displayAPI():
    if request.method == 'GET':
        apiId = request.args.get('apiid', '000')
        apidata = runApi(app.kongurl+'/apis/'+apiId)
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
            apidata['params'] = row['params']
            apidata['version'] = row['version']
            apidata['apigroup'] = row['apigroup']
            apidata['example'] = row['example']
            apidata['success'] = row['success']
            apidata['error'] = row['error']
            apidata['uid'] = session.get('uid', 'uid error')

        return render_template(
            'displayAPI.html', api = apidata, kongapiurl=app.kongapiurl
            )
    return redirect(url_for('index'))

@app.route('/addAPI', methods=['GET', 'POST'])
@login_required
def addAPI():
    db = get_db()
    form = apiForm(request.form)

    groups = []
    group_row = db.get_group()
    for g in group_row:
        gdata={}
        gdata['id'] = g['id']
        gdata['name'] = g['name'].replace(" ", "")
        groups.append(gdata)
    form.group.choices = [(str(g['id']), str(g['name'])) for g in groups]

    if request.method == 'POST' and form.validate():
        addApiUrl = app.kongurl+"/apis"
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
        apidata['uid'] = session.get('uid')
        db.add_api(apidata)
        return redirect(url_for('index'))
   
    return render_template('addAPI.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nauth = nchciam.nchcIAM(app.config_file)
        if nauth.login(username, password) == True:
            user = User(nauth.id)
            login_user(user)
            session['uid'] = str(current_user.id)
            session['uname'] = str(current_user.name)
            if not request.args.get("next"):
                return redirect(url_for('.index'))
            return redirect(request.args.get("next"))
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')

@app.before_request
def before_request():
    g.user = current_user

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out and redirect to <a href="/">homepage manually</a></p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)


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
    #kongurl = kong_base_url+":"+kong_admin_port
    #kongapiurl = kong_base_url+":"+kong_api_port
    #app.run(debug=True,host='0.0.0.0',port=7788)
    app.config_file = config_file
    app.kongapiurl = kong_base_url+":"+kong_api_port
    app.kongurl = kong_base_url+":"+kong_admin_port
    app.debug = True
    app.testing = True
    app.run(host='0.0.0.0')
