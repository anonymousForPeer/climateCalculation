#!/usr/bin/python

from time import process_time
t1= process_time()
import os
import utility.ensemble as en
from resource import getrusage, RUSAGE_SELF

path = os.environ['PATHNAME']
rcp = os.environ['RCP']
climdata=os.environ['CLIMDATA']
extra=os.environ['EXTRA']
iter=int(os.environ['K'])
stat=os.environ['STAT']


print('rcp'+rcp, flush=True)
print('iteration ' + str(iter), flush=True)
print(climdata, flush=True)


en.iterateThroughFiles(stat, rcp, extra, iter, path, climdata)


print(str(round((getrusage(RUSAGE_SELF).ru_maxrss)/1024, 2)) + ' MB RAM used')
t2= process_time()
print('Processing time in seconds: %f' % (t2-t1))
