#!/usr/bin/env python
import eeml

# parameters
API_KEY = 'lzH_J6nHkyOeB8MoJiZ5MK_QxOKSAKwxUGxVdU1UbitjUT0g'
FEED = 75479
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)

pac = eeml.Pachube(API_URL, API_KEY)
battV = 12
battI = 1
arrayV = 100
arrayI = 0.5

print "batt v: %.2f" % battV
print "batt i: %.2f" % battI
print "array v: %.2f" % arrayV
print "array i: %.2f" % arrayI

print "push to cosm"
pac.update([eeml.Data(0, battV)])
pac.update([eeml.Data(1, battI)])
pac.update([eeml.Data(2, arrayV)])
pac.update([eeml.Data(3, arrayI)])
pac.put()
print "done"
