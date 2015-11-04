#!/usr/bin/python

import os,sys,glob

def texts() :
	l0 = '\\set nbranches :scale'
	l1 = '\\set ntellers 10 * :scale'
	l2 = '\\set naccounts 100000 * :scale'
	l3 = '\\setrandom aid 1 :naccounts'
	l4 = '\\setrandom bid 1 :nbranches'
	l5 = '\\setrandom tid 1 :ntellers'
	l6 = '\\setrandom delta -5000 5000'
	l7 = 'BEGIN;'
	l8 = 'UPDATE pgbench_accounts SET abalance = abalance + :delta WHERE aid = :aid;'
	l9 = 'SELECT abalance FROM pgbench_accounts WHERE aid = :aid;'
	l10 = 'UPDATE pgbench_tellers SET tbalance = tbalance + :delta WHERE tid = :tid;'
	l11 = 'UPDATE pgbench_branches SET bbalance = bbalance + :delta WHERE bid = :bid;'
	l12 = 'INSERT INTO pgbench_history (tid, bid, aid, delta, mtime) VALUES (:tid, :bid, :aid, :delta, CURRENT_TIMESTAMP);'
	l13 = 'END;'

	return [l0,l1,l2,l3,l4,l5,l6,l7,l8,l9,l10,l11,l12,l13]

def writeTests(filename,lines) :
	f = open(filename,'wb')
	for l in lines :
		if l == lines[0] :
			f.write(l)
		else :
			f.write('\n' + l)

def deleteFiles(fpattern) :
	for f in glob.glob(fpattern) :
		os.remove(f)

def formulateTestQuery(testType) :
	fname = testType + '.sql'
	if testType == 'read' :
		l = texts()[2:4]
		l.append(texts()[9])
		writeTests(fname,l )	
	elif testType == 'write' : 
		l = texts()[0:6] 
		l.append(texts()[12])
	elif tesyType == 'update' :
		l = texts()[0:9] + texts()[10:12]
		l.append(texts()[13])
		writeTests(fname,l)
	elif testType == 'all' :
		writeTests(fname,texts()[0:])
	elif testType == 'custom' :
		fname = 'custom'
	return fname
