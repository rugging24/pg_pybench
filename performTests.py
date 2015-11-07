#!/usr/bin/python

import utilfunc as uf
import subprocess
import glob,datetime
import os_metrics as mets

def runBenchwarmer (repeat,scale,client,script,param) : 
#	pgbench -t 1000 -T 6000 -M simple -l -j 4 -c 50 dbname
	queryMode = param['QUERYMODE']
	runtime = param['RUNTIME']
	trans = param['TRANSACTIONS']
	thread = param['THREADCOUNT']
	db = param['TESTDB']
	
	# this will throw a huge error if thread is not a multiple of client, so we try to normilize that
	if int(client) % int(thread) != 0 : 
		client = str( int(thread) * ( int(client) / int(thread) ) )

	out = ''

	start_time  = str(datetime.datetime.now())  # might be a few milli or micro sec off, but it won't influence the results.
	end_time = ''

	cpu_load = open('','wb')

	cpu_load_proc = subprocess.Popen( [ mets.getLoadAverage(5) ] , stdout=subprocess.PIPE,stderr=subprocess.PIPE )
	if runtime != '' and runtime != None :
		out = subprocess.check_output( uf.utilfunc('testdb','PGBENCH',param) + ['-M',queryMode,'-f',script,'-T',runtime,'-j',\
	 	thread,'-c',client,'-l','-s',str(scale),db] )

		end_time = str(datetime.datetime.now())
	elif trans != '' and trans != None and ( runtime == '' or runtime == None ) :
		out = subprocess.check_output( uf.utilfunc('testdb','PGBENCH',param) + ['-M',queryMode,'-f',script,'-t',trans,'-j',\
                thread,'-c',client,'-l','-s',str(scale),db] )
		
		end_time = str(datetime.datetime.now())

	else :
		print ("Either the runtime or transaction/client must be specified ...")
		sys.exit(1)


	
	f = open('result.txt','wb')
	f.write(out)
	f.close()

	print (out) 

	r = open('result.txt','r')
	trans = ''
	tps = ''
	for lines in r : 
		if lines.startswith('number of transactions actually processed:') == True :
			trans = lines.split()[-1]
		elif lines.endswith('(including connections establishing)\n') == True :
			tps = lines.split()[2]

	r.close()
		
	test = subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-tAc',\
               uf.insertTestResult( script,client,thread,scale,param['TESTDB'],start_time.rstrip(),end_time.rstrip(),tps,trans  )] )


	for f in glob.glob('*_log*') :
                uf.writeCSV(f,test.split("\n")[0])

	subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-c',uf.copyTimingCSV(param['BASEDIR']) ] )

	
	subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-tAc',uf.storeTestLatency(test) ] )

	subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-c',uf.truncateTiming() ] )

