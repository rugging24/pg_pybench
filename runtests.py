#!/usr/bin/python

import utilfunc as uf
import subprocess
import glob

def runBenchwarmer (repeat,scale,client,script,param) : 
#	pgbench -t 1000 -T 6000 -M simple -l -j 4 -c 50 dbname
	queryMode = param['QUERYMODE']
	runtime = param['RUNTIME']
	trans = param['TRANSACTIONS']
	thread = param['THREADCOUNT']
	db = param['TESTDB']
	script = script if param['CUSTOMFILE'] == None or param['CUSTOMFILE'] == '' else param['CUSTOMFILE']

	out = ''

	start  = subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-tAc',"select  clock_timestamp()::timestamp from testset limit 1"])


	if runtime != '' and runtime != None :
		out = subprocess.check_output(uf.utilfunc('testdb','pgbench',param) + ['-M',queryMode,'-f',script,'-T',runtime,'-j',\
	 	thread,'-c',client,'-l','-s',str(scale),db])
	elif trans != '' and trans != None and ( runtime == '' or runtime == None ) :
		out = subprocess.check_output(uf.utilfunc('testdb','pgbench',param) + ['-M',queryMode,'-f',script,'-t',trans,'-j',\
                thread,'-c',client,'-l','-s',str(scale),db])

	else :
		print ("Either the runtime or transaction/client must be specified ...")
		sys.exit(1)

	f = open('result.txt','wb')
	f.write(out)
	f.close()

	r = open('result.txt','r')
	trans = ''
	tps = ''
	for lines in r : 
		if lines.startswith('number of transactions actually processed:') == True :
			trans = lines.split()[-1]
			print(trans)
		elif lines.endswith('(including connections establishing)\n') == True :
			cols = lines.split()
			tps = cols[2]
			print (tps)
	r.close()
		
	test = subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-tAc',\
		"insert into tests(script,clients,workers,set,scale,dbsize,start_time,end_time,tps,trans) \
		select '{0:s}','{1:s}','{2:s}',max(set),'{3:s}',pg_database_size('{4:s}'),'{5:s}',now(),{6:s},{7:s} from testset"\
		" returning test"
               .format( script,str(client),str(thread),str(scale),param['RESULTDB'],str(start.rstrip()),str(tps),str(trans)  )] )


	for f in glob.glob('*_log*') :
                uf.writeCSV(f,test.split("\n")[0])

	subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c',
                " copy timing from '{0:s}' with csv ".format(param['BASEDIR'] + '/timing.csv') ] )

	
	test = subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-tAc',\
                "update tests set avg_latency=(select avg(latency) from \
                 timing where tests.test=timing.test), max_latency=(select max(latency)from \
                 timing where tests.test=timing.test), percentile_90_latency=(select latency \
                 from timing where tests.test=timing.test \
                 order by latency offset (round(0.90*trans)) limit 1) where tests.test='{0:s}'".format(test.split("\n")[0])   ] )

	subprocess.check_output(uf.utilfunc('resultdb','psql',param) + ['-c'," truncate table timing  " ] )

