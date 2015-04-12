software for demand energy equality's solar tree

http://www.demandenergyequality.org/

# pushCosm.py

gets modbus charge controller data (morning star tristar) via usb RS232 and pymodbus. Uploads data to cosm: https://cosm.com/feeds/75479

## dependancies

* sudo apt-get install python-lxml
* sudo apt-get install python-pymodbus
* sudo pip install mechanize

# pf.py

port forwards (using twisted) http or modbus so that an ssh tunnel can connect from the outside.

## dependancies

* twisted (comes with pymodbus)

# ssh

* sudo apt-get install autossh
* ssh tunnel setup for modbus like so:

    ssh matt@mattvenn.net -Rmattvenn.net:10000:localhost:8080

# sakis3g 3g dongle controller

sudo apt-get install libusb-dev
sudo apt-get install ppp
sakis3g recompile
sudo cp sakis3g /usr/bin

# netchecker install

cp netchecker /usr/sbin/
sudo update-rc.d netchecker defaults

# TODO

* setup reader -> xively - done
* read only filesystem - done
* ssh tunnel
