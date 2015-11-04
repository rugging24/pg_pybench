
Introduction :
	The pgbench-tools was originally written by Greg Smith (yeah, the one and only in the PostgreSQL world) as a couple
        of shell script which makes it usable in Linux or nix systems.
        This version intends to create a cross platform pgbench test tool as well as adding a few more features. Testing is
        still being done, so please report any bug you may have found. And suggestions to improving the scripts are welcom.

Requirements:
	- postgresql v >= 8.4
	- pgbench (obviously) 
	- configobj module
	
	Install configobj module using pip or any other means you may prefer
	
		pip install configobj   

	- Ensure the user executing this script(s) has read/write access in the execution directory


Usage : 

        python runTest.py [options]
                

	Options : 

                 -h , --help                   displays the help options
                 -c , --conf                   used to pass the configuration file to the script
                 --query-mode                  for passing the query mode [simple|extended|prepared] default is simple
                 -t , --test-type              accpets values read|write|update|all|custom  . 
					       Default : read
                                               Use the custom value only if you are providing a custom sql script and are probably
                                               not using the pgbench default data set.
                 -f , --file                   the full path (with extension, usually .sql) of the custom sql file


Example :

	python runTest.py --query-mode extended -t all 


This will run the test using all the queries that make up the tpc-b benchmark test. See http://www.postgresql.org/docs/9.5/static/pgbench.html
for details.

To use a custom data set and script , you can specify the following :
	
	python runTest.py --query-mode extended -t custom -f /full/path/to/your/script.sql


Do not forget to set the INITDB parameter to 1 in the pgtest.conf file, else the script will attempt to drop the default pgbench_* tables and 
initialize the database with the new set using a default scale factor.


Credits :

	Greg Smith (see the shell scrip version at : https://github.com/gregs1104/pgbench-tools ) 
