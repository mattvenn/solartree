#!/usr/bin/env python
"""
todo:
"""

import datetime
import os
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import logging
import logging.handlers
import argparse
import fcntl

# configure the client logging
log = logging.getLogger('solartree')
# has to be set to debug as is the root logger
log.setLevel(logging.DEBUG)


# create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter for console
cf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(cf)
log.addHandler(ch)

# create syslog handler and set to debug
sh = logging.handlers.SysLogHandler(address = '/dev/log')
sh.setLevel(logging.DEBUG)

# create formatter for syslog
sf = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
sh.setFormatter(sf)
log.addHandler(sh)

from PachubeFeedUpdate import *

bad_data = 100 #current will never be this high

def get_data():

    # choose the serial client
    client = ModbusClient(method='rtu', port=args.tty, baudrate=9600, timeout=args.timeout)

    client.connect()
    log.debug(client)

    #read the registers
    rr = client.read_holding_registers(0,count=60,unit=1)
    if rr == None:
        client.close()
        log.error("couldn't connect")
        exit(1)

    #scaling
    v_scale = rr.registers[0] + rr.registers[1]/(2**16)
    i_scale = rr.registers[2] + rr.registers[3]/(2**16)

    #the stuff we want
    data={}
    data["arrayV" ] = ( rr.registers[27] * float(v_scale )) / (2**15)
    data["arrayI" ] = ( rr.registers[29] * float(i_scale )) / (2**15)
    data["battI" ] = ( rr.registers[28] * float(i_scale )) / (2**15)
    data["battV" ] = ( rr.registers[24] * float(v_scale )) / (2**15)
    data["battTemp" ] = rr.registers[37] 
    data["powerIn" ] = ( rr.registers[59] * float(v_scale)*float(i_scale)) / (2**17)

    # close the client
    client.close()

    #debug
    log.info(datetime.datetime.now())
    log.info("batt v: %.2f" % data["battV" ])
    log.info("batt i: %.2f" % data["battI" ])
    log.info("array v: %.2f" % data["arrayV" ])
    log.info("array i: %.2f" % data["arrayI" ])
    log.info("batt temp: %.2f" % data["battTemp" ])
    log.info("power in: %.2f" % data["powerIn" ])

    return data

def push_data(data):
    if data["arrayI"] > bad_data:
        log.error("bad data, not pushing")
        return

    #cosm parameters


    API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = args.feed)

    keyfile="/home/pi/solartree/cosm/api.key"
    key=open(keyfile).readlines()[0].strip()
    feed_id = "75479"

    f=open("/proc/uptime","r");
    uptime_string=f.readline()
    uptime=uptime_string.split()[0]

    pfu = PachubeFeedUpdate(feed_id,key)
    pfu.addDatapoint('uptime', uptime)
    pfu.addDatapoint("batt-voltage", data["battV"] )
    pfu.addDatapoint("batt-current", data["battI"] )
    pfu.addDatapoint("array-voltage", data["arrayV"] )
    pfu.addDatapoint("array-current", data["arrayI"] )
    pfu.addDatapoint("batt-temp", data["battTemp"])
    pfu.addDatapoint("power-in", data["powerIn"] )

    # finish up and submit the data
    pfu.buildUpdate()
    pfu.sendUpdate()
    log.info("pushed to cosm")


if __name__ == '__main__':
  argparser = argparse.ArgumentParser(
      description="fetches data via modbus and pushes to cosm")
  argparser.add_argument('--tty',
    action='store', dest='tty',
      help="which serial tty is the tristar on")
  argparser.add_argument('--keyfile',
    action='store', dest='keyfile', default="api.key",
      help="where the api key is stored")
  argparser.add_argument('--timeout',
    action='store', dest='timeout', type=int, default = 15, 
      help="serial timeout")
  argparser.add_argument('--feed',
    action='store', dest='feed', type=int, default = 75479, #default is for solar tree
      help="feed number")

  args = argparser.parse_args()

  #locking
  file = "/tmp/modbus.lock"
  fd = open(file,'w')
  try:
      log.debug("check lock")
      fcntl.lockf(fd,fcntl.LOCK_EX | fcntl.LOCK_NB)
      log.debug("ok")
  except IOError:
      log.error("another process is running with lock. quitting!")
      exit(1)

  if args.tty == None:
    os.system("dmesg | grep 'pl2303.*ttyUSB' > /tmp/tty")
    try:
        with open('/tmp/tty') as fh:
            line = fh.readline()
            args.tty = '/dev/ttyUSB' + line[-2]
            log.info("auto detected tty as %s" % args.tty)
    except IndexError as e:
        log.error("couldn't detect serial usb adapter")
        exit(1)
    

  log.info("using feed number %d" % args.feed)

  #load keyfile
  try:
    keyfile = open(args.keyfile)
    key = keyfile.read()
    key = key.strip()
    log.info("using key: %s" % key)
  except:
    log.error("couldn't open key file %s" % args.keyfile)
    exit(1)

  #fetch data
  data = get_data()

  #push data
  push_data(data)

  log.info("done")
