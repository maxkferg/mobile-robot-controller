echo "Connected I2C ports:"
i2cdetect -y 0
echo "My Private IP:"
ifconfig wlan0 | grep "inet addr"
