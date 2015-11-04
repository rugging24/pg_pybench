#!/usr/bin/python

import utilfunc as uf
import subprocess
import glob,datetime

def runBenchwarmer (repeat,scale,client,script,param) : 
#	pgbench -t 1000 -T 6000 -M simple -l -j 4 -c 50 dbname
	queryMode = param['QUERYMODE']
	runtime = param['RUNTIME']
	trans = param['TRANSACTIONS']
	thread = param['THREADCOUNT']
	db = param['TESTDB']

	out = ''

	start  = str(datetime.datetime.now())


	if runtime != '' and runtime != None :
		out = subprocess.check_output(uf.utilfunc('testdb','PGBENCH',param) + ['-M',queryMode,'-f',script,'-T',runtime,'-j',\
	 	thread,'-c',client,'-l','-s',str(scale),db])
	elif trans != '' and trans != None and ( runtime == '' or runtime == None ) :
		out = subprocess.check_output(uf.utilfunc('testdb','PGBENCH',param) + ['-M',queryMode,'-f',script,'-t',trans,'-j',\
                thread,'-c',client,'-l','-s',str(scale),db])

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
			cols = lines.split()
			tps = cols[2]
	r.close()
		
	test = subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-tAc',\
               uf.insertTestResult( script,client,thread,scale,param['RESULTDB'],start.rstrip(),tps,trans  )] )


	for f in glob.glob('*_log*') :
                uf.writeCSV(f,test.split("\n")[0])

	subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-c',uf.copyTimingCSV(param['BASEDIR']) ] )

	
	subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-tAc',uf.storeTestLatency(test) ] )

	subprocess.check_output(uf.utilfunc('resultdb','PSQL',param) + ['-c',uf.truncateTiming() ] )

