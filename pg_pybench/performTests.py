#!/usr/bin/python

import utilfunc as uf
import subprocess
import glob,datetime
import cpu_load as cpu
import io_count as io
import os
import executeSql as sql

def runBenchwarmer (testset,repeat,scale,client,script,param,datadir,runtime,resultDBParam,thread,trans=None) : 
#	pgbench -t 1000 -T 6000 -M simple -l -j 4 -c 50 dbname
	queryMode = param.get('querymode')
	db = param.get('testdbname')
	delay = param.get('delay')
	
	# this will throw a huge error if thread is not a multiple of client, so we try to normilize that
	if int(client) % int(thread) != 0 : 
		client = str( int(thread) * ( int(client) / int(thread) ) )

	out = ''

	start_time  = str(datetime.datetime.now())  # might be a few milli or micro sec off, but it won't influence the results.
	end_time = ''

	# start saving the cpu load and the I/O count "--client",str(client)
	execdir = param.get('execdir')
	cpu_load = subprocess.Popen( ["python",execdir + os.sep + "cpu_load.py","--thread",str(thread),"--delay",str(delay),"--testset",str(testset),"--repeat",str(repeat),"--scale",str(scale),"--client",str(client) ] , stdout=subprocess.PIPE )
	io_count = subprocess.Popen( [ "python" , execdir + os.sep + "io_count.py" ,"--thread",str(thread),"--delay", str(delay),"--datadir" ,str(datadir),"--testset", str(testset), "--repeat",str(repeat),"--scale", str(scale),"--client",str(client)  ] , stdout=subprocess.PIPE )
	
	if trans == None :
		out = subprocess.check_output( uf.utilfunc('testdb','pgbench',param) + ['-M',str(queryMode),'-f',script,'-T',str(runtime),'-j',\
	 	str(thread),'-c',str(client),'-l','-s',str(scale),db] )
		end_time = str(datetime.datetime.now())
	elif trans != None and runtime == None :
		out = subprocess.check_output( uf.utilfunc('testdb','pgbench',param) + ['-M',queryMode,'-f',script,'-t',str(trans),'-j',\
                str(thread),'-c',str(client),'-l','-s',str(scale),db] )
		
		end_time = str(datetime.datetime.now())

	else :
		print ("Either the runtime or transaction/client must be specified ...")
		cpu_load.stdout.close()
        	cpu_load.terminate()
		io_count.stdout.close()
                io_count.terminate()
		sys.exit(1)


	cpu_load.stdout.close()
	cpu_load.terminate()
	io_count.stdout.close()
        io_count.terminate()
	
	f = open('result.txt','wb')
	f.write(out)
	f.close()

	r = open('result.txt','r')
	trans = ''
	tps = ''
	for lines in r : 
		if lines.startswith('number of transactions actually processed:') == True :
			trans = lines.split()[-1]
		elif lines.endswith('(including connections establishing)\n') == True :
			tps = lines.split()[2]

	r.close()
		

	test = sql.queryDB (resultDBParam,uf.insertTestResult( script,client,thread,scale,param.get('testdbname'),start_time.rstrip(),end_time.rstrip(),tps,trans  ),'read',1)

	if test[0] == 0 :
		for f in glob.glob('*_log*') :
                	uf.writeCSV(f,test[1][0])

		subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',uf.copyCSV(param.get('pwd'),'timing.csv',',','timing') ] )
		subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',uf.copyCSV(param.get('pwd'),'disk_io_count.csv',';','disk_io_count') ] )
		subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',uf.copyCSV(param.get('pwd'),'load.csv',';','load_average') ] )

	
		subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-tAc',uf.storeTestLatency(test[1][0]) ] )

		subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',uf.truncateTiming() ] )
	else : 
		print ("Test results could not be saves ")
		sys.exit(0)

