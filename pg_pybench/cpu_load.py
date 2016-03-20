#!/usr/bin/python

import csv,os,time

#'python','cpu_load.py','--delay','5','--testset',str(testset),'--repeat',str(repeat),'--scale',str(scale) ]

def getCPULoad(delay,testset,repeat,scale) :

	try :
		while True :
        		f = open('load.csv','ab')
        		cs = csv.writer(f,delimiter=',')
			cpu = os.getloadavg()
        		load = str( str(testset) + ',' + str(repeat) + ',' + str(scale) + ',' + str(cpu[0]) + ',' + str(cpu[1]) + ',' + str(cpu[2])  )
        		cs.writerow(load)
			f.close()
        		time.sleep(delay)

	except Exception as err :
		print (err) 
		sys.exit(0) 
