#!/usr/bin/python
import os,sys 
import mains
import argparse 

# Three levels of checks to be performed related to disks 

# - In Buffer Test: 0.1 X RAM
# - Mostly Cached: 0.9 X RAM
# - Mostly on Disk: 4.0 X RAM

# See https://wiki.postgresql.org/wiki/Pgbenchtesting for more details  :) 

def runBenchmark() :
	parser = argparse.ArgumentParser(prog='pg_pybench' ,description = 'Runs PostgreSQL Database Benchmark')
	parser.add_argument ( '--initdb', type=int , default=0 ,help='set to 1 if a custom script is to be used')
	parser.add_argument ( '--transactions', type=str , default=None ,nargs='?' ,help='Comma separated number of transactions per client')
	parser.add_argument ( '--clients', type=str , default='2,10,10,30,40,50,60,70,80,90,100,110,120,130' ,nargs='?' ,help='Comma separated number of clients to connect to the database')
	parser.add_argument ( '--repeattime', type=int , default=3 ,help='Sets the number of times the benchmark process is to be repeated')
	parser.add_argument ( '--runtime', type=int , default=60 ,help='Time in Seconds the benchmark should run. This and the --transactions parameter are mutually exclusive')
	parser.add_argument ( '--threadcount', type=str , default="1,2" , nargs='?' ,help='Number of processor to be used in the benchmark for concurrent connections.\
			      ensure the number of clients is a multiple of the threadcount otherwise , the script will exit.')
	parser.add_argument ( '--testhost', type=str , default='localhost' ,help='Host of the test database')
	parser.add_argument ( '--testuser', type=str , default='postgres' ,help='User of the test database')
	parser.add_argument ( '--testport', type=str , default='5432' ,help='Port of the test database')
	parser.add_argument ( '--testdbname', type=str , default='bench_db' ,help='Port of the test database')
	parser.add_argument ( '--testuserpassword', type=str , default=None ,help='Password of the test user in the test database')
	parser.add_argument ( '--resulthost', type=str , default='localhost' ,help='Host of the result database')
        parser.add_argument ( '--resultuser', type=str , default='postgres' ,help='User of the result database')
        parser.add_argument ( '--resultport', type=str , default='5432' ,help='Port of the result database')
        parser.add_argument ( '--resultdbname', type=str , default='result_db' ,help='Name of the result database')
	parser.add_argument ( '--resultuserpassword', type=str , default=None ,help='Password of the result user in the result database')
	parser.add_argument ( '--querymode', type=str , default='simple' ,choices=['simple', 'prepared', 'extended'] ,help='Specifies the query mode to be used')
	parser.add_argument ( '--testtype', type=str , default='all' ,choices=['read','write','update','all','custom'] ,help='Type of test to perform')
	parser.add_argument ( '--customfile', type=str , default=None  ,help='Path (absolute/relative) to the custom sql file')
	parser.add_argument ( '--resulttablespaces', type=str , default='pg_default'  ,help='tablesspace where the result db is created')
	parser.add_argument ( '--testtablespaces', type=str , default='pg_default', nargs='?'  ,help='Comma separated list of the mount point of each disk to be benchmarked')
	parser.add_argument ( '--delay', type=int , default=5  ,help='Interval in seconds for which the I/O and cpu load are to be measured')


	param = {}
	args = parser.parse_args()

	if args.customfile != None and os.path.isfile(args.customfile) and str(args.customfile).find('.sql') != -1 :
		param['transaction'] = args.customfile
	#else :
	#	print ('Invalid custom file format provided or an incorrect path to the custom file was supplied')
	#	sys.exit(0)

	param['transaction'] = str(args.transactions).split(',') if args.transactions != None else None
	param['clients'] = str(args.clients).split(',')
	param['repeattime'] = args.repeattime
	param['runtime'] = args.runtime
	param['threadcount'] = str(args.threadcount).split(',')
	param['testhost'] = args.testhost
	param['testuser'] = args.testuser
	param['testport'] = args.testport
	param['testdbname'] = args.testdbname
	param['resulthost'] = args.resulthost
	param['resultuser'] = args.resultuser
	param['resultport'] = args.resultport
	param['resultdbname'] = args.resultdbname
	param['querymode'] = args.querymode 
	param['testtype'] = args.testtype
	param['resulttablespaces'] = args.resulttablespaces
	param['testtablespaces'] = str(args.testtablespaces).split(',')
	param['testuserpassword'] = args.testuserpassword
	param['resultuserpassword'] = args.resultuserpassword
	param['initdb'] = args.initdb
	param['delay'] = args.delay

	mains.callFunctions(param)


if __name__ == '__main__' :
	runBenchmark()

