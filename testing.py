#!/usr/bin/python 

import os,sys,subprocess
import os_metrics as mets


c = subprocess.Popen( os.getloadavg(), stderr=subprocess.PIPE)

#print (str(c.pid) )
print (c)
#c.communicate()
