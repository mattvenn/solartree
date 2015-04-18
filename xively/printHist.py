#!/usr/bin/python
import json
fh=open("history.json")
d=json.load(fh)


#print header
print "time,",
for key in d.keys():
  print "%s," % (key),
print

first_key = d.keys()[0]
datapoints = len(d[first_key])

for line in range(0, datapoints):
  print "%s," % d[first_key][line]["at"],
  for key in d.keys():
    print "%s," % d[key][line]["value"],
  print
