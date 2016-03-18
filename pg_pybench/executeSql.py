#!/usr/bin/python
import psycopg2 as pg 

def queryDB (dbParam,query,operation) :
	dbname = dbParam['dbname']
	host = dbParam['host']
	user = dbParam['user']
	password = dbParam['password']
	port = dbParam['port']
	
	try :
		conn_str = "host={0:s} port={1:s} user={2:s} dbname={3:s} password={4:s}".format(host,str(port),user,dbname,password)
		conn = pg.connect (conn_str)
		cur = conn.cursor()

		cur.execute(query)
		
		
		if operation == 'read' :
			rows = cur.fetchall()
		else :
			rows = (0,)

		cur.close()
		conn.close()

		return [0 , rows ]
	except pg.Error as err : 
		return [None, str(err) ]
