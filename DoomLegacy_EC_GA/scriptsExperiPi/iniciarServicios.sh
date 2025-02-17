# Turn on USB/LAN
echo '1-1' | tee /sys/bus/usb/drivers/usb/bind
sleep 4s
# Readquire IP
ifconfig eth0 up 
dhcpcd -n eth0 2> /dev/null
# Restart ssh server
systemctl restart sshd
# Enable HDMI
#/usr/bin/tvservice -p
# Enable UART, I2C, SPI
#raspi-config nonint do_serial 0  # 0: uart cmd, 2: hardware uart
#raspi-config nonint do_i2c 0
#raspi-config nonint do_spi 0
#
# - Cold options - 
#
## Enable crontab 
#	micro /etc/crontab
#	Remove the # before each line
#
## Enable Undervoltage warning (Choose one)
#
# echo "avoid_warnings=0"       | tee -a /boot/config.txt > /dev/null # Show UV Warnings
#
## Enable Bluetooth & WiFi

# *** to do ****

# sed -i 's/search_string/replace_string/' filename
#
# sed -i 's/dtoverlay=disable-wifi/""/' /boot/config.txt > /dev/null
#sudo sed -i 's/avoid_warnings=\b[0-2]/avoid_warnings=0/' /boot/config.txt 
#
#
#	echo "dtoverlay=disable-wifi" | tee -a /boot/config.txt > /dev/null
#	echo "dtoverlay=disable-bt"   | tee -a /boot/config.txt > /dev/null
#
#	echo "enable_uart=0"          | tee -a /boot/config.txt > /dev/null
#
#	echo "dtparam=i2c_arm=off"    | tee -a /boot/config.txt > /dev/null
#	echo "dtparam=i2s=off"        | tee -a /boot/config.txt > /dev/null
#	echo "dtparam=spi=off"        | tee -a /boot/config.txt > /dev/null
#	echo "dtparam=audio=off"      | tee -a /boot/config.txt > /dev/null
#	echo "dtparam=act_led_trigger=none"  | tee -a /boot/config.txt > /dev/null
#	echo "dtparam=pwr_led_trigger=none"  | tee -a /boot/config.txt > /dev/null
# echo "dtparam=act_led_activelow=off" | tee -a /boot/config.txt > /dev/null
# echo "dtparam=pwr_led_activelow=off" | tee -a /boot/config.txt > /dev/null
