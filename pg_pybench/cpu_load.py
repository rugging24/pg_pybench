#!/usr/bin/python

import csv,os,time
import getopt

#'python','cpu_load.py','--delay','5','--testset',str(testset),'--repeat',str(repeat),'--scale',str(scale) ]

def getCPULoad(delay,testset,repeat,scale) :

	try :
		while True :
        		f = open('load.csv','ab')
        		cs = csv.writer(f,delimiter=',')
        		load = str( str(testset) + ',' + sr(repeat) + ',' + str(scale) + ','+ str(os.getloadavg()).replace('(','').replace(')','') ).split(',')
        		cs.writerow(load)
			f.close()
        		time.sleep(delay)

	except Exception as err :
		print (err) 
		sys.exit(0) 
