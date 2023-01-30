import serial
import serial.tools.list_ports
import sys

def get_ports():
    availablePort = []
    port_list = list(serial.tools.list_ports.comports())
    #print(port_list)
    if len(port_list) == 0:
        print('没有找到串口设备!')
    else:
        for port in port_list:
            availablePort.append(port.device)
            print(port.device)
            #print(port)
    return availablePort

def open_port(portName,baudrate, byteSize, stopBit, parity):
    # print('[serialUtils]', baudrate, type(baudrate))
    # print('[serialUtils]','Line:{}'.format(sys._getframe().f_lineno), byteSize, type(byteSize))
    ser = serial.Serial(port = portName,
                        baudrate=baudrate,
                        bytesize=byteSize,#8
                        stopbits=serial.STOPBITS_ONE,#stopBit
                        parity=serial.PARITY_NONE,#parity,#
                        rtscts=False,
                        timeout=None,
                        #xonxoff=False,
                        write_timeout=None)
    #print('Line:{}'.format(sys._getframe().f_lineno), baudrate,type(baudrate))
    return ser

if __name__ == '__main__':
    get_ports()
    #open_port('COM3',19200)