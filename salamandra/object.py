# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import re


class Object(object):
    @staticmethod
    def is_name_valid(name):  # verilog rules
        return re.match(r'(^[a-zA-Z_][a-zA-Z0-9_$]{0,1023}$|^\\\S* $)', name)

    def __init__(self, name):
        # verilog rules
        if not self.is_name_valid(name):
            raise Exception('name "' + name + '" should be as verilog syntax format')
        self.__name = name
        self.__properties = {}

    def get_object_name(self):
        return self.__name

    def set_object_name(self, name):
        if not self.is_name_valid(name):
            raise Exception('name "' + name + '" should be as verilog syntax format')
        self.__name = name

    def get_property(self, property):
        return self.__properties.get(property)

    def set_property(self, property, value):
        self.__properties[property] = value
        return self

    def get_properties(self, filter=None, name_regex=None):
        return self.filter_objects(self.__properties, name_regex=name_regex, filter=filter)

    @staticmethod
    def filter_objects(objects, name_regex=None, filter=None):
        # filter pins/nets/busses with regex or/with lambda filter(using their properties for example)
        if filter is None and name_regex is None:
            return objects
        if name_regex:  # get all objects that matches regex
            if filter is None:
                filter = lambda x: True
            return [obj for obj in objects if filter(obj) and re.match(name_regex, obj.get_object_name())]
        return [obj for obj in objects if filter(obj)]  # get all objects that pass filter

    def __str__(self):
        return self.__name


def slm_sort(pattern=None, addition=None, is_object=False, ignore_error=True):
    # return key to sort, such as subcomponents names as ABC123ABC123ABC123 (for default)
    if not pattern:
        pattern = r'([^\d]+)(\d+)([^\d]+)(\d+)([^\d]+)(\d+)'
    if not addition:
        addition = '0_0_0'
    my_fun = lambda k, v, q=0, p=0, l=0, r=0: [k, int(v), q, int(p), l, int(r)]

    def key(t):
        if is_object:
            t = t.get_object_name()
        try:
            return my_fun(*re.match(pattern, t + addition).groups())
        except AttributeError:  # don't match pattern
            if not ignore_error:
                raise
            return my_fun(*re.match(pattern, 'A' + addition).groups())
    return key
