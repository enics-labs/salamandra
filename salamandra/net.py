# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from .object import Object, slm_sort
from .associable import Associable
import re


class Net(Object, Associable):
    def __init__(self, name, bus = None):
        Object.__init__(self, name)
        Associable.__init__(self, None) #TODO remove associable
        if bus.__class__.__name__ == 'Bus':
            self.__bus = bus
        else:
            self.__bus = None

    def is_part_of_bus(self):
        if self.__bus:
            return True
        return False

    def bus(self):
        if self.is_part_of_bus():
            return self.__bus
        else:
            raise Exception('not part of bus')

    def verilog_type(self):
        return 'wire'

    def verilog_declare(self):
        if self.is_part_of_bus():
            return self.__bus.verilog_declare(self)
        else:
            return self.verilog_type() + ' ' + self.get_object_name() + ';'

    @staticmethod
    def is_name_valid(name):  # verilog rules ('[]' for bus. like: A[0], \A#@ [0])
        return re.match(r'(^[a-zA-Z_][a-zA-Z0-9_$\[\]\-]{0,1023}$|^\\\S* (\[-?\d+\])?$)', name)

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
