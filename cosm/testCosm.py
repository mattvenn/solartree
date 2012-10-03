#!/usr/bin/env python
import eeml

# parameters
API_KEY = 'lzH_J6nHkyOeB8MoJiZ5MK_QxOKSAKwxUGxVdU1UbitjUT0g'
FEED = 75479
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)

pac = eeml.Pachube(API_URL, API_KEY)
battV = 12


print "push to cosm"
pac.update([eeml.Data("batt v", battV)])
pac.put()
print "done"
