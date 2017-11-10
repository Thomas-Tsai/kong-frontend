#!/bin/python
# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras
import configparser

class apidb():
    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        config = configparser.ConfigParser()
        config.read(config_file)
        print(config.sections())

        self.conn = 0
        db = config['db']['database']
        user = config['db']['user']
        server = config['db']['host']
        password = config['db']['password']

        try:
            self.conn = psycopg2.connect("dbname=%s user=%s host=%s password=%s" % (db, user, server, password))
            self.cur = self.conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
        except:
            print("connect db error")

    def get_group(self):
        rows = []
        try:
            sql = "select id, name from group"
            print(sql)
            self.cur.execute(sql)
            rows = self.cur.fetchall()
        except:
            print("select group error")
        return rows
    def get_api(self, apiid):
        apis = []
        rows=[]
        try:
            sql = "select shortname, description, params, version, apigroup, example, success, error from apis where apiid like '{0}'".format(apiid)
            print(sql)
            self.cur.execute(sql)
            rows = self.cur.fetchall()
        except:
            print("select api "+apiid+" error")
        return rows

    def get_apis(self, apiid):
        apis = []
        rows=[]
        try:
            sql = "select shortname, description, apigroup from apis where apiid like '{0}'".format(apiid)
            print(sql)
            self.cur.execute(sql)
            rows = self.cur.fetchall()
        except:
            print("select apis error")
        return rows

    def exist(self, api):
        return 0

    def add_api(self, api):
        pkg_c = self.exist(api)
        if pkg_c > 0:
            print("api exist?!")
        else:
            try:
                sql = "insert into apis(id, shortname, description, apiid, apigroup, version, params, example, success, error) values ('{2}', '{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')".format(api['shortName'], api['Desc'], api['apiid'], api['Group'], api['Version'], api['Params'], api['Example'], api['Success'], api['Error'])
                print(sql)
                self.cur.execute(sql)
                self.conn.commit()
                print("insert api ok")
            except:
                print("insert api error")

    def update_api(self, api):
        
        print(api)
        try:
            sql="update apis set shortname='{0}', description='{1}', version='{2}', apigroup='{3}', params='{4}', example='{5}', success='{6}', error='{7}' where apiid like '{8}'".format(api['shortName'], api['Desc'], api['Version'], api['Group'], api['Params'], api['Example'], api['Success'], api['Error'], api['apiid'])
            print(sql)
            self.cur.execute(sql)
            self.conn.commit()
            print("update ok"+api['apiid'])
        except:
            print("update error "+api['apiid'])

    def delete_api(self, apiid):
        try:
            self.cur.execute("""delete from apis where apiid=?""" , (apiid,))
            self.conn.commit()
        except:
            print("delete api "+apiid+"error")

