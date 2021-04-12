# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from .object import Object, slm_sort
from .associable import Associable
import re


class Pin(Object, Associable):
    def __init__(self, name, bus=None, is_virtual=False, associated_comp=None, associated_pin=None):
        Object.__init__(self, name)
        Associable.__init__(self, None) #TODO remove associable
        if bus.__class__.__name__ == 'Bus':
            self.__bus = bus
        else:
            self.__bus = None
        self.__is_virtual = is_virtual
        if is_virtual:
            self.__associated_comp = associated_comp
            self.__associated_pin = associated_pin

    def is_part_of_bus(self):
        if self.__bus:
            return True
        return False

    def bus(self):
        if self.is_part_of_bus():
            return self.__bus
        else:
            raise Exception('not part of bus')

    def verilog_port_list(self):
        if self.is_part_of_bus():
            return self.__bus.verilog_port_list(self)
        else:
            return self.get_object_name()

    def verilog_declare(self):
        if self.is_part_of_bus():
            return self.__bus.verilog_declare(self)
        else:
            return self.verilog_type() + ' ' + self.get_object_name() + ';'

    def verilog_type(self):
        return 'inout'

    def is_virtual(self):
        return self.__is_virtual

    def get_associated_comp(self):
        return self.__associated_comp

    def get_associated_pin(self):
        return self.__associated_pin

    @staticmethod
    def is_name_valid(name):  # verilog rules ('.' for virtual_pins, '[]' for bus. like: A[0], \A#@ [0])
        return re.match(r'((^[a-zA-Z_][a-zA-Z0-9_$\[\]\-]{0,1023}|^\\\S* (\[-?\d+\])?)'
                        r'(\.(^[a-zA-Z_][a-zA-Z0-9_$\[\]\-]{0,1023}|^\\\S* (\[-?\d+\])?))?)', name)

    def __lt__(self, other):  # sort by width of bus
        if self.is_part_of_bus():
            sw = self.__bus.width()
            sn = self.__bus.get_name()
        else:
            sw = 0
            sn = self.get_object_name()

        if other.is_part_of_bus():
            ow = other.__bus.width()
            on = other.__bus.get_name()
        else:
            ow = 0
            on = other.get_object_name()

        if sw != ow:
            return sw > ow
        return slm_sort()(sn) < slm_sort()(on)
