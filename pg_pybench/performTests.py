#!/usr/bin/python

import utilfunc as uf
import subprocess
import glob,datetime
import cpu_load as cpu
import io_count as io

def runBenchwarmer (testset,repeat,scale,client,script,param,datadir,trans=None,runtime) : 
#	pgbench -t 1000 -T 6000 -M simple -l -j 4 -c 50 dbname
	queryMode = param.get('querymode')
	thread = param.get('threadcount')
	db = param.get('testdbname')
	
	# this will throw a huge error if thread is not a multiple of client, so we try to normilize that
	if int(client) % int(thread) != 0 : 
		client = str( int(thread) * ( int(client) / int(thread) ) )

	out = ''

	start_time  = str(datetime.datetime.now())  # might be a few milli or micro sec off, but it won't influence the results.
	end_time = ''

	# start saving the cpu load and the I/O count 
	cpu_load = subprocess.Popen( [ cpu.(5,str(testset),str(repeat),str(scale)) ] , stdout=subprocess.PIPE )
	io_count = subprocess.Popen( [ io.getIOCount(5, datadir, str(testset), str(repeat), str(scale)) ] , stdout=subprocess.PIPE )

	if trans == None :
		out = subprocess.check_output( uf.utilfunc('testdb','pgbench',param) + ['-M',queryMode,'-f',script,'-T',runtime,'-j',\
	 	thread,'-c',client,'-l','-s',str(scale),db] )

		end_time = str(datetime.datetime.now())
	elif  :
		out = subprocess.check_output( uf.utilfunc('testdb','pgbench',param) + ['-M',queryMode,'-f',script,'-t',trans,'-j',\
                thread,'-c',client,'-l','-s',str(scale),db] )
		
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
		
	test = subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-tAc',\
               uf.insertTestResult( script,client,thread,scale,param.get('testdbname'),start_time.rstrip(),end_time.rstrip(),tps,trans  )] )


	for f in glob.glob('*_log*') :
                uf.writeCSV(f,test.split("\n")[0])

	#subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',uf.copyCSV(param.get('pwd'),'timing.csv') ] )
	#subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',uf.copyCSV(param.get('pwd'),'disk_io_count.csv') ] )
	#subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',uf.copyCSV(param.get('pwd'),'disk_io_count.csv') ] )

	
	#subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-tAc',uf.storeTestLatency(test) ] )

	#subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',uf.truncateTiming() ] )

