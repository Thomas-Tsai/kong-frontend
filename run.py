import sys
import os.path
import configparser

from apiServer import app
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
