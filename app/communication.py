#-------------------------------------------------------------------------------
 #!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------

from serial.tools import list_ports
from collections import OrderedDict
import serial
import threading
from queue import Queue
from time import sleep
import struct

class search_thread(threading.Thread):
    def __init__(self, target, code,baudrates, callback):
        threading.Thread.__init__(self)
        self.target=target
        self.__code=code
        self.__baudrates=baudrates
        self.__callback=callback

    def run(self):
        self.target(self.__code,self.__baudrates, self.__callback)

class com_port:
    def __init__(self):
        self.__com_ports=OrderedDict()
        self.__current_com=None
        self.__baudrate=115200
        self.connected = False
        self.check_all()

    def closeport(self, ser):
        if ser.isOpen() == True:
            ser.setDTR(False)
            sleep(2)
            ser.setDTR(True)
            ser.close()
            print('{0} with br:{1} closed'.format(ser.port,ser.baudrate))

    def baudrate(self):
        return self.__baudrate

    def setBaudrate(self, value):
        self.__baudrate=value

    def current(self):
        return self.__current_com

    def setCurrent(self, value):
        self.__current_com=value

    def search_device(self, code,baudrates, callback=None):
        rx_thread=search_thread(self.search_device_func, code,baudrates,callback)
        rx_thread.setDaemon(True)
        rx_thread.start()

    def search_device_func(self, code,baudrates,callback):
        finded=False
        trys=10
        for baudrate in baudrates:
            for com in self.__com_ports:
                self.__baudrate=baudrate
                print(self.__baudrate, com)
                try:
                    ser = serial.Serial(com, self.__baudrate, timeout=.1)
                    ser.setDTR(False)
                    sleep(1)
                    ser.flushInput()
                    ser.setDTR(True)
                    sleep(1)
                    with ser:
                        for i in range(0,trys):
                            ser.write(code.encode('utf-8'))
                            try:
                                rx = ser.readline()
                                rx2 = ser.readline().decode("ascii")
                            except Exception:
                                break
                            if rx!=b'H':
                                # rx=int(ord(rx))
                                break
                            sleep(1)
                    self.closeport(ser)
                    rule = 'Название прибора' in rx2
                    if rule:
                        print(rx2)
                        self.setCurrent(com)
                        finded=True
                        break
                except serial.serialutil.SerialException:
                    print('Used')
                if finded:
                    break
            if finded:
                break
        callback(self.current(), baudrate, finded)


    def check_all(self):
        for port, desc, hwid in sorted(list_ports.comports()):
            if u'USB' in hwid:
                self.__com_ports[port]={u'desc':desc, u'hwid':hwid}

    def comports(self):
        return tuple(self.__com_ports)

