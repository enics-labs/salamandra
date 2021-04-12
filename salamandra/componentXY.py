# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from .component import Component
import re
from enum import Enum


class group_type(Enum):
    guide = 1
    region = 2
    fence = 3


class inst_place_type(Enum):
    fixed = 1
    placed = 2


class ComponentXY(Component):
    def __init__(self, name, original=None):
        self.__positions = {}
        self.__pin_positions = {}
        self.__width = 0.0
        self.__height = 0.0
        self.__group = None
        super(ComponentXY, self).__init__(name, original)
        if original is not None:  # copy component
            self.set_component_dimensions(*original.get_component_dimensions())
            for inst, pos in original.get_positions_dict().items():
                self.set_position(inst, pos[0], pos[1], pos[2])
            for pin_name, pin_dict in original.get_pin_positions_dict().items():
                self.set_pin_position(pin_name, pin_dict['assign'], pin_dict['side'], pin_dict['layer'])

    def add_component(self, component, instance_name, xcoord=0.0, ycoord=0.0, xmin=None, ymin=None,
                      xmax=None, ymax=None, fixed_OR_placed='fixed', group_type=None):
        self.add_subcomponent(component, instance_name, xcoord, ycoord, xmin, ymin, xmax, ymax, fixed_OR_placed, group_type)

    def add_subcomponent(self, component, instance_name, xcoord=0.0, ycoord=0.0, xmin=None, ymin=None,
                         xmax=None, ymax=None, fixed_OR_placed='fixed', group_type=None):
        Component.add_subcomponent(self, component, instance_name)
        ComponentXY.set_position(self, instance_name, xcoord, ycoord, xmin, ymin, xmax, ymax, fixed_OR_placed, group_type)

    def get_position(self, inst):
        return self.__positions[inst]

    def set_position(self, instance_name, xcoord=0.0, ycoord=0.0, xmin=None, ymin=None,
                     xmax=None, ymax=None, fixed_OR_placed='fixed', group_type=None):
        if xmin is None: xmin = xcoord
        if xmax is None: xmax = xcoord
        if ymin is None: ymin = ycoord
        if ymax is None: ymax = ycoord
        self.__positions[instance_name] = (xmin, ymin, xmax, ymax, fixed_OR_placed, group_type)
        # print(str(instance_name)+' -> '+str(self.__positions[instance_name]))  # --> for debug

    def set_component_dimensions(self, width, height):
        self.__width = width
        self.__height = height

    def get_component_dimensions(self):
        width = self.__width
        height = self.__height
        return width, height

    def calc_component_dimensions(self):  # calculate component dimensions recursive
        width = 0.0
        height = 0.0
        comp_dict = self.get_subcomponents()
        if len(comp_dict) == 0:  # dictionary is empty --> leaf cell
            return self.get_component_dimensions()
        else:  # not leaf --> recurse
            for inst, comp in comp_dict:
                if isinstance(comp, ComponentXY):
                    x, y = self.get_position(inst)[0:2]
                    w, h = comp.calc_component_dimensions()
                    width = max(width, x+w)
                    height = max(height, y+h)
                else:
                    raise Exception(str(inst)+' is not ComponentXY')
            self.set_component_dimensions(width, height)
        return width, height

    def get_positions_dict(self):
        return self.__positions

    def get_pin_positions_dict(self):
        return self.__pin_positions

    def get_positions_recursive(self, path="", xmin=0.0, ymin=0.0, xmax=0.0, ymax=0.0, fixed_OR_placed='fixed', group_type=None):
        comp_dict = self.get_subcomponents()
        if len(comp_dict) == 0:  # dictionary is empty --> leaf cell
            return [(path, xmin, ymin, xmax, ymax, fixed_OR_placed, group_type)]
        else:  # not leaf --> recurse
            if path != "":
                path += "/"
            l = []
            for inst, comp in comp_dict:
                if isinstance(comp, ComponentXY):
                    inst_position = self.get_position(inst)
                    inst_pos_list = comp.get_positions_recursive(path+inst, xmin + inst_position[0],
                                                                 ymin + inst_position[1], xmax + inst_position[2],
                                                                 ymax + inst_position[3], inst_position[4], inst_position[5])
                    l += inst_pos_list
                else:
                    raise Exception(str(inst)+' is not ComponentXY')
            return l

    def set_pin_position(self, pin_name, xcoord=0.0, ycoord=0.0, side='LEFT', layer=2):
        self.__pin_positions[pin_name] = {}
        self.__pin_positions[pin_name]['assign'] = (xcoord, ycoord)
        self.__pin_positions[pin_name]['side'] = side
        self.__pin_positions[pin_name]['layer'] = layer

    def write_tcl_placement_commands(self, tool, put_placed_inst_in_comment=0):
        place_instance_list = []
        create_group_list = []
        add_inst_to_group_list = []
        groups_dict = {}
        group_index = 0

        if tool == 'Cadence':
            place_command = 'placeInstance'
            for line in self.get_positions_recursive():
                # print(line)
                if line[0] == line[2] or line[1] == line[3]:  # if xmin == xmax or ymin == ymax so regular placeInstance
                    if line[5] == 'placed':
                        place_instance_list += [place_command + ' ' + line[0] + ' [expr ($x_coordinate+' + str(round(line[1], 2)) + ')] [expr ($y_coordinate+' + str(round(line[2], 2)) + ')] -placed']
                    elif line[5] == 'fixed':
                        place_instance_list += [place_command + ' ' + line[0] + ' [expr ($x_coordinate+' + str(round(line[1], 2)) + ')] [expr ($y_coordinate+' + str(round(line[2], 2)) + ')] -fixed']
                    else:
                        place_instance_list += [place_command + ' ' + line[0] + ' [expr ($x_coordinate+' + str(round(line[1], 2)) + ')] [expr ($y_coordinate+' + str(round(line[2], 2)) + ')]']

                    if put_placed_inst_in_comment == 1 and line[5] == 'placed':
                        place_instance_list[-1] = '# '+place_instance_list[-1]
                else:
                    group_exist = 0
                    for group in groups_dict:
                        if groups_dict[group]['box'] == (line[1], line[2], line[3], line[4]):
                            groups_dict[group]['inst_list'] += [line[0]]
                            group_exist = 1
                    if group_exist == 0:
                        groups_dict[group_index] = {}
                        groups_dict[group_index]['box'] = (line[1], line[2], line[3], line[4])
                        groups_dict[group_index]['inst_list'] = [line[0]]
                        group_index += 1
            print(groups_dict)
            for group in groups_dict:
                create_group_command = 'createInstGroup'
                box = str(groups_dict[group]['box'][0])+' '+str(groups_dict[group]['box'][1])+' '+str(groups_dict[group]['box'][2])+' '+str(groups_dict[group]['box'][3])
                create_group_list += [create_group_command+' '+str(group)+' -fence {'+box+'}']
                for inst in groups_dict[group]['inst_list']:
                    add_inst_to_group_list += ['addInstToInstGroup'+' '+str(group)+' '+inst]

        elif tool == 'Synopsys':
            place_command = 'move_objects'
            for line in self.get_positions_recursive():
                if line[5] == 1:
                    place_instance_list += [place_command + ' [get_flat_cells ' + line[0] + '] -x [expr ($x_coordinate+' + str(round(line[1], 2)) + ')] -y [expr ($y_coordinate+' + str(round(line[2], 2)) + ')] -placed']
                else:
                    place_instance_list += [place_command + ' [get_flat_cells ' + line[0] + '] -x [expr ($x_coordinate+' + str(round(line[1], 2)) + ')] -y [expr ($y_coordinate+' + str(round(line[2], 2)) + ')]']

        return place_instance_list, create_group_list, add_inst_to_group_list

    def write_pin_tcl_placement_commands(self):
        l = []
        place_command = 'editPin'
        pin_dict = self.get_pin_positions_dict()
        for pin in sorted(pin_dict):
            l += [place_command + ' -pin "' + str(pin) + '" -layer ' + str(pin_dict[pin]['layer']) + ' -side '+str(pin_dict[pin]['side'])+' -assign '+ str(round(pin_dict[pin]['assign'][0],2))+' '+str(round(pin_dict[pin]['assign'][1],2))+' -snap TRACK -fixOverlap']
        return l

    def write_floorPlan_tcl_commands(self, tech_site):
        self.calc_component_dimensions()
        dimensions = self.get_component_dimensions()
        l = 'floorPlan -site '+str(tech_site)+' -adjustToSite -s '+' [expr ($floorPlan_margin_x+' + str(round(dimensions[0],2))+')] [expr ($floorPlan_margin_y+'+str(round(dimensions[1],2))+')] 0 0 0 0'
        return l

    def write_addStripe_tcl_commands(self, welltap_width=0.4, min_stripe_spacing=0.1, min_stripe_width=0.1):
        l = []
        place_command = 'addStripe'
        # Calculations:
        stripe_width = (welltap_width - min_stripe_spacing)/2
        stripe_width = max(stripe_width,min_stripe_width)
        two_stripe_width = min_stripe_spacing + (2*stripe_width)
        print('\n==========+=============')
        dict_ = self.get_subcomponents()
        for k in sorted(dict_):
            # if dict_[k].get_object_name() == 'welltap_stripe':
            if re.match('welltap_stripe', dict_[k][1].get_object_name()):
                x_pos = round(self.get_positions_dict()[k][0],2)
                stripe_area = str(x_pos) + ' 0.0 '+ str(round(x_pos + 0.4,2)) +' '+ str(round(self.get_subcomponent(k).get_component_dimensions()[1],2))
                print(k+'\t->\tstripe_area: '+str(stripe_area))
                l += [place_command + ' -nets {gnd vdd} -layer M2 -direction vertical -width "'+str(round(stripe_width,2))+' '+str(round(stripe_width,2))+'" -spacing '+str(round(min_stripe_spacing,2))+' -number_of_sets 1 -area "'+ stripe_area +'" -start_offset 0']
        return l

