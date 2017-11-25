#!/usr/bin/python3
import sys
import logging
import os.path
import configparser
sys.path.insert(0,"/var/www/kong-frontend")
logging.basicConfig(stream=sys.stderr)

from apiServer import app as application

config_file = "/etc/kong-frontend/config.ini"
if os.path.isfile(config_file) == True:
    config = configparser.ConfigParser()
    config.read(config_file)
else:
    sys.exit(0)

# The Endpoint of base URL
kong_admin_port = config['kong']['admin_port']
kong_api_port = config['kong']['api_port']
kong_base_url = config['kong']['host']
application.config_file = config_file
application.kongapiurl = kong_base_url+":"+kong_api_port
application.kongurl = kong_base_url+":"+kong_admin_port
application.debug = True
application.testing = True
