import os
from pysabertooth import Sabertooth

class MotorController():
    port = '/dev/tty.usbserial'
    baud = 9600
    address = 128
    timeout = 0.1

    def __init__(self, use_hardware=False):
        self.use_hardware = use_hardware
        if self.use_hardware:
            print("Setting up motor controller")
            self.saber = Sabertooth(port=self.port, baudrate=self.baud, address=self.address, timeout=self.timeout)
        else:
            print("Hardware controller is running in 'mock' model")

    def drive(self, wheel, value):
        if self.use_hardware:
            print("Sending %f to motor %i"%(value, wheel))
            self.saber.drive(value, wheel)
        else:
            print("Would send %f to motor %i"%(value, wheel))


    def stop(self, wheel, value):
        self.drive(1, 0)
        self.drive(2, 0)
        if self.use_hardware:
            print("Sending stop to motors")
            self.saber.stop()
        else:
            print("Would stop to motors")


def clip_verbose(value, minval, maxval):
    if value > maxval:
        print("Clipping control %i to %i"%(value,maxval))
        value = maxval
    if value < minval:
        print("Clipping control %i to %i"%(value,minval))
        value = minval
    return value
