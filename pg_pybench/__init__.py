#!/usr/bin/python
import pyBench as bench
import os, sys


def callFunctions(param) :
	try :
		dir_name = 'pg_pybench_results'
		os.mkdir(os.path.expanduser('~') + os.sep + dir_name )
		param.update ({'pwd' : os.path.expanduser('~') + os.sep + dir_name + os.sep})
		os.chdir(os.path.expanduser('~') + os.sep + dir_name )
		bench.runMainTest(param)
	except OSError err :
		print (err) 
		sys.exit(0) 
