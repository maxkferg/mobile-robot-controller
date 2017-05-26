
SYSFS_GPIO_DIR = "/sys/class/gpio"

J21_PINS = {
    "32": "gpio36",      # J21 - Pin 32 - Unused - AO_DMIC_IN_CLK
    "16": "gpio37",      # J21 - Pin 16 - Unused - AO_DMIC_IN_DAT
    "13": "gpio38",      # J21 - Pin 13 - Bidir  - GPIO20/AUD_INT
    "33": "gpio63",      # J21 - Pin 33 - Bidir  - GPIO11_AP_WAKE_BT
    "18": "gpio184",    # J21 - Pin 18 - Input  - GPIO16_MDM_WAKE_AP
    "31": "gpio186",    # J21 - Pin 31 - Input  - GPIO9_MOTION_INT
    "37": "gpio187",    # J21 - Pin 37 - Output - GPIO8_ALS_PROX_INT
    "29": "gpio219",    # J21 - Pin 29 - Output - GPIO19_AUD_RST
}

J3A_PINS = {
    "50": "gpio57",     # J3A1 - Pin 50
    "40": "gpio160",    # J3A2 - Pin 40
    "43": "gpio161",    # J3A2 - Pin 43
    "46": "gpio162",    # J3A2 - Pin 46
    "49": "gpio163",    # J3A2 - Pin 49
    "52": "gpio164",    # J3A2 - Pin 52
    "55": "gpio165",    # J3A2 - Pin 55
    "58": "gpio166"     # J3A2 - Pin 58
}



class MockPin(object):
    """
    Mock GPIO Pin for development testing
    """

    def __init__(self, port, pin, is_out=True):
        """
        Setup the GPIO pin
        @port The GPIO port number (J21 or J3A)
        @pin is the pin number (int)
        @is_out specifies the direction of the GPIO pin (Bool)
        """
        if port=="J21":
            self.name = J21_PINS.get(pin)
        elif port=="J3A_PINS":
            self.name = J21_PINS.get(pin)
        else:
            raise Exception("No such port {0}".format(port))
        if not self.name:
            raise Exception("No such pin: {0} on port {1}".format(pin,port))


    def low(self):
        """
        Set the pin to the low state (convenience method)
        """
        pass



    def high(self):
        """
        Set the pin to the low state (convenience method)
        """
        pass


    def enable(self):
        """
        Open the GPIO pin for usage
        """
        print("Mock: Enabled pin {0}".format(self.name))



    def disable(self):
        """
        Disable the GPIO pin
        """
        print("Mock: Disabled pin {0}".format(self.name))



    def set_direction(self, is_out):
        """
        Set the direction of the GPIO pin
        Return: Success = 0 ; otherwise open file error
        """
        print("Mock: Set direction of pin {0}".format(self.name))



    def set_value(self, value):
        """
        Set the value of the GPIO pin to 1 or 0
        Return: Success = 0 ; otherwise open file error
        """
        pass



    def get_value(self):
        """
        Get the value of the requested GPIO pin ; value return is 0 or 1
        Return: The value on the pin
        """
        return 1




class Pin(object):
    """
    Represents a GPIO pin on the NVIDIA Jetson TX1
    """

    def __init__(self, port, pin, is_out=True):
        """
        Setup the GPIO pin
        @port The GPIO port number (J21 or J3A)
        @pin is the pin number (int)
        @is_out specifies the direction of the GPIO pin (Bool)
        """
        if port=="J21":
            self.name = J21_PINS.get(pin)
        elif port=="J3A_PINS":
            self.name = J21_PINS.get(pin)
        else:
            raise Exception("No such port {0}".format(port))
        if not self.name:
            raise Exception("No such pin: {0} on port {1}".format(pin,port))
        # The pin and port are valid
        # Set the output
        self.id = self.name.strip("gpio")
        self.enable()
        self.set_direction(is_out)


    def __exit__(self):
        """
        Disable the pin
        """
        self.disable()


    def low(self):
        """
        Set the pin to the low state (convenience method)
        """
        self.set_value(0)



    def high(self):
        """
        Set the pin to the low state (convenience method)
        """
        self.set_value(1)



    def enable(self):
        """
        Open the GPIO pin for usage
        """
        filename = "{0}/export".format(SYSFS_GPIO_DIR, self.name)

        try:
            with open(filename,'w') as buff:
                buff.write(self.id)
        except Exception as e:
            print("Unable to setup {0}".format(self.name))
        print("Enabled pin {0}".format(self.name))



    def disable(self):
        """
        Disable the GPIO pin
        """
        filename = "{0}/unexport".format(SYSFS_GPIO_DIR, self.name)

        try:
            with open(filename,'w') as buff:
                buff.write(self.id)
        except Exception as e:
            print("Unable to disable {0}".format(self.name))
            raise e
        print("Disabled pin {0}".format(self.name))



    def set_direction(self, is_out):
        """
        Set the direction of the GPIO pin
        Return: Success = 0 ; otherwise open file error
        """

        filename = "{0}/{1}/direction".format(SYSFS_GPIO_DIR, self.name)

        try:
            with open(filename,'w') as buff:
                if is_out:
                    buff.write("out")
                else:
                    buff.write("in")
        except Exception as e:
            print("Unable to set GPIO direction")
            raise e



    def set_value(self, value):
        """
        Set the value of the GPIO pin to 1 or 0
        Return: Success = 0 ; otherwise open file error
        """
        filename = "{0}/{1}/value".format(SYSFS_GPIO_DIR, self.name)

        try:
            with open(filename,'w') as buff:
                if value==1:
                    buff.write("1")
                elif value==0:
                    buff.write("0")
                else:
                    raise Exception("Pin {0} got unkown value: {1}".format(self.name, value))
        except Exception as e:
            print("Unable to set GPIO direction")
            raise e



    def get_value(self):
        """
        Get the value of the requested GPIO pin ; value return is 0 or 1
        Return: The value on the pin
        """
        filename = "{0}/{1}/value".format(SYSFS_GPIO_DIR, self.name)

        try:
            with open(filename) as buff:
                value = buff.read().strip()
                if value=="1" or value=="0":
                    return int(value)
                else:
                    raise Exception("Unknown value from pin {0}: {1}".format(self.name, value)) 
        except Exception as e:
            print("Unable to read GPIO value")
            raise e
