#!/usr/bin/env python
import eeml

# parameters
API_KEY = 'lzH_J6nHkyOeB8MoJiZ5MK_QxOKSAKwxUGxVdU1UbitjUT0g'
FEED = 75479
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)

pac = eeml.Pachube(API_URL, API_KEY)
'''
Pymodbus Synchronous Client Examples
--------------------------------------------------------------------------

The following is an example of how to use the synchronous modbus client
implementation from pymodbus.

It should be noted that the client can also be used with
the guard construct that is available in python 2.5 and up::

    with ModbusClient('127.0.0.1') as client:
        result = client.read_coils(1,10)
        print result
'''
#---------------------------------------------------------------------------# 
# import the various server implementations
#---------------------------------------------------------------------------# 
#from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#from pymodbus.client.sync import ModbusUdpClient as ModbusClient
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

#---------------------------------------------------------------------------# 
# configure the client logging
#---------------------------------------------------------------------------# 
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#---------------------------------------------------------------------------# 
# choose the client you want
#---------------------------------------------------------------------------# 
# make sure to start an implementation to hit against. For this
# you can use an existing device, the reference implementation in the tools
# directory, or start a pymodbus server.
#
# It should be noted that you can supply an ipv4 or an ipv6 host address for
# both the UDP and TCP clients.
#---------------------------------------------------------------------------# 
#client = ModbusClient('192.168.2.150')
#client = ModbusClient(method='ascii', port='/dev/pts/2', timeout=1)
client = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, timeout=1)
client.connect()

#---------------------------------------------------------------------------# 
# example requests
#---------------------------------------------------------------------------# 
# simply call the methods that you would like to use. An example session
# is displayed below along with some assert checks. Note that some modbus
# implementations differentiate holding/input discrete/coils and as such
# you will not be able to write to these, therefore the starting values
# are not known to these tests. Furthermore, some use the same memory
# blocks for the two sets, so a change to one is a change to the other.
# Keep both of these cases in mind when testing as the following will
# _only_ pass with the supplied async modbus server (script supplied).
#---------------------------------------------------------------------------# 
#import pdb;pdb.set_trace()
#rr = client.read_holding_registers(24,30,1)
#print rr.registers
#assert(rr.registers[0] == 10)       # test the expected value
#print rr.registers[0]

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
#    print rr.registers
#    print i_scale
    return ( rr.registers[0] * float(i_scale )) / (2**15)

def getBattI(i_scale):
    rr = client.read_holding_registers(28,1,1)
    return ( rr.registers[0] * float(i_scale )) / (2**15)

def getBattV(v_scale):
    rr = client.read_holding_registers(24,1,1)
    return ( rr.registers[0] * float(v_scale )) / (2**15)

def getTemp():
    rr = client.read_holding_registers(37,1,1)
    return rr.registers[0] 

def getPowerIn(v_scale,i_scale):
    rr = client.read_holding_registers(59,1,1)
    return ( rr.registers[0] * float(v_scale)*float(i_scale)) / (2**17)

battV = getBattV(v_scale)
battI = getBattI(i_scale)
arrayV = getArrayV(v_scale)
arrayI = getArrayI(i_scale)
temp = getTemp()
powerIn = getPowerIn(v_scale,i_scale)

print "batt v: %.2f" % battV
print "batt i: %.2f" % battI
print "array v: %.2f" % arrayV
print "array i: %.2f" % arrayI
print "temp: %.2f" % temp
print "power in: %.2f" % powerIn

print "push to cosm"
pac.update([eeml.Data(0, battV)])
pac.update([eeml.Data(1, battI)])
pac.update([eeml.Data(2, arrayV)])
pac.update([eeml.Data(3, arrayI)])
pac.update([eeml.Data("temp", temp)])
pac.update([eeml.Data("power in", powerIn)])
pac.put()
print "done"

#---------------------------------------------------------------------------# 
# close the client
#---------------------------------------------------------------------------# 
client.close()
