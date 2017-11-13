#-*- coding=UTF-8 -*-
import json, requests
import base64
import configparser

class nchcIAM():

    def __init__(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)
        print(config.sections())

        self.APP_PRIVATE_ID = config['iam']['APP_PRIVATE_ID']
        self.APP_PRIVATE_PASSWD = config['iam']['APP_PRIVATE_PASSWD']
        self.APP_COMPANY_ID = config['iam']['APP_COMPANY_ID']
        self.APP_COMPANY_UUID = config['iam']['APP_COMPANY_UUID']
        self.APP_DEPT_NODE_UUID = config['iam']['APP_DEPT_NODE_UUID']
        self.localip =  config['iam']['ip']
        self.id = ''

    def login(self, username, password):
        # Step 1 WS-Z01-A0-01 : 進行應用系統身分認證(03身份認證_基本)
        # URL = https://iam-api.nchc.org.tw/app/request_basic_authentication/
        
        url = 'https://iam-api.nchc.org.tw/app/request_basic_authentication/'
        resp = requests.post(url, json={"APP_PRIVATE_ID" : self.APP_PRIVATE_ID, "APP_PRIVATE_PASSWD" : self.APP_PRIVATE_PASSWD}, verify=False)
        #print resp.text
        app_login_data = json.loads(resp.text)
        #print("Step 1 WS-Z01-A0-01 : 進行應用系統身分認證(03身份認證_基本)")
        #print(app_login_data)
        
        if app_login_data['ERROR_CODE'] == '0': 
            print("app login ok\n") 
        else: 
            return False

        # Step 2 WS-Z01-B0-01 : 進行應用入口網使用者身分認證(03身份認證_基本)
        # URL = https://iam-api.nchc.org.tw/app_user/request_basic_authentication/
        
        url = 'https://iam-api.nchc.org.tw/app_user/request_basic_authentication/'
        
        user_login_json = {
        	"PUBLIC_APP_SSO_TOKEN" : app_login_data['PUBLIC_APP_SSO_TOKEN'],
        	"PRIVILEGED_APP_SSO_TOKEN" : app_login_data['PRIVILEGED_APP_SSO_TOKEN'],
        	"APP_USER_LOGIN_ID" : username,
        	"APP_COMPANY_ID" : self.APP_COMPANY_ID,
        	"APP_USER_LOGIN_PASSWD" : password,
        	"AUTH_FROM_ADDRESS": self.localip
        	}
        resp = requests.post(url, json=user_login_json, verify=False) 
        user_login_data = json.loads(resp.text)
        #print("Step 2 WS-Z01-B0-01 : 進行應用入口網使用者身分認證(03身份認證_基本)")
        #print(user_login_data)

        if user_login_data['ERROR_CODE'] == '0': 
            bid = base64.b64encode(username.encode('utf-8'))
            self.id = bid.decode('utf-8')
            return True
        else: 
            return False
        return False

    

