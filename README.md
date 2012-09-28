software for demand energy equality's solar tree

http://www.demandenergyequality.org/

getModbus.py
------------
gets modbus charge controller data (morning star tristar) via usb RS232 and pymodbus. Uploads data to cosm: https://cosm.com/feeds/75479

deps:
apt-get install python-lxml
pip install eeml
apt-get install python-pymodbus
                 
pf.py
-----
port forwards (using twisted) http or modbus so that an ssh tunnel can connect from the outside.

deps:
twisted (comes with pymodbus)

ssh
---

ssh tunnel setup for modbus like so:
ssh matt@mattvenn.net -Rmattvenn.net:10000:localhost:8080
