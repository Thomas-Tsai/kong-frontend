# kong-frontend

A python flask version of kong frontend

# How to run

## clone the source first

    git clone ...
    cd kong-frontend

## Prepare python virtual environment and install modules (optional)

    python3 -m venv kong-env
    source kong-env/bin/active
    
## install python3 and pip

    apt-get install python3 python3-pip
    pip3 install -r  requirements.txt

## create and prepare databse

    apt-get install postgresql # if you run database locally
    apt-get install postgresql-client postgresql-client postgresql-client-common # for psql cmd
    psql -h $db_host -U $db_user < apis.sql

## prepare web server

    apt-get install apache2 libapache2-mod-wsgi-py3
    cp apache2-site.conf /etc/apache2/sites-available/kongfd.conf
    mkdir -p /var/www/kong-frontend/
    cp run.wsgi /var/www/kong-frontend/
    a2ensite kongfd
    
## config file
    mkdir /etc/kong-frontend/
    cp config.ini.sample /etc/kong-frontend/config.ini
    ## manual chang kong url and db information

## restart apache2

    service apache2 reload
    service apache2 restart
