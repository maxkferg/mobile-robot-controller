sudo modprobe --first-time i2c-dev
echo "Connected I2C ports:"
i2cdetect -y 1
echo "My Private IP:"
ifconfig wlan0 | grep "inet addr"