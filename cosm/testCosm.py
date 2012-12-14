#!/usr/bin/env python
import eeml
import time

# parameters
API_KEY = 'lzH_J6nHkyOeB8MoJiZ5MK_QxOKSAKwxUGxVdU1UbitjUT0g'
FEED = 75479
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)


f=open("/proc/uptime","r");
uptime_string=f.readline()
uptime=uptime_string.split()[0]
pac = eeml.Pachube(API_URL, API_KEY)
print "push to cosm: update=%s" % uptime
pac.update([eeml.Data("update", uptime)])
pac.put()
print "done"
