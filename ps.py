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
    ADDRESS = 2
    BIT = 3


class psRegisters:
    def __init__(self):

        # Change the IP address and port to suite your environment:
        self.inverter_ip = "10.0.0.110"
        self.inverter_port = "4196"
        self.client = ModbusTcpClient(self.inverter_ip, port=self.inverter_port)
        self.slaveAdr = 2

        #self.registers = {'name': 'output1Status', 'description': 'Output 1', 'type': 'BOOL', 'address:' 0x110, 'bit': 15}

        self.registers = {'output1Relais': ['Output 1', 'BOOL', 0x110, 14],
                            'output1Auto': ['Output 1', 'BOOL', 0x110, 15] }

    def read(self, client, bit = 0):
        try:
            # -----------------------------------------
            # Routine to read a string from one address with 8 registers
            if self.type == 'Strg8':
                r1 = client.read_holding_registers(self.address, 8, unit=2)
                str8Register = BinaryPayloadDecoder.fromRegisters(r1.registers, byteorder=Endian.Big)
                self.value = str8Register.decode_string(8)

            # Routine to read a U16 from one address with 1 register
            if self.type == 'U16':
                
                r1 = client.read_holding_registers(self.address, 1, unit=2)

                print(str(r1) + "  " + str(r1.registers))
                self.value = r1.registers

            # Routine to read a U16 from one address with 1 register
            if self.type == 'BOOL':
                
                r1 = client.read_holding_registers(self.address, 1, self.slaveAdr)
               # print(str(r1) + " " + str(r1.registers[0]) + "  " + str(r1.registers) + str(type(r1.registers)))

                self.value = bool(r1.registers[0] & (2 ^ bit))


            return True
            # print(self.name + ':\t' + str(self.value))
        except Exception as ex:
            print("### Error Reading from PS: ", ex)
            return False

    def getRegister(self):
        return self.registers

    def getTimestamp(self):
        return self.timestamp


    def getValue(self, name):

        reg = self.registers[name]
        value = None
        # print(reg[0])
        # print(reg[1])
        # print(reg[3])
        # print(reg[Reg.TYPE])
        # print("")

        self.client.connect()
        if reg[Reg.TYPE] == 'BOOL':            
            r1 = self.client.read_holding_registers(reg[Reg.ADDRESS], 1, unit=self.slaveAdr)
            #print(str(r1.registers))
            value = bool(r1.registers[0] & (2 ^ reg[Reg.BIT]))
        elif reg[Reg.TYPE] == 'uint16':    
            r1 = self.client.read_holding_registers(reg[Reg.ADDRESS], 1, unit=self.slaveAdr)
            #print(str(r1.registers))
            value = r1.registers[0]
        else:
            exit(-1)

        self.client.close()


        return value
            




if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get data from Idegis Poolstation via Modbus')
    parser.add_argument('registerName',help='Register name like: output1Status')
    parser.add_argument('--setValue', '-s', type=int, help='Int16 value which will be written to register')
    args = parser.parse_args()
    ps = psRegisters()

    if args.setValue:
        print(str(ps.setValue(args.registerName)))
        print(str(ps.getValue(args.registerName)))
    else:
        print(str(ps.getValue(args.registerName)))
