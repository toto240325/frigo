# establishing an ad-hoc wifi connection, which can be connected to without intermediary
# router
# wifi dongle is wlan1
 
essid="PI0"
ip="192.168.0.150"

sudo ifconfig wlan1 up
sudo iwconfig wlan1 mode ad-hoc
sudo iwconfig wlan1 essid $essid
sudo ifconfig wlan1 $ip netmask 255.255.255.0
