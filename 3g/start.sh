count=0
date

#if no modem tty then try and switch modem
if ls /dev/ttyUSB0 2> /dev/null; then 
	echo "ttyUSB0 already exists"
else
	while [ $count -le 1 ]; do
		echo "usb modeswitch attempt $count"
		count=$((count+1))
		sudo usb_modeswitch -c usb-modeswitch.conf -I
	done
fi

#if got tty then start wvdial
if ls /dev/ttyUSB0 2> /dev/null; then 
	echo "starting wvdial"
	sudo wvdial -C wvdial.conf 3gconnect
else
	echo "no modem, finishing"
fi
