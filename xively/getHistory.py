#!/usr/bin/python
import urllib
import urllib2
import datetime
import json
import iso8601
import dateutil.parser
import argparse

def fetchRange(start_date,end_date,key,feed_number):
    alldatapoints = {}
    per_page = 500 #seems limited to 500, tho docs say 1000
    url = 'http://api.cosm.com/v2/feeds/%d.json' % feed_number

    while start_date < end_date:
        page = 1
        while True:
            values = {
                      'start' : start_date.isoformat(),
                      'duration' : "6hours",
                      'interval' : 0, #once a minute. 0 is everything but can only get 6 hours at a time
                      'key' : key,
                      'per_page' : per_page,
                      'page' : page,
                      }

            data = urllib.urlencode(values)
            fullurl = url + '?' + data
            req = urllib2.Request(fullurl)
            print values

            response = None
            while response == None:
                try:
                    response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                    print e.code
                    print e.read()
                    print "trying again..."

            the_page = response.read()

            data = json.loads(the_page)
#            import pdb; pdb.set_trace()
            datapoints = 0
            try:
                for datastream in data["datastreams"]:
                  feed_id = datastream["id"]
                  #create key array if necessary
                  if not alldatapoints.has_key(feed_id):
                    alldatapoints[feed_id] = []
                  alldatapoints[feed_id] = alldatapoints[feed_id] + datastream["datapoints"]
                  datapoints += len(datastream["datapoints"])
#                alldatapoints = alldatapoints + datapoints

                print "got %d datapoints in %d streams" % (datapoints, len(data["datastreams"]) )
                page += 1

                if datapoints != per_page:
                    print "starting new request"
                    break;

            except KeyError:
                print "no data points for that period"
                break



#        last_date = dateutil.parser.parse(datapoints[len(datapoints)-1]["at"])
#        print "date of last datapoint %s" % last_date
        start_date = start_date + datetime.timedelta(hours=6)

    return alldatapoints

if __name__ == '__main__':
  argparser = argparse.ArgumentParser(
      description="fetches historical data from cosm")
  argparser.add_argument('--keyfile',
    action='store', dest='keyfile', default="api.key",
      help="where the api key is stored")
  argparser.add_argument('--feed',
    action='store', dest='feed', type=int, default = 75479, #default is for solar tree
      help="feed number")
  argparser.add_argument('--start',
    action='store', dest='start',
      help="start date")
  argparser.add_argument('--end',
      action='store', dest='end',
      help="end date")

  args = argparser.parse_args()

  print "using feed number", args.feed

  #load keyfile
  try:
    keyfile = open(args.keyfile)
    key = keyfile.read()
    key = key.strip()
    print "using key: ", key
  except:
    print "couldn't open key file", args.keyfile
    exit(1)

  #check dates
  if not ( args.start and args.end ):
    print "must provide start and end date"
    exit(1)

  #parse dates
  start_date = dateutil.parser.parse(args.start,dayfirst=True)
  end_date = dateutil.parser.parse(args.end,dayfirst=True)

  #fetch data
  data = fetchRange(start_date,end_date,key,args.feed)

  #make a summary
  for key in data.keys():
    print "got %d points in feed %s" % ( len(data[key]), key )
  
  savefh=open("history.json","w")
  json.dump(data,savefh)
