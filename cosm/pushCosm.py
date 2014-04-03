#!/usr/bin/env python
"""
todo:
"""

import datetime
import eeml
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import logging
import argparse


def get_data():
    # configure the client logging
    logging.basicConfig()
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    # choose the serial client
    client = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, timeout=1)
    client.connect()

    #read the registers
    rr = client.read_holding_registers(0,60,1)

    if rr == None:
        client.close()
        print "couldn't connect"
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
    print datetime.datetime.now()
    print "batt v: %.2f" % data["battV" ]
    print "batt i: %.2f" % data["battI" ]
    print "array v: %.2f" % data["arrayV" ]
    print "array i: %.2f" % data["arrayI" ]
    print "batt temp: %.2f" % data["battTemp" ]
    print "power in: %.2f" % data["powerIn" ]

    return data

def push_data(data):
    print "push to cosm"
    #cosm parameters
    API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = args.feed)
    pac = eeml.Pachube(API_URL, key )

    pac.update([eeml.Data("batt-voltage", data["battV" ])])
    pac.update([eeml.Data("batt-current", data["battI" ])])
    pac.update([eeml.Data("array-voltage", data["arrayV" ])])
    pac.update([eeml.Data("array-current", data["arrayI" ])])
    pac.update([eeml.Data("batt-temp", data["battTemp" ])])
    pac.update([eeml.Data("power-in", data["powerIn" ])])
    pac.put()


if __name__ == '__main__':
  argparser = argparse.ArgumentParser(
      description="fetches data via modbus and pushes to cosm")
  argparser.add_argument('--keyfile',
    action='store', dest='keyfile', default="api.key",
      help="where the api key is stored")
  argparser.add_argument('--feed',
    action='store', dest='feed', type=int, default = 75479, #default is for solar tree
      help="feed number")

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

  #fetch data
  data = get_data()

  #push data
  push_data(data)

  print "done"