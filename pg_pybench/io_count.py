#!/usr/bin/python
import sys
import os
import psutil
import pyudev
import csv
import time


def getIOCount (delay, datadir, testset, repeat, scale) :
	if dataDir != '' and testset != '' and repeat != '' and scale != '' :
        	deviceNumber = os.stat(dataDir).st_dev
                deviceNode = ''
                context = pyudev.Context()
                for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
                	if deviceNumber == device.device_number :
                        	deviceNode = device.device_node

        	try :
			f = open('disk_io_count.csv','ab')
			cs = csv.writer(f,delimiter=';')
                	while True :
                                io = psutil.disk_io_counters(perdisk=True)
                                for node in io.keys() :
                                        if deviceNode.find(node) != -1 :
                                                io = io[node]
                                                ioCount = str(testset) + ',' + str(repeat) + ',' + str(scale) + ',' + \
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
