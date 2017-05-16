sudo modprobe --first-time i2c-dev
echo "Connected I2C ports:"
i2cdetect -y 1
echo "My Public IP:"
curl ipinfo.io/ip