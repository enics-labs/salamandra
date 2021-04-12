# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import re
from .object import Object
from .bus import Bus
from copy import copy, deepcopy

class Group(Object):
    __global_groups = {}

    @staticmethod
    def get_group_by_name(group_name):
        return Group.__global_groups[group_name]

    def __init__(self, name):
        super(Group, self).__init__(name)

        if name in Group.__global_groups:
            raise Exception('group already defined')
        else:
            Group.__global_groups[name] = self

        self.__subcomponents = {}
        self.__place_type = 'region'    # guide | region | fence
        self.__position = (0.0, 0.0)
        self.__width = 0.0
        self.__height = 0.0

    def set_group_dimensions(self, width, height):
        self.__width = width
        self.__height = height

    def get_group_dimensions(self):
        width = self.__width
        height = self.__height
        return width, height

    def get_position(self):
        return self.__position

    def get_place_type(self):
        return self.__place_type

    def write_tcl_group_definitions_commands(self):
        l = []
        create_group_command = 'createInstGroup'
        add_inst_to_group_command = 'addInstToInstGroup'
        llx = self.get_position()[0]
        lly = self.get_position()[1]
        urx = llx + self.get_group_dimensions()[0]
        ury = lly + self.get_group_dimensions()[1]
        group_box = str(llx)+' '+str(lly)+' '+str(urx)+' '+str(ury)
        l += [create_group_command+' '+self.get_object_name()+' -'+self.get_place_type()+' '+group_box]

        for inst in self.__subcomponents:
            l += [add_inst_to_group_command+' '+self.get_object_name()+' '+inst]

        return l
