#!/usr/bin/python

import serial
baud = [ 9600, 57600, 19200 ]
for i in range(10000):
	print i
	s= serial.Serial()
	s.port= '/dev/ttyUSB0'
	s.baudrate= baud[ i % 3 ]
	s.timeout= 0.1
	s.writeTimeout= 0.1
	s.open()

	s.write(" ")
	a = s.read()

	s.close()

