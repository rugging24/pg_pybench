# pgbench_py

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
