#! /bin/bash

echo "Setup UART serial data port? |Only select if using Raspberry Pi 3| (y,N)"
read UART
if [ "$UART" == "y" ]; then
	echo "core_freq=250" >> /boot/config.txt
	echo "enable-uart=1" >> /boot/config.txt
	echo "pi3-disable-bt" >> /boot/config.txt
	echo "Enabled UART, reboot required to take effect."
	REBOOT_REQUIRED="y"
fi
echo "We will now setup the configuration file. Please entry the following information found at your Cayenne dashboard."
echo "MQTT Username? [no default]"
read MQTT_U
echo "MQTT Password? [no default]"
read MQTT_P
echo "Client ID? [no default]"
read CLIENT
echo "MQTT Server? [mqtt.mydevices.com]"
read SERVER
echo "MQTT Port? [1883]"
read PORT
if ["$SERVER" == ""]; then
	SERVER="mqtt.mydevices.com"
fi
if ["$PORT" == ""]; then
	PORT="1883"
fi
echo "MQTT_USERNAME="$MQTT_U > mqtt.conf
echo "MQTT_PASSWORD="$MQTT_P >> mqtt.conf
echo "CLIENT_ID="$CLIENT >> mqtt.conf
echo "MQTT_SERVER="$SERVER >> mqtt.conf
echo "MQTT_PORT="$PORT >> mqtt.conf
echo "Generated configuration file, please check this is correct."
cat mqtt.conf

echo "Would you like to set Cayenne Uploader to start automatically on boot? (Y,n)"
read AUTOSTART
if [ "$AUTOSTART" == "y" ]; then
	echo "#! /bin/bash" > /etc/init.d/cayenne_autostart.sh
	echo "$(pwd)/bore_reader.py" >> /etc/init.d/cayenne_autostart.sh
	chmod 755 /etc/init.d/cayenne_autostart.sh
	update-rc.d cayenne_autostart.sh defaults
	echo "Cayenne uploader will now start automatically on boot."
else
	if [ "$AUTOSTART" == "Y" ]; then
		echo "#! /bin/bash" > /etc/init.d/cayenne_autostart.sh
		echo "$(pwd)/bore_reader.py" >> /etc/init.d/cayenne_autostart.sh
		chmod 755 /etc/init.d/cayenne_autostart.sh
		update-rc.d cayenne_autostart.sh defaults
		echo "Cayenne uploader will now start automatically on boot."
	else
		echo "Capenne uploader will have to be started manually after rebooting."
	fi
fi
# after complete check for reboot
if [ "$REBOOT_REQUIRED" == "y" ]; then
	echo "You need to reboot for changes to take effect. Reboot now? (Y,n)"
	read REBOOT
	if [ "REBOOT" == "y" ]; then
		reboot
	fi
	if [ "REBOOT" == "Y" ]; then
		reboot
	fi
	echo "Okay, not rebooting. Please reboot manually before trying to use this new setup."
fi
echo "Setup complete."
