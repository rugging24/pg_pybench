#!/usr/bin/python
import sys
import os
import psutil
import pyudev
import csv
import time
import argparse


def getIOCount (delay, datadir, testset, repeat, scale,client,thread) :
	if datadir != '' and testset != '' and repeat != '' and scale != '' :
        	deviceNumber = os.stat(datadir).st_dev
                deviceNode = ''
                context = pyudev.Context()
                for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
                	if deviceNumber == device.device_number :
                        	deviceNode = device.device_node

        	try :
                	while True :
				f = open('disk_io_count.csv','ab')
				cs = csv.writer(f,delimiter=';')
                                io = psutil.disk_io_counters(perdisk=True)
                                for node in io.keys() :
                                        if deviceNode.find(node) != -1 :
                                                io = io[node]
                                                ioCount = str(testset) + ',' + str(repeat) + ',' + str(scale) + ',' + str(client) + ',' + str(thread) + ',' + \
                                                        str( io.write_count ) + ',' + \
                                                        str( io.read_count ) + ',' + \
                                                        str( io.write_bytes ) + ',' + \
                                                        str( io.read_bytes ) + ',' + \
                                                        str( io.write_time ) + ',' + \
                                                        str( io.read_time ) 
                                cs.writerow(ioCount.split(','))
                                time.sleep(delay)
				f.close()
        	except Exception as err :
                	print (err)
                	sys.exit(0)


	else :
		print ('invalid parameter(s) passed. This script will now exit ..')
		sys.exit(0)	

if __name__ == '__main__' :
        parser = argparse.ArgumentParser(prog='migrate', description ='migrate data')
        parser.add_argument ('--delay', type=int, required=True)
        parser.add_argument ('--datadir', type=str, required=True)
        parser.add_argument ('--testset', type=int, required=True)
        parser.add_argument ('--repeat', type=int, required=True)
	parser.add_argument ('--scale', type=int, required=True)
	parser.add_argument ('--client', type=int, required=True)
	parser.add_argument ('--thread', type=int, required=True)
        args = parser.parse_args()
	getIOCount (args.delay, args.datadir, args.testset, args.repeat, args.scale,args.client,args.thread)
