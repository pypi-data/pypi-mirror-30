#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "Mike Qin"
__email__ = "laigui@gmail.com"

import minimalmodbus


class RelayModule(minimalmodbus.Instrument):
    """Instrument class for HHC R4I4D 4 Digital Inputs/4 Relay Outputs Controller.
    Communicates via Modbus RTU protocol (via RS485), using the *MinimalModbus* Python module.

    Args:
        * portname (str): port name

            * examples:
            * OS X: '/dev/tty.usbserial'
            * Linux: '/dev/ttyUSB0'
            * Windows: '/com3'

        * slaveaddress (int): slave address in the range 1 to 247
    """

    def __init__(self, portname, slaveaddress):
        super().__init__(portname, slaveaddress)
        self.serial.baudrate = 9600
        self.serial.bytesize = 8
        self.serial.parity = minimalmodbus.serial.PARITY_NONE
        self.serial.stopbits = 1
        self.serial.timeout = 1  # seconds
        self.mode = minimalmodbus.MODE_RTU  # rtu or ascii mode

    def get_digital_inputs(self):
        """Return the digital inputs value."""
        return self.read_bits(32)

    def set_relay_output(self, pin, value):
        """Set the relay output value per pin.

        Args:
            * pin (int): pin number in the range 1 to 4
            * value (int): set value for the relay
        """
        if pin == 1:
            self.write_bit(16, value)
        elif pin == 2:
            self.write_bit(17, value)
        elif pin == 3:
            self.write_bit(18, value)
        elif pin == 4:
            self.write_bit(19, value)

    def get_relay_output(self, pin):
        """Return the relay output status valve per pin.

        Args:
            * pin (int): pin number in the range 1 to 4

        Returns:
            The relay status value (int).
        """
        if pin == 1:
            return self.read_bit(16, 1)
        elif pin == 2:
            return self.read_bit(17, 1)
        elif pin == 3:
            return self.read_bit(18, 1)
        elif pin == 4:
            return self.read_bit(19, 1)

    def read_bits(self, registeraddress, functioncode=2):
        """Read multiple bits from the slave.

        Args:
            * registeraddress (int): The slave register address (use decimal numbers, not hex).
            * functioncode (int): Modbus function code. Can be 1 or 2.

        Returns:
            The bits value (int).
        """
        payloadToSlave = minimalmodbus._numToTwoByteString(registeraddress) + \
                        minimalmodbus._numToTwoByteString(4)
        payloadFromSlave = self._performCommand(functioncode, payloadToSlave)
        minimalmodbus._checkResponseByteCount(payloadFromSlave)
        registerdata = payloadFromSlave[1:]
        return int(minimalmodbus._hexlify(registerdata))


########################
## Testing the module ##
########################

if __name__ == '__main__':
    minimalmodbus._print_out('TESTING HHC-R4I4D MODBUS MODULE')

    PORTNAME = '/dev/ttyUSB0'
    ADDRESS = 1

    minimalmodbus._print_out('Port: ' + str(PORTNAME) + ', Address: ' + str(ADDRESS))

    instr = RelayModule(PORTNAME, ADDRESS)
    instr.debug = True

    minimalmodbus._print_out('Digital inputs: {0}'.format(instr.get_digital_inputs()))
    instr.set_relay_output(1, 1)
    minimalmodbus._print_out('Relay 1 output: {0}'.format(instr.get_relay_output(1)))
    instr.set_relay_output(1, 0)
    minimalmodbus._print_out('Relay 1 output: {0}'.format(instr.get_relay_output(1)))
    instr.set_relay_output(2, 1)
    minimalmodbus._print_out('Relay 2 output: {0}'.format(instr.get_relay_output(2)))
    instr.set_relay_output(2, 0)
    minimalmodbus._print_out('Relay 2 output: {0}'.format(instr.get_relay_output(2)))
    instr.set_relay_output(3, 1)
    minimalmodbus._print_out('Relay 3 output: {0}'.format(instr.get_relay_output(3)))
    instr.set_relay_output(3, 0)
    minimalmodbus._print_out('Relay 3 output: {0}'.format(instr.get_relay_output(3)))
    instr.set_relay_output(4, 1)
    minimalmodbus._print_out('Relay 4 output: {0}'.format(instr.get_relay_output(4)))
    instr.set_relay_output(4, 0)
    minimalmodbus._print_out('Relay 4 output: {0}'.format(instr.get_relay_output(4)))

    minimalmodbus._print_out('DONE!')

pass