import datetime

f = open('/tmp/viri.res', 'w')
f.write('%s\n' % datetime.datetime.now())
f.close()

