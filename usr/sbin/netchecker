#!/usr/bin/python

import urllib2
from os import system
from time import sleep
import logging


sleep_time=60
#reboot after this many bad connections
reboot_connections=5

bad_connections=0
timeout_time=5

def internet_on():
    try:
        response=urllib2.urlopen('http://google.co.uk',timeout=timeout_time)
        return True
    except urllib2.URLError as err: pass
    return False

if __name__ == "__main__":
	logger = logging.getLogger('net checker')
	hdlr = logging.FileHandler('/var/log/netcheck.log')
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
	logger.setLevel(logging.INFO)
	logger.info('starting')

	#forever...
	while True:
		if internet_on():
			logger.info("internet connection OK")
			bad_connections=0
		else:
			logger.warning("internet failure! rebooting in %dsecs" % ((reboot_connections-bad_connections)*sleep_time))
			bad_connections+=1
		if bad_connections > reboot_connections:
			logger.warning("rebooting!")
			system("/sbin/shutdown -r now")
			exit(1)
		sleep(sleep_time)
