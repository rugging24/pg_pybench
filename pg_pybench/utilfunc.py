#!/usr/bin/python

from __future__ import print_function
import sys,os
import psutil
import math
import csv,datetime
import logging
import executeSql as sql

# programs needed - psql, pgbench , gnuplot

def writeCSV(fileName,test) :
	f = open(fileName,'r')
	fo = open('timing.csv','ab')
	of = csv.writer(fo, delimiter=',')
	for line in f :
		client,trans,latency,filenum,sec,usec = line.split()
		latency=float(latency) / 1000
		timestamp=float(sec)+float(usec) / 1000000
		d=datetime.datetime.fromtimestamp(timestamp)
		r=[d.isoformat(" "),filenum,latency,test]
		of.writerow(r)
		#print (line.split())
	f.close()
	fo.close()


def getLevelScale(testType) :
	# this runs the test on 3 different levels
	# 1 - in buffer, 
	# 2 - mostly in cache, and 
	# 3 - all on disk

	scales = {}
	if str(testType).lower() != 'custom' :
		mem = psutil.virtual_memory()
		RAM = math.ceil(mem.total/float(1024*1024*1024))	
		# set the scale 
		ratio = [0.1,0.9,4.0]
		titles = ['In Buffer','Mostly in Cache', 'All on disk']
		i = 0
		for r in ratio :
			scales.update( "'" + titles[i]] + "'" : int(math.ceil((float(75) * float(r) * float(RAM)))) )
			i += 1
	elif str(testType).lower() == 'custom' :
		# Scale will always be 1 for a custom test
		scales = {'custom file' : 1 }

	return  scales

def truncateTiming() :
	return " truncate table timing  "

def storeTestLatency(test) :
	return "update tests set avg_latency=(select avg(latency) from \
                 timing where tests.test=timing.test), max_latency=(select max(latency)from \
                 timing where tests.test=timing.test), percentile_90_latency=(select latency \
                 from timing where tests.test=timing.test \
                 order by latency offset (round(0.90*trans)) limit 1) where tests.test='{0:s}'".format(test.split("\n")[0]) 

def copyCSV(basedir,filename) :
	return " \copy timing from '{0:s}' with csv ".format(basedir + '/' + filename)

def insertTestResult(script,client,thread,scale,testdb,start,end,tps,trans) :
	return "insert into tests(script,clients,workers,set,scale,dbsize,start_time,end_time,tps,trans) \
                select '{0:s}','{1:s}','{2:s}',max(set),'{3:s}',pg_database_size('{4:s}'),'{5:s}','{6:s}',{7:s},{8:s} from testset"\
                " returning test".format( script,str(client),str(thread),str(scale),testdb,str(start.rstrip()),str(end.rstrip()),str(tps),str(trans)  )


def createDBText(dbname) :
	return 'CREATE DATABASE {0:s} TABLESPACE = {1:s}'.format(dbname, getTableSpaceName())

def dropDBText(dbname) :
	return "DROP DATABASE IF EXISTS {0:s} ".format(dbname)

def getTableSpaceName () :
	return 'benchmark_test_tablespace'

def createTableSpaceText(location) :
	location = location + os.sep + getTableSpaceName()
	os.mkdir(location )	
	return "CREATE TABLESPACE {0:s} LOCATION '{1:s}' ".format(getTableSpaceName(), location)

def dropTableSpaceText() :
	return 'DROP TABLESPACE IF EXISTS {0:s}'.format(getTableSpaceName())


def checkDBExist(dbname) :
	return "select coalesce(datname,null) from pg_stat_database where datname = '{0:s}'".format(dbname)


def getSysInfo(version) :
	text = ''
	if version <= 9.4 :
		text = "select current_setting('shared_buffers') , current_setting('checkpoint_segments') , current_setting('checkpoint_completion_target')"
	elif version >= 9.5 : 
		text = "select current_setting('shared_buffers') , current_setting('max_wal_size') , current_setting('checkpoint_completion_target')"
	return text 

def insertNewTest(version,sysinfo,tbsLocation) :
	props = {}
	if version <= 9.4 :
		keys = ['shared_buffers','checkpoint_segments','checkpoint_completion_target']
	elif version >= 9.5 :
		keys = ['shared_buffers','max_wal_size','checkpoint_completion_target']
	i = 0 
	
	for p in sysinfo :
		props.update("'" + keys[i] + "'" : p )   
		i += 1

	comment= 'Test performed at {0:s} with the sys parameters stated in the config_info column - '.format( str(datetime.datetime.now()) )
	return	"insert into testset(set,config_info,info) select coalesce(max(set),0) + 1,'{0:s}','{1:s}' from testset returning set".format(str(props),comment) 

def getDBVersion(param) :
	pgversion = sql.queryDB (param,"select substring(version() from '(\d\.\d)')","read")[1][0]	
	return pgversion


def getCurrentDBSetting(param,setting_name) :
	dbsetting = sql.queryDB (param,"select current_setting('{0:s}')".format(str(setting_name)),"read")[1][0]
	return dbsetting

def droppgBenchTables() :
        return 'drop table if exists pgbench_accounts cascade;  \
                drop table if exists pgbench_branches cascade; \
                drop table if exists pgbench_tellers cascade; \
                drop table if exists pgbench_history cascade;'

def findProg(name):
        prog = None
        for path in os.getenv("PATH").split(os.path.pathsep):
                full_path = path + os.sep + name
                if os.path.exists(full_path) :
                        prog = full_path
        return prog


def utilfunc(dest,prog,param) :
        c_str = []
        if dest == 'resultdb':
                c_str = [ findProg(prog),'-h',param['resulthost'],'-U',param['resultuser'],'-p',param['resultport'],param['resultdbname']]
        elif dest == 'testdb' :
                c_str = [ findProg(prog),'-h',param['testhost'],'-U',param['testuser'],'-p',param['testport'],param['testdbname']]
	elif dest == 'createdb' :
                c_str = [ findProg(prog) ,'-h',param['resulthost'],'-U',param['resultuser'],'-p',param['resultport'],'postgres']

        return c_str


