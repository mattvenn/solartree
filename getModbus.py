#!/usr/bin/env python
"""
todo:
"""

import datetime
import eeml
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import logging

#cosm parameters
API_KEY = 'lzH_J6nHkyOeB8MoJiZ5MK_QxOKSAKwxUGxVdU1UbitjUT0g'
FEED = 75479
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)

pac = eeml.Pachube(API_URL, API_KEY)

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
arrayV = ( rr.registers[27] * float(v_scale )) / (2**15)
arrayI = ( rr.registers[29] * float(i_scale )) / (2**15)
battI = ( rr.registers[28] * float(i_scale )) / (2**15)
battV = ( rr.registers[24] * float(v_scale )) / (2**15)
battTemp = rr.registers[37] 
powerIn = ( rr.registers[59] * float(v_scale)*float(i_scale)) / (2**17)

#debug
print datetime.datetime.now()
print "batt v: %.2f" % battV
print "batt i: %.2f" % battI
print "array v: %.2f" % arrayV
print "array i: %.2f" % arrayI
print "batt temp: %.2f" % battTemp
print "power in: %.2f" % powerIn

print "push to cosm"
pac.update([eeml.Data("batt-voltage", battV)])
pac.update([eeml.Data("batt-current", battI)])
pac.update([eeml.Data("array-voltage", arrayV)])
pac.update([eeml.Data("array-current", arrayI)])
pac.update([eeml.Data("batt-temp", battTemp)])
pac.update([eeml.Data("power-in", powerIn)])
pac.put()

# close the client
client.close()

print "done"
