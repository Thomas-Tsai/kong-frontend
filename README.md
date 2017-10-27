# kong-frontend
A python flask version of kong frontend

# How to run

## Prepare python virtual environment and install modules

    python3 -m venv kong-env
    source kong-env/bin/active
    pip3 install -r  requirements.txt
  
## before you run

update file api-doc-server.py and replace tour kong url to kongurl

    kongurl = "http://10.12.0.6:8001"
  
create local database
  
    sqlite3 apidoc.db < create-db.sql
  
## almost ready, run it

    python3 api-doc-server.py
