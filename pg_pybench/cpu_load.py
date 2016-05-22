#!/usr/bin/python

import csv,os,time

def getCPULoad(delay,testset,repeat,scale) :

	try :
		f = open('load.csv','ab')
		cs = csv.writer(f,delimiter=';')
		while True :
			cpu = os.getloadavg()
        		load = str(testset) + ';' + str(repeat) + ';' + str(scale) + ';' + str(cpu[0]) + ';' + str(cpu[1]) + ';' + str(cpu[2])  
        		cs.writerow(load.split(';'))
			time.sleep(delay)

		f.close()
	except Exception as err :
		print (err) 
		sys.exit(0) 
