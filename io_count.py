#!/usr/bin/python
import sys
import os
import psutil
import getopt
import pyudev
import csv
import time


dataDir = ''
testset = ''
repeat = ''
scale = ''
delay = 5
try :
	options,v = getopt.getopt(sys.argv[1:],'h',['datadir=','testset=','repeat=','scale=','delay='])
	for opt,val in options : 
		if opt == '--datadir' :
			dataDir = val
		elif opt == '--testset' :
			testset = val 
		elif opt == '--repeat' :
			repeat = val 
		elif opt == '--scale' :
			scale = val
		elif opt == '--delay' :
			print val
			delay = int(val)
	if dataDir != '' and testset != '' and repeat != '' and scale != '' :
		deviceNumber = os.stat(dataDir).st_dev
        	deviceNode = ''
        	context = pyudev.Context()
        	for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
                	if deviceNumber == device.device_number :
                        	deviceNode = device.device_node

		while True :
                	f = open('disk_io_count.csv','ab')
                	cs = csv.writer(f,delimiter=',')
			io = psutil.disk_io_counters(perdisk=True)
			ioCount= ''
			for key in io.keys() :
				if key in deviceNode :
                			ioCount = str( \
						str(testset) + ',' + str(repeat) + ',' + str(scale) + ',' + \
						str( io.get(key).write_count ) + ',' + \
						str( io.get(key).read_count ) + ',' + \
						str( io.get(key).write_bytes ) + ',' + \
						str( io.get(key).read_bytes ) + ',' + \
						str( io.get(key).write_time ) + ',' + \
						str( io.get(key).read_time )
						).split(',')
        		cs.writerow(ioCount)
                	f.close()
                	time.sleep(delay)
	else :
		print ('invalid parameter(s) passed. This script will now exit ..')
		sys.exit(0)  

except getopt.GetoptError as err :
	print (err) 
	sys.exit(0) 
