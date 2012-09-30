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

def getVScale():
    rr = client.read_holding_registers(0,2,1)
    return rr.registers[0] + rr.registers[1]/(2**16)
  
def getIScale():
    rr = client.read_holding_registers(2,2,1)
    return rr.registers[0] + rr.registers[1]/(2**16)

v_scale = getVScale()
i_scale = getIScale()

def getArrayV(v_scale):
    rr = client.read_holding_registers(27,1,1)
    return ( rr.registers[0] * float(v_scale )) / (2**15)

def getArrayI(i_scale):
    rr = client.read_holding_registers(29,1,1)
    return ( rr.registers[0] * float(i_scale )) / (2**15)

def getBattI(i_scale):
    rr = client.read_holding_registers(28,1,1)
    return ( rr.registers[0] * float(i_scale )) / (2**15)

def getBattV(v_scale):
    rr = client.read_holding_registers(24,1,1)
    return ( rr.registers[0] * float(v_scale )) / (2**15)

def getBattTemp():
    rr = client.read_holding_registers(37,1,1)
    return rr.registers[0] 

def getPowerIn(v_scale,i_scale):
    rr = client.read_holding_registers(59,1,1)
    return ( rr.registers[0] * float(v_scale)*float(i_scale)) / (2**17)

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
