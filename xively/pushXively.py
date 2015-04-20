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
from xively import xively
from post_data import cursive_data

keys = [ "batt-voltage", "batt-current", "array-voltage", "array-current", "batt-temp", "power-in", "power-out" ]



# configure the client logging
log = logging.getLogger('xively')
# has to be set to debug as is the root logger
log.setLevel(logging.DEBUG)


# create console handler and set level to info
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter for console
cf = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(cf)
log.addHandler(ch)

# create syslog handler and set to debug
sh = logging.handlers.SysLogHandler(address = '/dev/log')
sh.setLevel(logging.INFO)

# create formatter for syslog
sf = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
sh.setFormatter(sf)
log.addHandler(sh)


bad_data = 100 #current will never be this high

def get_data():
    # choose the serial client
    client = ModbusClient(method='rtu', port=args.tty, baudrate=9600, timeout=args.timeout)

    client.connect()
    log.debug(client)

    # read the registers
    # for information about modbus registers see doc TSMPPT.APP.Modbus.EN.10.2.pdf
    rr = client.read_holding_registers(0,count=60,unit=1)
    if rr == None:
        client.close()
        log.error("couldn't connect")
        exit(1)

    # scaling
    v_scale = rr.registers[0] + rr.registers[1]/(2**16)
    i_scale = rr.registers[2] + rr.registers[3]/(2**16)

    # the stuff we want (the numbers are decimal but the registers are listed in hex)
    data={}
    data["batt-voltage" ] = ( rr.registers[24] * float(v_scale )) / (2**15)	# 0x18
    data["array-voltage" ] = ( rr.registers[27] * float(v_scale )) / (2**15)	# 0x1b
    data["batt-current" ] = ( rr.registers[28] * float(i_scale )) / (2**15)	# 0x1c
    data["array-current" ] = ( rr.registers[29] * float(i_scale )) / (2**15)	# 0x1d
    data["batt-temp" ] = rr.registers[37] 				# 0x25
    data["power-out" ] = ( rr.registers[58] * float(v_scale)*float(i_scale)) / (2**17)	# 0x3a
    data["power-in" ] = ( rr.registers[59] * float(v_scale)*float(i_scale)) / (2**17)	# 0x3b

    # close the client
    client.close()

    # debug
    log.info("got data from mppt via modbus")
    log.debug(datetime.datetime.now())
    for key in keys:
        log.debug("%-15s : %.2f" % (key, data[key]))

    return data

def push_data(data):
    if data["array-current"] > bad_data:
        log.error("bad data, not pushing")
        return

    # xively parameters
    if args.xively:
        xively_t = xively(args.feed_id, logging, keyfile=args.keyfile, uptime=True)
        for key in keys:
            xively_t.add_datapoint(key, data[key])
        xively_t.start()
    else:
        # then we just update cursive data datastore with the one parameter
        datastore_id = 13
        key = 'value'
        value = data["power-out"]
        log.info("power-out: %s" % data["power-out"])


        cd = cursive_data(datastore_id)
        cd.add_datapoint(key, value)
        cd.start()


if __name__ == '__main__':
  argparser = argparse.ArgumentParser(
      description="fetches data via modbus and pushes to xively")
  argparser.add_argument('--tty',
    action='store', dest='tty', required=True,
      help="which serial tty is the tristar on")
#  argparser.add_argument('--no-modbus',
#    action='store_const', dest='no_modbus', const=True, default=False,
#      help="don't try to use modbus")
  argparser.add_argument('--xively',
    action='store_const', dest='xively', const=True, default=False,
      help="use xively (otherwise post direct to cursive data")
  argparser.add_argument('--keyfile',
    action='store', dest='keyfile', default="xively.key",
      help="where the api key is stored")
  argparser.add_argument('--timeout',
    action='store', dest='timeout', type=int, default = 15, 
      help="serial timeout")
  argparser.add_argument('--feed-id',
    action='store', dest='feed_id', type=int, default = 75479, #default is for solar tree
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

  log.info("using feed number %d" % args.feed_id)
  log.info("using tty %s" % args.tty)

  #fetch data
  data = get_data()
  #push data
  push_data(data)

  log.info("done")
