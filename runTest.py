#!/usr/bin/python

import subprocess,sys
import utilfunc as uf
import performTests as bw
import formTestQuery as tests


def runMainTest() :
	param = uf.getConfParameters(sys.argv)
	
	if len(param) > 0 :
		pgversion = getDBVersion()
		tbsLocation = getTablespaceLocation(pgversion,param['TESTTABLESPACE']) 

		script = tests.formulateTestQuery(param['TESTTYPE']) if param['TESTTYPE'] != 'custom' else param['CUSTOMFILE']
		resultDBExists = subprocess.call(uf.utilfunc('resultdb','PSQL',param) + ['-tAc',uf.checkResultDb(param['RESULTDB'])])

		if resultDBExists != 0 :
			subprocess.check_output(uf.utilfunc('createdb','PSQL',param) + ['-tAc',uf.createResultDb(param['RESULTDB'])])
			subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-f','initdb.sql',param['RESULTDB']])		

		# create the main test entry 
		sysinfo = subprocess.check_output(uf.utilfunc('testdb','PSQL',param) + ['-tAc',uf.getSysInfo()] )
		testset = subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-c',uf.insertNewTest(sysinfo,tbsLocation)] )

		# if a custom script is used, set scale to 1
		scales = uf.getLevelScale(param['TESTTYPE'])
		for key in scales.keys() :
			if param['INITDB'] == '0' :
				subprocess.check_output(uf.utilfunc('testdb','PSQL',param) + ['-c',uf.houseKeeping()])
				subprocess.check_output(uf.utilfunc('testdb','PSQL',param) + ['-c','vacuum'])
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
			## here is where you chart ur results


if __name__ == '__main__' :
	try :
		runMainTest()
	except Exception as err :
		print(err)
		sys.exit(0)
