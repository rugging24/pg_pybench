
Introduction :
	The pgbench-tools was originally written by Greg Smith as a couple of shell scripts for Linux and Unix systems.
        This version intends to create a cross platform pgbench test tool as well as adding a few more features. Testing is
        still being done, so please report any bug as well as suggestions or request a new feature you may want.
	(Use the email address below to leave a note !)

Requirements:
	- postgresql v >= 8.4
	- postgresql-contrib 
	- python v >= 2.7
	- python-dev
	- configobj module
	- psutil python module (https://pypi.python.org/pypi/psutil)
	- pyudev (https://pyudev.readthedocs.org/en/latest/)
	
	Install configobj module using pip or any other means you may prefer
	
		pip install configobj   
		(don't forget the sudo in Linux systems , and in Windos, run as an admin)

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

Contact :
	You can send you bug report or feature request to :
	rugging24@gmail.com

Credits :
	Greg Smith (https://github.com/gregs1104/pgbench-tools ) wrote the orginal version in shell scripts
	 
