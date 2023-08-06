# pyusbmodule
Python interface to expansion modules via USB(Modbus/UART) connection.


## Installation

```
pip3 install -U pyusbmodule
```


## Usage

```
>from usbmodule import r4i4d
>instr = r4i4d.RelayModule('/dev/ttyUSB0', 1) 
>instr.get_digital_inputs()
```