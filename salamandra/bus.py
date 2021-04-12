# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from .associable import Associable
from .input import Input
from .output import Output
from .inout import Inout
from .net import Net
from .object import Object


class Bus(Associable):
    def __init__(self, bit_type, name, width, associate_with=None, signed=False):
        Associable.__init__(self, associate_with)
        if not Object.is_name_valid(name):
            raise Exception('name "' + name + '" should be as verilog syntax format')
        self.__name = name
        if isinstance(bit_type, str):
            if bit_type.lower() == 'input':
                self.__type = Input
            elif bit_type.lower() == 'output':
                self.__type = Output
            elif bit_type.lower() == 'inout':
                self.__type = Inout
            elif bit_type.lower() == 'net':
                self.__type = Net
        else:
            self.__type = bit_type
        self.__signed = signed

        if isinstance(width, tuple):
            self.__msb = max(width)
            self.__lsb = min(width)
        elif isinstance(width, int):
            self.__msb = width-1
            self.__lsb = 0
        else:
            raise Exception('type of width unsupported - should be tuple or int')

        self.associate(associate_with)

        # self.__bits = [None] * self.width()
        self.__bits = {}

        for i in self.indices():
            self.set_bit(i, self.__type(name + '[' + str(i) + ']', self))
        self.__properties = {}

    def get_name(self):
        return self.__name

    def get_object_name(self):
        return self.get_name()

    def msb(self):
        return self.__msb

    def lsb(self):
        return self.__lsb

    def width(self):
        return (self.msb() - self.lsb() + 1)

    def get_width(self):
        return self.width()

    def indices(self):
        return range(self.lsb(), self.msb() + 1)

    def set_bit(self, i, obj):
        if obj.is_associated() and obj.associated_with() != self:
            raise Exception('bit should be associated with bus')
        else:
            obj.associate(self)

        if self.__type != type(obj):
            raise Exception('added bit should be of same type as bus')

        self.__bits[i] = obj

    def verilog_type(self):
        return self.get_bit(self.lsb()).verilog_type()

    def verilog_port_list(self, p):
        if p is self.get_bit(self.lsb()):
            return self.__name
        else:
            return None

    def verilog_declare(self, p):
        if p is self.get_bit(self.lsb()):
            return self.verilog_type() + self.signedness_declare() + ' [' + str(self.msb()) + ':' + str(self.lsb()) + '] ' + self.__name + ';'
        else:
            return None

    def get_bit(self, i):
        return self.__bits[i]

    def all_bits(self, msb2lsb_order=True):
        return (self.get_bit(i) for i in sorted(self.indices(), reverse=msb2lsb_order))

    def is_signed(self):
        return self.__signed

    def signedness_declare(self):
        if self.is_signed():
            return ' signed'
        else:
            return ''

    def get_property(self, property):
        return self.__properties.get(property)

    def set_property(self, property, value):
        self.__properties[property] = value
        return self

    def get_properties(self):
        return self.__properties

    def __str__(self):
        return self.__name
