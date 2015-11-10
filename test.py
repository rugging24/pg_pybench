#!/usr/bin/python

import subprocess
import os,time
#output=`dmesg | grep hda`
# becomes
p1 = subprocess.Popen(['python','os_metrics.py'], stdout=subprocess.PIPE)
for x in xrange(1,10) :
	print (x)
	time.sleep(2)

print ('before out close')

p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
print ('terminating')
p1.terminate()
print ('end of subs')
