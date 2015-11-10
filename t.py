#!/usr/bin/python 
import subprocess

#DETACHED_PROCESS = 0x00000008

print ('before starting')

k = subprocess.Popen(['nohup','python','os_metrics.py'])

#k.communicate()

print ('after')


#DETACHED_PROCESS = 0x00000008

#print ('before starting')

#c = subprocess.Popen(['nohup',os_metrics.py], stderr=subprocess.PIPE) #,creationflags=DETACHED_PROCESS).pid
#c.communicate()
#print (c )
#print (c)
#c.communicate()

