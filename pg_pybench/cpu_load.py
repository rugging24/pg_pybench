#!/usr/bin/python

import csv,os,time
import argparse

def getCPULoad(delay,testset,repeat,scale,client,thread) :
	try :
		while True :
			f = open('load.csv','ab')
			cs = csv.writer(f,delimiter=';')
			cpu = os.getloadavg()
        		load = str(testset) + ';' + str(repeat) + ';' + str(scale) + ';' + str(client) + ';' + str(thread) + ';' + str(cpu[0]) + ';' + str(cpu[1]) + ';' + str(cpu[2])  
        		cs.writerow(load.split(';'))
			time.sleep(delay)
			f.close()
	except Exception as err :
		print (err) 
		sys.exit(1) 

if __name__ == '__main__' :
	parser = argparse.ArgumentParser(prog='cpu_load', description ='cpu load')
        parser.add_argument ('--delay', type=int, required=True)
	parser.add_argument ('--testset', type=int, required=True)
	parser.add_argument ('--repeat', type=int, required=True)
        parser.add_argument ('--scale', type=int, required=True)
	parser.add_argument ('--client', type=int, required=True)
	parser.add_argument ('--thread', type=int, required=True)
        args = parser.parse_args()
	getCPULoad(args.delay,args.testset,args.repeat,args.scale,args.client,args.thread)
