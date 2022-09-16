#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Idegis Poolstaion - using TCP/IP modbus protocol
#  Copyright (C) 2022  Christian Uhrmacher
#


from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from enum import IntEnum, auto
import time
import json
from datetime import datetime
import argparse

def roundDec(number):
    number = int((number + 5) / 10)
    return number * 10


class Reg(IntEnum):
    DESCRIPTION = 0
    TYPE = 1
    FUNCTION = 2
    ADDRESS = 3
    BIT = 4


class psRegisters:
    def __init__(self):

        # Change the IP address and port to suite your environment:
        self.inverter_ip = "10.0.0.110"
        self.inverter_port = "4196"
        self.client = ModbusTcpClient(self.inverter_ip, port=self.inverter_port)
        self.slaveAdr = 2

        #self.registers = {'name': 'output1Status', 'description': 'Output 1', 'type': 'BOOL', 'address:' 0x110, 'bit': 15}

        self.registers = {  'output1Relais': ['Output 1', 'BOOL', 0x03, 0x110, 14],
                            'output1Auto': ['Output 1', 'BOOL', 0x03, 0x110, 15],
                            'output2Relais': ['Output 1', 'BOOL', 0x03, 0x118, 14],
                            'output2Auto': ['Output 1', 'BOOL', 0x03, 0x118, 15],
                            'output3Relais': ['Output 1', 'BOOL', 0x03, 0x120, 14],
                            'output3Auto': ['Output 1', 'BOOL', 0x03, 0x120, 15],
                            'output4Relais': ['Output 1', 'BOOL', 0x03, 0x128, 14],
                            'output4Auto': ['Output 1', 'BOOL', 0x03, 0x128, 15],
                            'redox': ['Output 1', 'U16', 0x04, 0x81, 15],
                            'temperature': ['Output 1', 'U16', 0x04, 0xB1, 15], 
                            'salt': ['Output 1', 'U16', 0x04, 0xC1, 15], 
                            'ph': ['Output 1', 'U16', 0x04, 0x51, 15] }

    def getValue(self, name):

        reg = self.registers[name]
        value = None

        self.client.connect()
        if reg[Reg.FUNCTION] == 0x03:
            r1 = self.client.read_holding_registers(reg[Reg.ADDRESS], 1, unit=self.slaveAdr)
        elif reg[Reg.FUNCTION] == 0x04:
            r1 = self.client.read_input_registers(reg[Reg.ADDRESS], 1, unit=self.slaveAdr)
                 
        #print(str(r1.registers))
        
        if reg[Reg.TYPE] == 'BOOL':   
            value = int((r1.registers[0] & (2 ** reg[Reg.BIT])) / (2 ** reg[Reg.BIT]))
        elif reg[Reg.TYPE] == 'U16':   
            value = r1.registers[0]
        else:
            exit(-1)

        self.client.close()
        return value

    def setValue(self, name, input):

        reg = self.registers[name]

        self.client.connect()
        
        if reg[Reg.TYPE] == 'BOOL':
            if input == 1:
                r1 = self.client.read_holding_registers(reg[Reg.ADDRESS], 1, unit=self.slaveAdr)
                newVale = r1.registers[0] | (2 ** reg[Reg.BIT])
                #print(newVale)
                if newVale != r1.registers[0]:
                    print("write 1")
                    self.client.write_registers(reg[Reg.ADDRESS], newVale, unit=self.slaveAdr)
            elif input == 0:
                r1 = self.client.read_holding_registers(reg[Reg.ADDRESS], 1, unit=self.slaveAdr)
                newVale = r1.registers[0] & ~(2 ** reg[Reg.BIT])
                #print(newVale)
                if newVale != r1.registers[0]:
                    print("write 0")
                    self.client.write_registers(reg[Reg.ADDRESS], newVale, unit=self.slaveAdr)
            else:
                exit(-1)
            
        elif reg[Reg.TYPE] == 'uint16':    
            r1 = self.client.read_holding_registers(reg[Reg.ADDRESS], 1, unit=self.slaveAdr)
            #print(str(r1.registers))
            value = r1.registers[0]
        else:
            exit(-1)

        self.client.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get data from Idegis Poolstation via Modbus')
    parser.add_argument('registerName',help='Register name like: output1Status')
    parser.add_argument('--setValue', '-s', type=int, help='Int16 value which will be written to register')
    args = parser.parse_args()
    ps = psRegisters()

    if args.setValue or args.setValue == 0:
        str(ps.setValue(args.registerName, args.setValue))
        print(str(ps.getValue(args.registerName)))
    else:
        print(str(ps.getValue(args.registerName)))
