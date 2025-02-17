# Disable UART, I2C, SPI
#raspi-config nonint do_serial 1
#raspi-config nonint do_i2c 1
#raspi-config nonint do_spi 1
# Disable HDMI
/usr/bin/tvservice -o
# Turn off USB/LAN
echo '1-1' | tee /sys/bus/usb/drivers/usb/unbind
# down 1
systemctl stop bluetooth
systemctl stop wpa_supplicant
systemctl stop hciuart
systemctl stop alsa-state
# down 2
systemctl stop dhcpcd
systemctl stop avahi-daemon
systemctl stop polkit
systemctl stop triggerhappy
# down 3
systemctl stop syslog*
systemctl stop rsyslog*
systemctl stop rng-tools
systemctl stop systemd-timesyncd
systemctl stop systemd-logind
systemctl stop systemd-udevd
systemctl stop systemd-journald*
systemctl stop systemd-rfkill*
systemctl stop systemd-getty*
# down 4
systemctl stop cron*
systemctl stop dbus*
systemctl stop ssh*
#down 5
#systemctl stop getty@tty1
#systemctl stop user@1000
#systemctl stop session*
#
#
# - Cold options (need a reboot) - 
#
## Disable crontab 
#
#	sudo micro /etc/crontab
#	Place a # before each line
#
# ls /var/spool/cron/crontabs/
# crontab -l 						# list all users
# crontab -e 						# edit current's user crontab file
# crontab -e -u <user> 	# edit specified user crontab file
#
#
## Disable Undervoltage Warning (Choose one, not recommeded to do)
#
# echo "avoid_warnings=1"       | tee -a /boot/config.txt > /dev/null # Avoid Warnings
# echo "avoid_warnings=2"       | tee -a /boot/config.txt > /dev/null # AW & EN Turbo mode
#
#
## Disable Bluetooth & WiFi
#
#	echo "dtoverlay=disable-wifi" | tee -a /boot/config.txt > /dev/null
#	echo "dtoverlay=disable-bt"   | tee -a /boot/config.txt > /dev/null
#
#
## Disable hardware UART
#
#	echo "enable_uart=0"          | tee -a /boot/config.txt > /dev/null
#
#
## Disable SPI, I2C, I2S, AUDIO hardware modules
#
#	echo "dtparam=spi=off"        | tee -a /boot/config.txt > /dev/null
#	echo "dtparam=i2c_arm=off"    | tee -a /boot/config.txt > /dev/null
#	echo "dtparam=i2s=off"        | tee -a /boot/config.txt > /dev/null
#	echo "dtparam=audio=off"      | tee -a /boot/config.txt > /dev/null
#
#
## Disable Ethernet leds
#
#	echo "dtparam=act_led_trigger=none"  | tee -a /boot/config.txt > /dev/null
#	echo "dtparam=pwr_led_trigger=none"  | tee -a /boot/config.txt > /dev/null
# echo "dtparam=act_led_activelow=off" | tee -a /boot/config.txt > /dev/null
# echo "dtparam=pwr_led_activelow=off" | tee -a /boot/config.txt > /dev/null
#
#
## Disable Kernel modules
#
# 1) Create a blacklist file: sudo micro /etc/modprobe.d/blacklist.conf
# 2) Fill this file with:
#
# install videodev /bin/false
# install rfkill /bin/false
# install mc /bin/false
# blacklist cfg80211
# blacklist binfmt_misc
# blacklist raspberrypi_hwmon
# blacklist videobuf2_core
# blacklist videobuf2_memops
# blacklist videobuf2_vmalloc
# blacklist uvcvideo
# blacklist uio
# blacklist uio_pdrv_genirq
# blacklist vc_sm_cma
# blacklist i2c_dev
# 
# 3) Execute this command: sudo update-initramfs -u
# 4) Reboot: sudo reboot
# 5) Check loaded modules with: lsmod
#
# Source: https://askubuntu.com/questions/458515/how-to-disable-internal-webcam
