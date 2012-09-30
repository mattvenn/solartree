#!/usr/bin/env python
"""
todo:
    only read the registers once, save transactions
"""

import eeml

# parameters
API_KEY = 'lzH_J6nHkyOeB8MoJiZ5MK_QxOKSAKwxUGxVdU1UbitjUT0g'
FEED = 75479
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)

pac = eeml.Pachube(API_URL, API_KEY)

# import the server implementation
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# choose the client you want
client = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, timeout=1)
client.connect()

rr = client.read_holding_registers(0,60,1)

def getVScale():
    return rr.registers[0] + rr.registers[1]/(2**16)
  
def getIScale():
    return rr.registers[2] + rr.registers[3]/(2**16)

v_scale = getVScale()
i_scale = getIScale()

def getArrayV(v_scale):
    return ( rr.registers[27] * float(v_scale )) / (2**15)

def getArrayI(i_scale):
    return ( rr.registers[29] * float(i_scale )) / (2**15)

def getBattI(i_scale):
    return ( rr.registers[28] * float(i_scale )) / (2**15)

def getBattV(v_scale):
    return ( rr.registers[24] * float(v_scale )) / (2**15)

def getBattTemp():
    return rr.registers[37] 

def getPowerIn(v_scale,i_scale):
    return ( rr.registers[59] * float(v_scale)*float(i_scale)) / (2**17)

battV = getBattV(v_scale)
battI = getBattI(i_scale)
arrayV = getArrayV(v_scale)
arrayI = getArrayI(i_scale)
temp = getBattTemp()
powerIn = getPowerIn(v_scale,i_scale)

print "batt v: %.2f" % battV
print "batt i: %.2f" % battI
print "array v: %.2f" % arrayV
print "array i: %.2f" % arrayI
print "temp: %.2f" % temp
print "power in: %.2f" % powerIn

exit()
print "push to cosm"
pac.update([eeml.Data("batt-voltage", battV)])
pac.update([eeml.Data("batt-current", battI)])
pac.update([eeml.Data("array-voltage", arrayV)])
pac.update([eeml.Data("array-current", arrayI)])
pac.update([eeml.Data("batt-temp", temp)])
pac.update([eeml.Data("power-in", powerIn)])
pac.put()
print "done"

# close the client
client.close()
