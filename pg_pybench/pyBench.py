#!/usr/bin/python

import subprocess,sys,os
import utilfunc as uf
import performTests as bw
import formTestQuery as tests
import initdbSql as init
import executeSql as sql


def runMainTest(param) :

	# SQL connection parameters for the test and result databases 
	result_tblspc = param.get('resulttablespaces')
	test_tblspc = param.get('testtablespaces') 
	resultDBParam = {'dbname' : param.get('resultdbname'), 'host' : param.get('resulthost'), 'port' : param.get('resultport'),'user' : param.get('resultuser') ,\
                 'password' : param.get('resultuserpassword')}

	testDBParam = {'dbname' : param.get('testdbname'), 'host' : param.get('testhost'), 'port' : param.get('testport'),'user' : param.get('testuser') ,\
                 'password' : param.get('testuserpassword')}


	script = tests.formulateTestQuery(param['testtype']) if param['testtype'] != 'custom' else param.get('customfile')
	resultDBParam.update( {'dbname' : 'postgres'} )
	resultDBExists = sql.queryDB (resultDBParam,uf.checkDBExist(param.get('resultdbname')) ,'read',1)[1]

	if resultDBExists == None :
		sql.queryDB (resultDBParam,uf.createDBText(param.get('resultdbname'),result_tblspc) ,'write',2,1)
		resultDBParam.update( {'dbname' : param.get('resultdbname') })
		result = sql.queryDB (resultDBParam,init.getInitdbText() ,'write')
		if result[0] != 0 : 
			print ('Could not create resultdb objects')
			sys.exit(0)		
	else :	
		resultDBParam.update( {'dbname' : param.get('resultdbname') })

	
	# obtain disk mount points 
	devices = param.get('testtablespaces')
	threads = param.get('threadcount')
	
	for tblspace in devices :
		testDBParam.update( { 'dbname' : 'postgres'} )
                sql.queryDB (testDBParam,uf.dropDBText(param.get('testdbname')) ,'write',2,1)

		if tblspace != 'pg_default' :
			sql.queryDB (testDBParam,uf.dropTableSpaceText()  ,'write',2,1)
			sql.queryDB (testDBParam,uf.createTableSpaceText(tblspace)  ,'write')
			dataDirLocation = tblspace
		else :
			dataDirLocation = uf.getCurrentDBSetting(testDBParam,'data_directory')[0]

		sql.queryDB (testDBParam,uf.createDBText(param.get('testdbname'),tblspace),'write',2,1)
		testDBParam.update( {'dbname' : param.get('testdbname')} )

		pgversion = uf.getDBVersion(testDBParam)

		# create the main test entry
		sysinfo = sql.queryDB (testDBParam,uf.getSysInfo(pgversion),'read',1)
        	testset = sql.queryDB (resultDBParam,uf.insertNewTest(pgversion,sysinfo[1][0],dataDirLocation),'read',1)[1][0]

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
				trans = param.get('transaction')
				if trans != None  :
					for trans in param.get('transactions') :
						testComponents(param.get('repeattime'), param.get('clients') , testset,scales.get(key),script,param,dataDirLocation,runtime,resultDBParam,threads,trans)
				else :
					testComponents(param.get('repeattime'), param.get('clients') , testset,scales.get(key),script,param,dataDirLocation,runtime,resultDBParam,threads)
						
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


def testComponents(repeattime, clients , testset,scale,script,param,dataDirLocation,runtime,resultDBParam,threads,trans=None) :
	for client in clients :
		for thread in threads :
			for repeat in xrange(1,int(repeattime) + 1) :	
                		print("Running set {0:s} of {1:s} with {2:s} clients scale={3:s} and thread {4:s}".format(str(repeat), \
                        	str(repeattime),str(client),str(scale),str(thread) ))
                        	bw.runBenchwarmer(testset,repeat,scale,client,script,param,dataDirLocation,runtime,resultDBParam,thread,trans)



if __name__ == '__main__' :
	try :
		runBenchmark()
	except Exception as err :
		print(err)
		sys.exit(0)
