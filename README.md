# pgbench_py

# This is written for mostly  Windows and has been tested on Linux (ubuntu) as Well.
# The linux version could be found here : 
#  https://github.com/gregs1104/pgbench-tools

-- This uses configobj module to read the config file

=====Requirements=====
- postgresql v >= 8.4
- pgbench (obviously) 
- configobj module
	pip install configobj
- gnuplot (required for plotting the results)

- Ensure the user executing this script(s) has read/write access in the execution directory


======= Query Mode ==========

- Simple
- Select 

================= Usage ======================

python runset.py -c|--conf pgbench.conf [--query-mode simple|extended|prepared] --test-type read|write|update|all
-


-- More features to follow soon :) 
