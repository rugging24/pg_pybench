#!/usr/bin/python

from __future__ import print_function
from configobj import ConfigObj
import getopt
import sys,os
import subprocess
import psutil
import math
import csv,datetime
import logging



def usage() :
	print ( ' python runTest.py [options] \n'\
		'Options : \n' \
		'-h,--help			displays the help options\n'\
		'-c ,--conf			used to pass the configuration file to the script\n'\
		'--query-mode			for passing the query mode [simple|extended|prepared] default is simple \n'\
		'-t,--test-type			accpets values read|write|update|all|custom \n'\
		'				use the custom value only if you are providing a custom sql file and are probably\n'\
	  	'				not using the pgbench default data set\n'\
		'-f,--file			the full path (with extension, usually .sql) of the custom sql file \n' )


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


def getLevelScale() :
	# this runs the test on 3 different levels
	# 1 - in buffer, 
	# 2 - mostly in cache, and 
	# 3 - all on disk

	mem = psutil.virtual_memory()
	RAM = math.ceil(mem.total/float(1024*1024*1024))	
	# set the scale 
	ration = [0.1,0.9,4.0]
	titles = ['In Buffer','Mostly in Cache', 'All on disk']
	SCALES = {}
	i = 0
	for r in ration :
		SCALES[titles[i]] = int(math.ceil((float(68) * float(r) * float(RAM))))
		i += 1

	return  SCALES

def truncateTiming() :
	return " truncate table timing  "

def storeTestLatency(test) :
	return "update tests set avg_latency=(select avg(latency) from \
                 timing where tests.test=timing.test), max_latency=(select max(latency)from \
                 timing where tests.test=timing.test), percentile_90_latency=(select latency \
                 from timing where tests.test=timing.test \
                 order by latency offset (round(0.90*trans)) limit 1) where tests.test='{0:s}'".format(test.split("\n")[0]) 

def copyTimingCSV(basedir) :
	return " copy timing from '{0:s}' with csv ".format(basedir + '/timing.csv')

def insertTestResult(script,client,thread,scale,testdb,start,tps,trans) :
	return "insert into tests(script,clients,workers,set,scale,dbsize,start_time,end_time,tps,trans) \
                select '{0:s}','{1:s}','{2:s}',max(set),'{3:s}',pg_database_size('{4:s}'),'{5:s}',now(),{6:s},{7:s} from testset"\
                " returning test".format( script,str(client),str(thread),str(scale),testdb,str(start.rstrip()),str(tps),str(trans)  )

def getPGVersion():
	return "select substring(version() from '(\d\.\d)')"

def createResultDb(dbname) :
	return 'CREATE DATABASE {0:s}'.format(dbname)

def checkResultDb(resultdb) :
	return "select coalesce(datname,null) from pg_stat_database where datname = '{0:s}'".format(resultdb)

def insertNewTest(testname) :
	testname = testname + ' - ' + str(datetime.datetime.now())
	return	"insert into testset(set,info) select coalesce(max(set),0) + 1,'{0:s}' from testset".format(testname) 
	

def houseKeeping() :
        return 'drop table if exists pgbench_accounts cascade;  \
                drop table if exists pgbench_branches cascade; \
                drop table if exists pgbench_tellers cascade; \
                drop table if exists pgbench_history cascade;'

def getProg(name):
        prog = None
        for path in os.getenv("PATH").split(os.path.pathsep):
                full_path = path + os.sep + name
                if os.path.exists(full_path) :
                        prog = full_path
        return prog


def utilfunc(dest,prog,param) :
        c_str = []
        if dest == 'resultdb':
                c_str = [ param[prog],'-h',param['RESULTHOST'],'-U',param['RESULTUSER'],'-p',param['RESULTPORT'],param['RESULTDB']]
        elif dest == 'testdb' :
                c_str = [ param[prog],'-h',param['TESTHOST'],'-U',param['TESTUSER'],'-p',param['TESTPORT'],param['TESTDB']]
	elif dest == 'createdb' :
                c_str = [ param[prog],'-h',param['RESULTHOST'],'-U',param['RESULTUSER'],'-p',param['RESULTPORT'],'postgres']

        return c_str



def getConfParameters(switches):
        conf = None
        custom = None
        level = None
        qmode = None
	

        try :
                opts,args = getopt.getopt(switches[1:],'f:c:t:h',["conf=","help","query-mode=","test-type=","level=","file="])

		if len(opts) == 0 :
			usage()

                for opt,arg in opts :
                        if opt in ('-h','--help') :
				usage()
                                sys.exit(0)
                        elif opt in ('-c','--conf') :
                                conf = arg
                        elif opt in ('-f', '--file') :
                                custom = arg
                                if os.path.exists(custom) == False or custom.endswith('.sql') == False :
                                        print ("Specified custom file does not exist or its not a valid sql file... Aborting...")
                                        sys.exit(1)
                        elif opt == '--level' :
                                level = arg
                        elif opt == '--query-mode' :
                                qmode = arg
			elif opt in ('-t','--test-type') :
				t_type = arg

        except getopt.GetoptError as err :
		print (err)
		usage()

        param = {}
        config = ConfigObj(conf)
        for vals in config.values() :
                param.update(vals)

        param['BASEDIR'] = os.path.dirname(os.path.realpath(sys.argv[0]))
        param['PGBENCH'] = getProg("pgbench")
	param['PSQL'] = getProg("psql")
        param['GNUPLOT'] = getProg("gnuplot")
        param['RESULTHOST'] = param['RESULTHOST'] if param['RESULTHOST'] != '' else param['TESTHOST']
        param['RESULTUSER'] = param['RESULTUSER'] if param['RESULTUSER'] != '' else param['TESTUSER']
        param['RESULTPORT'] = param['RESULTPORT'] if param['RESULTPORT'] != '' else param['TESTPORT']
        param['RESULTDB'] = param['RESULTDB'] if param['RESULTDB'] != '' else param['TESTDB']
        param['TRANSACTIONS'] = param['TRANSACTIONS'] if param['TRANSACTIONS'] != '' else 1000
	param['RUNTIME'] = param['RUNTIME'] if param['RUNTIME'] != '' or param['RUNTIME'] != None else 600
        param['QUERYMODE'] = qmode if qmode in ('simple','prepared','extended')  else 'simple'
	param['TESTTYPE'] = t_type if t_type in ('read','write','update','all','custom')  else 'all'
        param['CUSTOMFILE'] = custom
	

        if param['PGBENCH'] == None :
                print ("Exiting, pgbench not found .... install and try again...")
                sys.exit(2)
        elif param['GNUPLOT'] == False :
                print ('Exiting, gnuplot not found in ... this is required for the plots' )
                os._exit(1)
        elif len(param['CLIENTS'].split()) == 0 :
                param['CLIENTS'] = 5
        elif  param['REPEATTIME'] == '' or param['REPEATTIME'] == None :
                param['REPEATTIME'] = 3

        return param


