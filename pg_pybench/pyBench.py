#!/usr/bin/python

import subprocess,sys,os
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


	script = tests.formulateTestQuery(param['testtype']) if param['testtype'] != 'custom' else param.get('customfile')
	resultDBParam.update( 'dbname' : 'postgres' )
	resultDBExists = sql.queryDB (resultDBParam,uf.checkDBExist(param.get('resultdbname')) ,'read')[0][1]

	if resultDBExists != param.get('resultdbname') :
		sql.queryDB (resultDBParam,uf.createDBText(param.get('resultdbname')) ,'write')
		resultDBParam.update( 'dbname' : param.get('resultdbname') )
		result = sql.queryDB (resultDBParam,init.getInitdbText() ,'write')[0][1]
		if result != 0 : 
			print ('Could not create resultdb objects')
			sys.exit(0)		
	else :	
		resultDBParam.update( 'dbname' : param.get('resultdbname') )

	
	# obtain disk mount points 
	devices = param.get('tablespaces')
	

	for tblspace in devices :
		testDBParam.update( 'dbname' : 'postgres' )
                sql.queryDB (testDBParam,uf.dropDBText(param.get('testdbname')) ,'write')
		sql.queryDB (testDBParam,uf.dropTableSpaceText()  ,'write')
		sql.queryDB (testDBParam,uf.createTableSpaceText(tblspace)  ,'write')
		sql.queryDB (testDBParam,uf.createDBText(param.get('testdbname')) + ' TABLESPACE ' + tblspace ,'write')
		testDBParam.update( 'dbname' : param.get('testdbname') )

		pgversion = uf.getDBVersion(testDBParam)
		dataDirLocation = tblspace
		if tblspace == 'pg_default' :
			dataDirLocation = uf.getCurrentDBSetting(testDBParam,'data_directory')

		# create the main test entry
		sysinfo = sql.queryDB (testDBParam,uf.getSysInfo(pgversion),'read')
        	testset = sql.queryDB (resultDBParam,uf.insertNewTest(pgversion,sysinfo,dataDirLocation),'read')

		# if a custom script is used, set scale to 1
        	scales = uf.getLevelScale( param.get('testtype') )

		for key in scales.keys() :
			if param.get('initdb') == 0 :
				sql.queryDB (testDBParam,uf.droppgBenchTables(),'write')
				sql.queryDB (testDBParam,'VACUUM FULL','write')
				print ('Creating new pgbench tables')
				if pgversion >= 9.4  :
					subprocess.check_output(uf.utilfunc('testdb','pgbench',param) + ['-i','-s',str(scales.get(key)),'--foreign-keys'])
				else :
					subprocess.check_output(uf.utilfunc('testdb','pgbench',param) + ['-i','-s',str(scales.get(key))])

				# running the main test

			if pgversion >= 8.4  :
				runtime = param.get('runtime')
				if trans != None  :
					for trans in param.get('transactions') :
						testComponents(param.get('repeattime'), param.get('clients') , testset,scales.get(key),script,param,dataDirLocation,trans,runtime)
				else :
					testComponents(param.get('repeattime'), param.get('clients') , testset,scales.get(key),script,param,dataDirLocation,runtime)
						
			else :
				print ("PostgreSQL version number not supported .... \n supported version >=8.4")
				sys.exit(0)

		tests.deleteFiles(param['testtype'] + '.sql')
		tests.deleteFiles('timing.csv')
		tests.deleteFiles('result.txt')
		tests.deleteFiles('*_log*')
		tests.deleteFiles('load.csv')
		tests.deleteFiles('disk_io_count.csv')
			## here is where you chart ur results


def testComponents(repeattime, clients , testset,scale,script,param,dataDirLocation,trans=None,runtime) :
	for repeat in xrange(1,int(repeattime) + 1) :
        	for client in clients :
                	print("Running set {0:s} of {1:s} with {2:s} clients scale={3:s}".format(str(repeat), \
                        str(repeattime),str(client),str(scale)))
                        bw.runBenchwarmer(testset,repeat,scale,client,script,param,dataDirLocation,trans,runtime)



if __name__ == '__main__' :
	try :
		runMainTest()
	except Exception as err :
		print(err)
		sys.exit(0)
