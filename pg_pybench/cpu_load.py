#!/usr/bin/python

import csv,os,time
import getopt

#'python','cpu_load.py','--delay','5','--testset',str(testset),'--repeat',str(repeat),'--scale',str(scale) ]

delay = 5
try :
	options,s = getopt.getopt(sys.argv[1:],'h',['delay=','testset=','repeat=','scale='])
	for opt,val in options :
		if opt == '--delay':
			delay = val
		elif opt == '--testset' :
			testset = val 
		elif opt == '--repeat' :
			repeat = val 
		elif opt = '--scale' :
			scale = val

	while True :
        	f = open('load.csv','ab')
        	cs = csv.writer(f,delimiter=',')
        	load = str( str(testset) + ',' + sr(repeat) + ',' + str(scale) + ','+ str(os.getloadavg()).replace('(','').replace(')','') ).split(',')
        	cs.writerow(load)
		f.close()
        	time.sleep(delay)

except getopt.GetoptError as err :
	print (err) 
	sys.exit(0) 
