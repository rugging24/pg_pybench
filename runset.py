#!/usr/bin/python

import subprocess,sys
import utilfunc as uf
import benchwarmer as bw
import getTests as tests


if __name__ == "__main__" :
	param = uf.getConfParameters(sys.argv)
	
	
	if len(param) > 0 :
		script = tests.formulateTestQuery(param['TESTTYPE'])
		out = subprocess.call(uf.utilfunc('resultdb','psql',param) + ['-tAc',uf.checkResultDb(param['RESULTDB'])])
		print (out)
		if out != 0 :
			subprocess.check_output(uf.utilfunc('createdb','psql',param) + ['-tAc','CREATE DATABASE {0:s}'.format(param['RESULTDB'])])
			subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-f','resultdb.sql',param['RESULTDB']])		
		
	
		for scale in uf.getLevelScale() :
			out = subprocess.check_output(uf.utilfunc('testdb','psql',param) + ['-tAc',"select substring(version() from '(\d\.\d)')"])
			if param['INITDB'] == '0' :
				subprocess.check_output(uf.utilfunc('testdb','psql',param) + ['-c',uf.houseKeeping()])
				subprocess.check_output(uf.utilfunc('testdb','psql',param) + ['-c','vacuum'])
				print ('Creating new pgbench tables')
				if out >= 9.4  :
					subprocess.check_output(uf.utilfunc('testdb','pgbench',param) + ['-i','-s',str(scale),'--foreign-keys'])
				else :
					subprocess.check_output(uf.utilfunc('testdb','pgbench',param) + ['-i','-s',str(scale)])

			# running the main test
			subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',\
		                "insert into testset(info) values('{0:s}')".format( param['TESTTYPE'])] )

			if out >= 8.4  :
				for repeat in xrange(1,int(param['REPEATTIME']) + 1) :
					for client in param['CLIENTS'].split() :
						print("Run set {0:s} of {1:s} with {2:s} clients scale={3:s}".format(str(repeat), \
						str(param['REPEATTIME']),str(client),str(scale)))
						bw.runBenchwarmer(repeat,scale,client,script,param)	

			else :
				print ("PostgreSQL version number not supported .... \n supported version >=8.4")
				sys.exit(0)

		tests.deleteFiles(param['TESTTYPE'] + '.sql')
		tests.deleteFiles('timing.csv')
		tests.deleteFiles('result.txt')
		tests.deleteFiles('*_log*')
			## here is where you chart ur results
