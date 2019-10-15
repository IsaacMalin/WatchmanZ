#!/usr/bin/python3
import subprocess

arg_list = [ '/sbin/iwgetid', '-r' ]
args = ' '.join(arg_list)

proc = subprocess.Popen(arg_list, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)

(output, dummy) = proc.communicate()
output = output.replace('\n','')
output = output.replace('\r','')
print (output)
