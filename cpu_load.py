#!/usr/bin/python

import csv,os,time

while True :
	f = open('load.csv','ab')
	cs = csv.writer(f,delimiter=',')
	load = str(os.getloadavg()).replace('(','').replace(')','').split(',')
	cs.writerow(load)
	time.sleep(3)
	f.close()

