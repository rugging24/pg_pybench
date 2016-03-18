#!/usr/bin/python

import subprocess,sys
import utilfunc as uf
import performTests as bw
import formTestQuery as tests
import initdbSql as init
import executeSql as sql


def runMainTest(param) :

	# SQL connection parameters for the test and result databases 
	resultDBParam = {'dbname' : param.get('resultdbname'), 'host' : param.get('resulthost'), 'port' : param.get('resultport'),'user' : param.get('resultuser') \
                 'password' : param.get('resultuserpassword')}

	testDBParam = {'dbname' : param.get('testdbname'), 'host' : param.get('testhost'), 'port' : param.get('testport'),'user' : param.get('testuser') \
                 'password' : param.get('testuserpassword')}

	testDBExists = sql.queryDB (testDBParam,uf.checkDBExist(param.get('testdbname')) ,'read')[0][1]
	if testDBExists != param.get('testdbname') :
		sql.queryDB (resultDBParam,uf.createDBText(param.get('testdbname')) + ' TABLESPACE ' + tblspace ,'write')

	pgversion = uf.getDBVersion(testDBParam)
	dataDirLocation = uf.getCurrentDBSetting(testDBParam,'data_directory') 

	script = tests.formulateTestQuery(param['testtype']) if param['testtype'] != 'custom' else param.get('customfile')
	resultDBExists = sql.queryDB (resultDBParam,uf.checkDBExist(param.get('resultdbname')) ,'read')[0][1]

	if resultDBExists != param.get('resultdbname') :
		sql.queryDB (resultDBParam,uf.createDBText(param.get('resultdbname')) ,'write')
		result = sql.queryDB (resultDBParam,init.getInitdbText() ,'write')[0][1]
		if result != 0 : 
			print ('Could not create resultdb objects')
			sys.exit(0)		


		# create the main test entry 
	sysinfo = sql.queryDB (testDBParam,uf.getSysInfo(),'read')
	testset = sql.queryDB (resultDBParam,uf.insertNewTest(sysinfo,dataDirLocation),'read')

		# if a custom script is used, set scale to 1
	scales = uf.getLevelScale( param.get('testtype') )
	for key in scales.keys() :
		if param.get('initdb') == 0 :
			sql.queryDB (testDBParam,uf.droppgBenchTables(),'write')
			sql.queryDB (testDBParam,'vacuum','write')
			print ('Creating new pgbench tables')
			if pgversion >= 9.4  :
				subprocess.check_output(uf.utilfunc('testdb','PGBENCH',param) + ['-i','-s',str(scales.get(key)),'--foreign-keys'])
			else :
				subprocess.check_output(uf.utilfunc('testdb','PGBENCH',param) + ['-i','-s',str(scales.get(key))])

			# running the main test

		if pgversion >= 8.4  :
			for repeat in xrange(1,int(param['REPEATTIME']) + 1) :
				for client in param['CLIENTS'].split() :
					print("Running set {0:s} of {1:s} with {2:s} clients scale={3:s}".format(str(repeat), \
					str(param['REPEATTIME']),str(client),str(scales.get(key))))
					bw.runBenchwarmer(testset,repeat,scales.get(key),client,script,param)	
						
		else :
			print ("PostgreSQL version number not supported .... \n supported version >=8.4")
			sys.exit(0)

	tests.deleteFiles(param['TESTTYPE'] + '.sql')
	tests.deleteFiles('timing.csv')
	tests.deleteFiles('result.txt')
	tests.deleteFiles('*_log*')
	tests.deleteFiles('load.csv')
	tests.deleteFiles('disk_io_count.csv')
			## here is where you chart ur results


if __name__ == '__main__' :
	try :
		runMainTest()
	except Exception as err :
		print(err)
		sys.exit(0)
