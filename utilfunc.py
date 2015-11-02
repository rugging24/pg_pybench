#!/usr/bin/python

from __future__ import print_function
from configobj import ConfigObj
import getopt
import sys,os
import subprocess
import psutil
import math
import csv,datetime



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
	mem = psutil.virtual_memory()
	RAM = math.ceil(mem.total/float(1024*1024*1024))	
	# set the scale 
	ration = '0.1' # 0.9 4.0'
	SCALES = []
	for r in ration.split() :
		SCALES.append(int(math.ceil((float(68) * float(r) * float(RAM)))))

	return  SCALES

def checkResultDb(resultdb) :
	return "select coalesce(datname,null) from pg_stat_database where datname = '{0:s}'".format(resultdb)
	

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
                c_str = [ getProg(prog),'-h',param['RESULTHOST'],'-U',param['RESULTUSER'],'-p',param['RESULTPORT'],param['RESULTDB']]
        elif dest == 'testdb' :
                c_str = [ getProg(prog),'-h',param['TESTHOST'],'-U',param['TESTUSER'],'-p',param['TESTPORT'],param['TESTDB']]
	elif dest == 'createdb' :
                c_str = [ getProg(prog),'-h',param['RESULTHOST'],'-U',param['RESULTUSER'],'-p',param['RESULTPORT'],'postgres']

        return c_str



def getConfParameters(switches):
        conf = None
        custom = None
        level = None
        qmode = None

        try :
                opts,args = getopt.getopt(switches[1:],'f:c:h',["conf=","help","query-mode=","test-type=","level=","file="])

                for opt,arg in opts :
                        if opt in ('-h','--help') :
                                print ("python runset.py -c|--conf pgbench.conf [--query-mode simple|extended|prepared] --test-type read|write|update|all")
                                sys.exit(0)
                        elif opt in ('-c','--conf') :
                                conf = arg
                        elif opt in ('-f', '--file') :
                                custom = arg
                                if os.path.exists(arg) == False :
                                        print ("Specified custom file does not exist... Aborting...")
                                        sys.exit(1)
                        elif opt == '--level' :
                                level = arg
                        elif opt == '--query-mode' :
                                qmode = arg
			elif opt == '--test-type' :
				t_type = arg
			

        except getopt.GetoptError as err :
                print (err)

        param = {}
        config = ConfigObj(conf)
        for vals in config.values() :
                param.update(vals)

        param['BASEDIR'] = os.path.dirname(os.path.realpath(sys.argv[0]))
        param['PGBENCHBIN'] = getProg("pgbench")
        param['GNUPLOT'] = getProg("gnuplot")
        param['RESULTHOST'] = param['RESULTHOST'] if param['RESULTHOST'] != '' else param['TESTHOST']
        param['RESULTUSER'] = param['RESULTUSER'] if param['RESULTUSER'] != '' else param['TESTUSER']
        param['RESULTPORT'] = param['RESULTPORT'] if param['RESULTPORT'] != '' else param['TESTPORT']
        param['RESULTDB'] = param['RESULTDB'] if param['RESULTDB'] != '' else param['TESTDB']
        param['TRANSACTIONS'] = param['TRANSACTIONS'] if param['TRANSACTIONS'] != '' else 1000
	param['RUNTIME'] = param['RUNTIME'] if param['RUNTIME'] != '' or param['RUNTIME'] != None else 600
        param['QUERYMODE'] = qmode if qmode in ('simple','prepared','extended')  else 'simple'
	param['TESTTYPE'] = t_type if t_type in ('read','write','update','all')  else 'all'
        param['CUSTOMFILE'] = custom
	

        if param['PGBENCHBIN'] == None :
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


