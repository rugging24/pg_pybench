#!/usr/bin/python
import pyBench as bench
import os, sys


def callFunctions(param) :
	try :
		dir_name = 'pg_pybench_results'
		execdir = os.getcwd()
		if os.path.isdir(os.path.expanduser('~') + os.sep + dir_name) == False :
			os.mkdir(os.path.expanduser('~') + os.sep + dir_name )
		param.update ({'pwd' : os.path.expanduser('~') + os.sep + dir_name + os.sep})
		param.update ({'execdir' : execdir})
		os.chdir(os.path.expanduser('~') + os.sep + dir_name )
		bench.runMainTest(param)
	except OSError as err :
		print (err) 
		sys.exit(0) 
