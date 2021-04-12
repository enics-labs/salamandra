# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import re
from .object import Object, slm_sort
from .pin import Pin
from .net import Net
from .gnet import GNet
from .bus import Bus
from .input import Input
from .output import Output
from .inout import Inout
from copy import copy, deepcopy
from collections import defaultdict


class Component(Object):
    HIERARCHICAL_SEPARATOR = '.'
    PIN_SEPARATOR = '.'
    VIRTUAL_COMP_NAME = 'virtual_comp'
    COLLISION_NAME = '_$NAME$_'
    
    __global_components = {}
    __count_UC_nets = 0
    __count_VIRT_comps = 0
    __count_collision = 0

    @staticmethod
    def all_components():
        return Component.__global_components

    @staticmethod
    def save(filename):
        import pickle
        with open(filename, 'wb') as f:
            pickle.dump(Component.__global_components, f)

    @staticmethod
    def load(filename):
        import pickle
        with open(filename, 'rb') as f:
            Component.__global_components = pickle.load(f)

    @staticmethod
    def get_component_by_name(comp_name):
        if comp_name not in Component.__global_components:
            raise Exception('cant find component - ' + comp_name)
        return Component.__global_components[comp_name]

    @staticmethod
    def delete_component_by_name(comp_name):
        del Component.__global_components[comp_name]

    @staticmethod
    def delete_component(comp):
        del Component.__global_components[comp.get_object_name()]

    @staticmethod
    def delete_all_components():
        # TODO run on dictionary and call destructor of all components first
        Component.__global_components = {}

    def __init__(self, name, original=None):
        super(Component, self).__init__(name)

        if name in Component.__global_components:
            raise Exception('component already defined')
        else:
            Component.__global_components[name] = self

        self.__pins = {}
        self.__nets = {}
        self.__netbusses = {}
        self.__pinbusses = {}
        self.__subcomponents = {}
        self.__net_connectivity = {}
        self.__pin_connectivity = {}
        self.__virtual_pins = {}
        self.__pins_ordered = []
        self.add_pin_adds_net = True
        self.__dont_uniq = False
        self.__dont_write_verilog = False
        self.__is_physical = False
        self.__is_sequential = False
        self.__verilog_code = None
        self.__spectre_code = None
        # add Global Nets
        self.add_net(GNet("1'b0"))
        self.add_net(GNet("1'b1"))
        self.add_net(GNet("1'bx"))

        if original is not None:
            # copy regular variables
            self.add_pin_adds_net = original.add_pin_adds_net
            self.set_dont_uniq(original.get_dont_uniq())
            self.set_dont_write_verilog(original.get_dont_write_verilog())
            self.set_is_physical(original.get_is_physical())
            self.set_is_sequential(original.get_is_sequential())
            v_code = original.get_verilog_code()
            s_code = original.get_spectre_code()
            self.__verilog_code = v_code.copy() if v_code else None
            self.__spectre_code = s_code.copy() if s_code else None
            # copy pins
            for pin_str in original.pin_names():
                pin = original.get_pin(pin_str)
                if pin.is_part_of_bus():
                    if pin_str not in self.pin_names():
                        p_bus = pin.bus()
                        self.add_pinbus(Bus(p_bus.verilog_type(), p_bus.get_name(), p_bus.get_width()))
                else:
                    self.add_pin(type(pin)(pin_str))
            # copy nets
            for net_str in original.net_names():
                if net_str not in self.net_names():
                    net = original.get_net(net_str)
                    if original.get_net(net_str).is_part_of_bus():
                        n_bus = net.bus()
                        self.add_netbus(Bus(Net, n_bus.get_name(), n_bus.get_width()))
                    else:
                        self.add_net(Net(net_str))
            # copy subcomponents
            for sub_str, sub in original.get_subcomponents():
                self.add_subcomponent(sub, sub_str)
            # add/remove connectivity
            for net_str in original.net_names():
                my_net = self.get_net(net_str)
                original_net = original.get_net(net_str)
                if original_net not in original.__net_connectivity:
                    continue
                if my_net not in self.__net_connectivity:
                    self.__net_connectivity[my_net] = []
                # for every net, check all the pins that connected to it in self and see if they exist
                # in connectivity in original, if not - disconnect it in self.
                for pin_str in [pin.get_object_name() for pin in self.__net_connectivity[my_net]]:
                    if pin_str not in [pin.get_object_name() for pin in original.get_net_connectivity(original_net)]:
                        self.disconnect(pin_str)
                # for every net, check all the pins that connected to it in original and see if they exist
                # in connectivity in self, if not - connect it in self.
                for pin_str in [pin.get_object_name() for pin in original.get_net_connectivity(original_net)]:
                    if pin_str not in [pin.get_object_name() for pin in self.__net_connectivity[my_net]]:
                        self.connect(net_str, pin_str)
            # copy properties dictionary
            if original.get_properties():
                self._Object__properties = deepcopy(original.get_properties())

    def is_virtual(self):
        return False

    def get_pin(self, pin_name):
        return self.__pins[pin_name]

    def get_pins(self, filter=None, name_regex=None):
        return self.filter_objects(self.__pins.values(), name_regex=name_regex, filter=filter)

    def get_pins_ordered(self, filter=None, name_regex=None):
        return self.filter_objects(self.__pins_ordered, name_regex=name_regex, filter=filter)

    def pin_names(self):
        return self.__pins.keys()

    def get_pinbus(self, pinbus_name):
        return self.__pinbusses[pinbus_name]

    def get_pinbusses(self, filter=None, name_regex=None):
        return self.filter_objects(self.__pinbusses.values(), name_regex=name_regex, filter=filter)

    def pinbus_names(self):
        return self.__pinbusses.keys()

    def add_pin(self, pin):
        if not isinstance(pin, Pin):
            raise Exception('not a pin')
        pin_name = pin.get_object_name()
        if pin_name in self.pin_names():
            raise Exception('pin "'+pin_name+'" already exists in component')
        if pin_name in self.pinbus_names():
            raise Exception('pin "'+pin_name+'" already exists as pinbus in component')

        pin.associate(self)
        self.__pins[pin_name] = pin

        if self.add_pin_adds_net and not pin.is_part_of_bus():
            # add net with the same name as the pin
            n = pin_name
            if n not in self.net_names():
                self.add_net(Net(n))
            self.connect(n, n)

        self.__pins_ordered.append(pin)

    def add_pinbus(self, pinbus, msb2lsb_declaration=True):
        # msb2lsb_declaration flag: add_pin in reverse order (for spectre)
        if not isinstance(pinbus, Bus):
            raise Exception('not a bus')
        pinbus_name = pinbus.get_name()
        if pinbus_name in self.pinbus_names():
            raise Exception('pinbus "'+pinbus_name+'" already exists in component')
        if pinbus_name in self.pin_names():
            raise Exception('pinbus "'+pinbus_name+'" already exists as pin in component')

        # temporarily disable add_pin_adds_net feature so that pinbus is connected to
        # netbus (later, and not to nets that are not part of bus)
        temp = self.add_pin_adds_net
        self.add_pin_adds_net = False
        for p in pinbus.all_bits(msb2lsb_order=msb2lsb_declaration):
            self.add_pin(p)
        self.add_pin_adds_net = temp
        
        pinbus.associate(self)
        self.__pinbusses[pinbus_name] = pinbus

        if self.add_pin_adds_net:
            # add netbus with the same name as the pinbus
            n = pinbus_name
            if n not in self.netbus_names():
                self.add_netbus(Bus(Net, n, (pinbus.msb(), pinbus.lsb()), signed=pinbus.is_signed()))
            self.connect_bus(n, n)

    def set_param(self, key, param, value):
        if key not in self.get_properties():
            self.set_property(key, {})  # create key dict if not exist
        self.get_property(key)[param] = value

    def get_param(self, key, param):
        return self.get_property(key)[param]

    def get_params(self, key):
        params = self.get_property(key)
        if not params:  # if None, return empty list
            return []
        return params

    def set_spice_param(self, param, value):
        self.set_param('spice', param, value)

    def get_spice_param(self, param):
        return self.get_param('spice', param)

    def get_spice_params(self):
        return self.get_params('spice')

    def get_net(self, net_name):
        return self.__nets[net_name]

    def get_nets(self, filter=None, name_regex=None):
        return self.filter_objects(self.__nets.values(), name_regex=name_regex, filter=filter)

    def net_names(self):
        return self.__nets.keys()

    def get_netbus(self, netbus_name):
        return self.__netbusses[netbus_name]

    def get_netbusses(self, filter=None, name_regex=None):
        return self.filter_objects(self.__netbusses.values(), name_regex=name_regex, filter=filter)

    def netbus_names(self):
        return self.__netbusses.keys()

    def get_net_connectivity(self, net):
        return self.__net_connectivity[self.__2net(net)]

    def add_net(self, net):
        if not isinstance(net, Net):
            raise Exception('not a net')
        net_name = net.get_object_name()
        if net_name in self.net_names():
            raise Exception('net "'+net_name+'" already exists in component')
        if net_name in self.netbus_names():
            raise Exception('net "'+net_name+'" already exists as netbus in component')

        net.associate(self)
        self.__nets[net_name] = net

    def add_netbus(self, netbus):
        if not isinstance(netbus, Bus):
            raise Exception('not a bus')
        netbus_name = netbus.get_name()
        if netbus_name in self.netbus_names():
            raise Exception('netbus "'+netbus_name+'" already exists in component')
        if netbus_name in self.net_names():
            raise Exception('netbus "'+netbus_name+'" already exists as net in component')

        for n in netbus.all_bits():
            self.add_net(n)

        netbus.associate(self)
        self.__netbusses[netbus_name] = netbus

    def subcomponent_names(self):
        return [*self.__subcomponents]

    def get_subcomponent(self, inst_name):
        try:
            return Component.get_component_by_name(self.__subcomponents[inst_name])
        except:
            raise Exception('sub-component [' + inst_name + '] not found')

    def get_subcomponents(self, filter=None, inst_name_regex=None):
        # get list of subcomponents names and their component as tuples if component pass filter
        if filter:
            if inst_name_regex:  # also if inst_name matches pattern
                return [(inst, dev) for inst, dev in self.get_subcomponents()
                        if filter(dev) and re.match(inst_name_regex, inst)]
            return [(inst, dev) for inst, dev in self.get_subcomponents() if filter(dev)]
        elif inst_name_regex:
            return [(inst, dev) for inst, dev in self.get_subcomponents() if re.match(inst_name_regex, inst)]
        # get list of subcomponents names and their component as tuples
        return [(inst, self.get_subcomponent(inst)) for inst in self.__subcomponents]

    def get_descendants_hierarchy(self, filter=None):
        # add direct subcomponents
        dic = {}
        for inst, dev in self.get_subcomponents(filter=filter):
            dic[inst] = dev

        # add indirect (subcomponents of subcomponents)
        for inst, dev in self.get_subcomponents():
            dic_of_subcomp = dev.get_descendants_hierarchy(filter=filter)
            for inner_inst, inner_dev in dic_of_subcomp.items():
                dic[inst + Component.HIERARCHICAL_SEPARATOR + inner_inst] = inner_dev
        return dic

    def get_descendants(self, inclusive=False, filter=None, dev_name_regex=None):
        s = set(self.get_descendants_hierarchy().values())
        s = set(self.filter_objects(s, name_regex=dev_name_regex, filter=filter))
        if inclusive:
            s.add(self)
        return s

    def add_component(self, component, instance_name):
        self.add_subcomponent(component, instance_name)

    def add_subcomponent(self, component, instance_name):
        if not isinstance(component, Component):
            raise Exception('not a component')
        # verilog rules
        if not component.is_name_valid(instance_name):
            raise Exception('name "' + instance_name + '" should be as verilog syntax format')

        if instance_name in self.__subcomponents:
            raise Exception('component ['+instance_name+'] already exists')
        else:
            self.__subcomponents[instance_name] = component.get_object_name()

    def remove_subcomponent(self, instance_name):
        if instance_name not in self.__subcomponents:
            raise Exception('component ['+instance_name+'] not found in ['+self.get_object_name()+']')
        sub = self.get_subcomponent(instance_name)
        # remove connectivity (disconnect his virtual pins)
        for pin in sub.pin_names():
            vp = (instance_name, pin)
            if vp in self.__virtual_pins:
                self.disconnect(self.__virtual_pins[vp])
        del self.__subcomponents[instance_name]

    def remove_subcomponents(self):
        for instance_name in list(self.__subcomponents.keys()):
            self.remove_subcomponent(instance_name)

    def connect(self, net, pin_str):
        if not isinstance(pin_str, str):
            raise Exception('pin_str should be string')
        net = self.__2net(net)  # get Net object if it was string(its name)
        str2pin_dict = self.__2pin(pin_str)

        # Errors
        if str2pin_dict['is_pin_of_subcomponent'] and str2pin_dict['already_connected']:
            raise Exception('[' + str2pin_dict['subcomponent_str'] + Component.PIN_SEPARATOR +
                            str2pin_dict['subcomponent_pin_str'] + '] already connected')

        # connect
        pin = str2pin_dict['pin']
        if pin in self.__pin_connectivity:
            raise Exception('pin already connected')

        if net not in self.__net_connectivity:
            self.__net_connectivity[net] = []

        self.__net_connectivity[net].append(pin)
        self.__pin_connectivity[pin] = net

    def disconnect(self, pin):
        str2pin_dict = self.__2pin(pin)
        # Errors
        if not str2pin_dict['is_pin_of_subcomponent']:
            raise Exception('cannot disconnect primary pin [' + pin + '] from net!')
        if not str2pin_dict['already_connected']:
            raise Exception('[' + str2pin_dict['subcomponent_str'] + Component.PIN_SEPARATOR +
                            str2pin_dict['subcomponent_pin_str'] + '] not found as connected')
        pin = str2pin_dict['pin']
        if pin not in self.__pin_connectivity:
            raise Exception('pin not connected')

        # disconnect - delete virtual pin and net/pin connectivity
        del self.__virtual_pins[(str2pin_dict['subcomponent_str'], str2pin_dict['subcomponent_pin_str'])]
        net = self.__pin_connectivity[pin]
        self.__net_connectivity[net].remove(pin)
        del self.__pin_connectivity[pin]

    def disconnect_bus(self, pinbus_str):
        if not isinstance(pinbus_str, str):
            raise Exception('pinbus_str should be a string')

        # TODO: need to implement disconnect primary busses
        str2pin_dict = self.__2pinbus(pinbus_str)

        # disconnect bus
        pinbus = str2pin_dict['pinbus']
        inst = str2pin_dict['subcomponent_str'] if str2pin_dict['is_pin_of_subcomponent'] else pinbus_str
        for p in pinbus.all_bits():
            self.disconnect(inst + Component.PIN_SEPARATOR + p.get_object_name())

    def connect_bus(self, netbus, pinbus_str):
        if not isinstance(pinbus_str, str):
            raise Exception('pinbus_str should be a string')

        netbus = self.__2netbus(netbus)  # get Bus object if it was string(its name)
        str2pin_dict = self.__2pinbus(pinbus_str)

        # Errors
        if not str2pin_dict['is_pin_of_subcomponent'] and str2pin_dict['netbus'] == 'not found':
            raise Exception('cannot find netbus [' + pinbus_str + '] in component')

        # connect bus
        pinbus = str2pin_dict['pinbus']
        netbus = str2pin_dict['netbus'] if not str2pin_dict['is_pin_of_subcomponent'] else netbus

        if netbus.width() == pinbus.width():
            for n, p in zip(netbus.all_bits(), pinbus.all_bits()):
                if not str2pin_dict['is_pin_of_subcomponent']:
                    self.connect(n.get_object_name(), p.get_object_name())
                else:
                    self.connect(n.get_object_name(), str2pin_dict['subcomponent_str'] + Component.PIN_SEPARATOR + p.get_object_name())
        else:
            raise Exception('bus widths does not match')

    def connect_nets(self, input_net, output_net):
        from .componentVIRT import ComponentVIRT
        input_net = self.__2net(input_net)
        output_net = self.__2net(output_net)
        name = Component.VIRTUAL_COMP_NAME + str(Component.__count_VIRT_comps)
        self.add_subcomponent(ComponentVIRT(name, self, input_net, output_net), name)
        self.connect(input_net, name + Component.PIN_SEPARATOR + 'I')
        self.connect(output_net, name + Component.PIN_SEPARATOR + 'O')
        Component.__count_VIRT_comps += 1

    def connect_netbusses(self, input_netbus, output_netbus):
        input_netbus = self.__2netbus(input_netbus)
        output_netbus = self.__2netbus(output_netbus)
        if input_netbus.width() != output_netbus.width():
            raise Exception('input_netbus and output_netbus should have the same width')
        for input_net, output_net in zip(input_netbus.all_bits(), output_netbus.all_bits()):
            self.connect_nets(input_net, output_net)

    def __2net(self, net):  # return net from net_str/Net
        if isinstance(net, str):
            try:
                return self.get_net(net)
            except:
                raise Exception('cannot find net [' + net + '] in component')
        elif isinstance(net, Net):
            try:
                if net is self.get_net(net.get_object_name()):
                    return net
                else:
                    raise
            except:
                raise Exception('cant find net [' + net.get_object_name() + '] in component')
        else:
            raise Exception('net should be string or Net')

    def __2netbus(self, netbus):  # return netbus from net_str/Bus
        if isinstance(netbus, str):
            try:
                return self.get_netbus(netbus)
            except:
                raise Exception('cannot find netbus [' + netbus + '] in component')
        elif isinstance(netbus, Bus):
            try:
                if netbus is self.get_netbus(netbus.get_name()):
                    return netbus
                else:
                    raise
            except:
                raise Exception('cannot find netbus [' + netbus.get_name() + '] in component')
        else:
            raise Exception('netbus should be string or Bus')

    def __2pin(self, pin):
        # method that gets pin and return it as a Pin (or virtual pin)
        str2pin_dict = {}
        if isinstance(pin, str):
            lpin = pin.split(Component.PIN_SEPARATOR)  # like nand.A
            if len(lpin) == 1:  # pin of component
                str2pin_dict['is_pin_of_subcomponent'] = False
                try:
                    str2pin_dict['pin'] = self.get_pin(pin)
                except:
                    raise Exception('cannot find pin [' + pin + '] in component')

            elif len(lpin) == 2:  # pin of sub-component
                inst, inst_pin = lpin  # lpin[0]=instance name, lpin[1]=pin name
                str2pin_dict['is_pin_of_subcomponent'] = True
                str2pin_dict['subcomponent_str'] = inst
                str2pin_dict['subcomponent_pin_str'] = inst_pin
                sub = self.get_subcomponent(inst)
                try:
                    str2pin_dict['pin'] = sub.get_pin(inst_pin)
                except:
                    raise Exception('pin [' + inst_pin + '] not found in sub-component [' + inst + ']')

                # Virtual pin ("pointer" to the actual pin(that inside sub-component))
                if (inst, inst_pin) not in self.__virtual_pins:  # for connect method
                    str2pin_dict['already_connected'] = False
                    virtual_pin = Pin(inst+Component.PIN_SEPARATOR+inst_pin, is_virtual=True, associated_comp=sub, associated_pin=str2pin_dict['pin'])
                    self.__virtual_pins[(inst, inst_pin)] = virtual_pin
                    str2pin_dict['pin'] = virtual_pin
                else:
                    str2pin_dict['already_connected'] = True
                    str2pin_dict['pin'] = self.__virtual_pins[(inst, inst_pin)]

            else:  # too deep
                raise Exception(pin + ' is too deep')

        elif isinstance(pin, Pin):
            if not pin.is_virtual():
                str2pin_dict['is_pin_of_subcomponent'] = False
                str2pin_dict['pin'] = pin
            else:
                lpin = pin.get_object_name().split(Component.PIN_SEPARATOR)
                if len(lpin) != 2:
                    raise Exception(pin.get_object_name() + ' is too deep')
                inst, inst_pin = lpin
                str2pin_dict['is_pin_of_subcomponent'] = True
                str2pin_dict['subcomponent_str'] = inst
                str2pin_dict['subcomponent_pin_str'] = inst_pin
                if (inst, inst_pin) in self.__virtual_pins:
                    str2pin_dict['already_connected'] = True
                    str2pin_dict['pin'] = pin
                else:
                    raise Exception('got virtual pin that doesnt in virtual_pins of component')  # add to virtual_pins instead?
        else:
            raise Exception('pin should be a string or Pin')

        return str2pin_dict

    def __2pinbus(self, pinbus):
        # method that gets pinbus and return it as a Pin(Bus)
        str2pin_dict = {}
        if isinstance(pinbus, str):
            lpin = pinbus.split(Component.PIN_SEPARATOR)  # like nand.A
            if len(lpin) == 1:  # pin of component
                str2pin_dict['is_pin_of_subcomponent'] = False
                try:
                    str2pin_dict['pinbus'] = self.get_pinbus(pinbus)
                except:
                    raise Exception('cannot find pinbus [' + pinbus + '] in component')
                try:
                    str2pin_dict['netbus'] = self.get_netbus(pinbus)
                except:
                    str2pin_dict['netbus'] = 'not found'

            elif len(lpin) == 2:  # pin of sub-component
                inst, inst_pin = lpin  # lpin[0]=instance name, lpin[1]=pin name
                str2pin_dict['is_pin_of_subcomponent'] = True
                str2pin_dict['subcomponent_str'] = inst
                str2pin_dict['subcomponent_pin_str'] = inst_pin
                sub = self.get_subcomponent(inst)
                try:
                    str2pin_dict['pinbus'] = sub.get_pinbus(inst_pin)
                except:
                    raise Exception('pinbus [' + inst_pin + '] not found in sub-component [' + inst + ']')
            else:  # too deep
                raise Exception(pinbus + ' is too deep')

        elif isinstance(pinbus, Bus):
            str2pin_dict['pinbus'] = pinbus
        else:
            raise Exception('pinbus should be a string or Bus')

        return str2pin_dict

    def count_instances(self):
        # first count the module itself
        count = {self.get_object_name(): 1}
        # then add the sub-counts from submodules
        for inst, dev in self.get_subcomponents():
            sub_count = dev.count_instances()
            for m in sub_count:
                if m in count:
                    count[m] += sub_count[m]
                else:
                    count[m] = sub_count[m]
        return count

    def copy(self, copy_name):
        # use `new_dev = Component(copy_name, original=old_dev)` instead
        if copy_name in Component.__global_components:
            raise Exception('component ['+copy_name+'] already exists')
        new_dev = copy(self)
        new_dev.set_object_name(copy_name)
        Component.__global_components[copy_name] = new_dev
        return new_dev

    def deepcopy(self, copy_name):
        # use `new_dev = Component(copy_name, original=old_dev)` instead
        if copy_name in Component.__global_components:
            raise Exception('component ['+copy_name+'] already exists')
        new_dev = deepcopy(self)
        new_dev.set_object_name(copy_name)
        Component.__global_components[copy_name] = new_dev
        return new_dev

    def set_dont_uniq(self, val):
        self.__dont_uniq = val

    def get_dont_uniq(self):
        return self.__dont_uniq

    def set_dont_write_verilog(self, val):
        self.__dont_write_verilog = val

    def get_dont_write_verilog(self):
        return self.__dont_write_verilog

    def set_is_physical(self, val):
        self.__is_physical = val

    def get_is_physical(self):
        return self.__is_physical

    def set_is_sequential(self, val):
        self.__is_sequential = val

    def get_is_sequential(self):
        return self.__is_sequential

    def uniq(self, count=None, numbering=None):
        # uniqueness instances in component, e.g. every instance of component will be uniq(new component)
        # topmost component counts, all others should get count from above
        if not count:
            count = self.count_instances()
        # same as count, the one that counts should setup the numbering
        if not numbering:
            numbering = {}
            for k in count:
                numbering[k] = 0
                # make sure k_# not already used
                while k+"_"+str(numbering[k]) in Component.__global_components:
                    numbering[k] +=1

        for inst in sorted(self.subcomponent_names(), key=slm_sort()):
            dev = self.get_subcomponent(inst)
            devname = dev.get_object_name()
            if count[devname]>1 and not dev.get_dont_uniq():
                new_devname = devname+"_"+str(numbering[devname])
                new_dev = type(self)(new_devname, dev)
                self.__subcomponents.update({inst: new_devname})
                # self.add_subcomponent(inst, new_dev)
                # the new devname is missing from count dictionary
                count[new_devname] = 1
                # increment numbering to next available number
                while True:
                    numbering[devname] += 1
                    next_devname_uniq = devname+"_"+str(numbering[devname])
                    if next_devname_uniq not in Component.__global_components:
                        break
                dev = new_dev
            dev.uniq(count, numbering)

    def verilog_port_list(self):
        return [x for x in [pl.verilog_port_list() for pl in self.get_pins()] if x is not None]

    def __is_inst_bus_connected_any(self, inst, inst_bus):  # check if inst_bus is connected, at least 1 bit
        count_bits_uc = 0
        for inst_pin in inst_bus.all_bits():
            if (inst, inst_pin.get_object_name()) not in self.__virtual_pins:
                count_bits_uc += 1  # count bits that not connected
        return not count_bits_uc == inst_bus.width()  # true if at least 1 bit unconnected

    def legalize(self):
        # check if the component is legal by checking some rules
        self_instantiation = self.check_self_instantiations()
        if self_instantiation:
            raise Exception('self instantiations: "{}" cant have subcomponent of itself '
                            '(either direct or a subcomponent of a subcomponent)'.format(self_instantiation))
        self.check_if_instances_not_exist()
        asymmetry_name = self.check_pins_nets_names_asymmetry()
        if asymmetry_name:
            raise Exception('asymmetry name "{}" - cant hold net/pin with a different name from his'.format(asymmetry_name))
        duplicate_name = self.check_duplicate_names()
        if duplicate_name:
            raise Exception('duplicate name "{}" - is a name of instance and also a wire'.format(duplicate_name))
        multidriven = self.check_multidriven()
        if multidriven:
            raise Exception('net "{}" is driven by multiple drivers: {}'.format(multidriven[0], multidriven[1]))
        self.connect_half_unconnected_pinbusses()

    def check_multidriven(self):
        # check if net is driven by more then 2 Input, Output of subcomponent or assignment from net
        for net, pins in self.__net_connectivity.items():
            drivers = []
            for p in pins:
                if type(p) == Input or (p.is_virtual() and type(p.get_associated_pin()) == Output):
                    if p.is_virtual() and p.get_associated_comp().is_virtual():  # check if its assignment from net
                        drivers.append(p.get_associated_comp().input_net.get_object_name())
                    else:
                        drivers.append(p.get_object_name())
            if len(drivers) > 1:
                return net, drivers

    def check_duplicate_names(self):
        # check if there is an instance and wire with the same name
        instances = [*self.subcomponent_names(), self.get_object_name()]
        wires = self.net_names()
        for inst in instances:
            if inst in wires:
                return inst
        return None

    def check_pins_nets_names_asymmetry(self):
        # check if names of pin/net/bus in self.__nets/pins/bus is the same as their actual names
        items = list(self.__pins.items())+list(self.__nets.items())+list(self.__pinbusses.items())+list(self.__netbusses.items())
        for str_, obj in items:
            if str_ != obj.get_object_name():
                return obj

    def check_if_instances_not_exist(self):
        self.get_descendants()

    def check_self_instantiations(self):
        comps = [('', self)]
        ancestors = {('', self): []}
        for inst, sub in comps:
            for inner_inst, inner_sub in sub.get_subcomponents():
                comps.append((inner_inst, inner_sub))
                ancestors[(inner_inst, inner_sub)] = [(inst, sub)]
                ancestors[(inner_inst, inner_sub)].extend(ancestors[(inst, sub)])
                if inner_sub in [c[1] for c in ancestors[(inner_inst, inner_sub)]]:
                    return inner_sub

    def connect_half_unconnected_pinbusses(self):
        # connect half-unconnected pinbusses. inputs to 1'bx, outputs/inouts to UC_# wires
        for inst, dev in self.get_subcomponents():
            for inst_bus in set([p.bus() for p in dev.get_pins() if p.is_part_of_bus()]):
                if self.__is_inst_bus_connected_any(inst, inst_bus):  # not all unconnected
                    for inst_pin in inst_bus.all_bits():
                        inst_pin_name = inst_pin.get_object_name()
                        if (inst, inst_pin_name) not in self.__virtual_pins:  # unconnected pin
                            if type(inst_pin) == Input:
                                self.connect("1'bx", inst + Component.PIN_SEPARATOR + inst_pin_name)
                            else:  # output/inout
                                n_name = 'UC_{}'.format(Component.__count_UC_nets)
                                self.add_net(Net(n_name))
                                self.connect(n_name, inst + Component.PIN_SEPARATOR + inst_pin_name)
                                Component.__count_UC_nets += 1

    def hilomap(self, tiehi=None, tielo=None, inst_per_comp=True):
        # map constants('1', '0') to 'tiehi' and 'tielo' driver cells, respectively.
        gnet1 = self.get_net("1'b1")
        gnet0 = self.get_net("1'b0")
        if inst_per_comp is True:
            for gnet_, tie, net_str in zip([gnet1, gnet0], [tiehi, tielo], ['HI', 'LO']):
                if tie is not None and gnet_ in self.__net_connectivity:
                    tie_str = tie.get_object_name()
                    # check for outputs in tie
                    tie_pin_o = tie.get_pins(filter=lambda p: isinstance(p, Output))
                    if len(tie_pin_o) != 1:
                        raise Exception(tie_str + 'should have 1 output')
                    tie_pin_o = tie_pin_o[0]

                    self.add_subcomponent(tie, tie_str)
                    self.add_net(Net(net_str))
                    self.connect(net_str, tie_str + Component.PIN_SEPARATOR + tie_pin_o.get_object_name())
                    for pin in self.get_net_connectivity(gnet_)[:]:  # iterate over its copy, because its changing
                        pin_str = pin.get_object_name()
                        self.disconnect(pin)
                        self.connect(net_str, pin_str)

            # replace all assignments to constants to tielo or tiehi
            filter = lambda c: c.is_virtual() and isinstance(c.input_net, GNet)
            for virt_inst, virt_sub in self.get_subcomponents(filter=filter):
                if virt_sub.input_net.get_object_name() == "1'b1":
                    self.connect_nets(self.get_net('HI'), virt_sub.output_net)
                else:
                    self.connect_nets(self.get_net('LO'), virt_sub.output_net)
                self.remove_subcomponent(virt_inst)

    def print_verilog(self, include_descendants=False, filter=None):
        if include_descendants:
            for comp in sorted(self.get_descendants(inclusive=True, filter=filter), key=slm_sort(is_object=True)):  # sort by names
                if comp.get_dont_write_verilog():
                    continue
                for line in comp.write_verilog():
                    print(line)
        else:
            for line in self.write_verilog():
                print(line)

    def write_verilog_to_file(self, path=None, append=False, include_descendants=False, filter=None):
        text = ''
        if include_descendants:
            for comp in sorted(self.get_descendants(inclusive=True, filter=filter), key=slm_sort(is_object=True)):  # sort by names
                if comp.get_dont_write_verilog():
                    continue
                for line in comp.write_verilog():
                    text += line + '\n'
        else:
            for line in self.write_verilog():
                text += line + '\n'
        if path:
            with open(path, 'a' if append else 'w') as f:
                f.write(text)
        else:
            return text

    def write_verilog(self):
        v = []
        mod_def = '\nmodule ' + self.get_object_name() + ' ('
        ports = ', '.join(sorted(self.verilog_port_list(), key=slm_sort()))
        mod_def += ports + ');'
        for ll in Component.line_wrap(mod_def):
            v.append(ll)

        # ports
        if self.__pins:
            v.append('')
            v.append('\t//ports')

        for pin in sorted(self.get_pins()):
            pin_dec = pin.verilog_declare()
            if pin_dec:
                v.append('\t' + pin_dec)

        # wires
        if self.__nets:
            v.append('')
            v.append('\t//wires')
        
        for net in sorted(self.get_nets()):
            net_dec = net.verilog_declare()
            if net_dec:
                v.append('\t' + net_dec)

        # assignments
        if self.__subcomponents:
            once = True
            for inst, dev in self.get_subcomponents():
                if dev.is_virtual():
                    if once:
                        once = False
                        v.append('')
                        v.append('\t//assignments')
                    v.append('\t' + dev.verilog_declare())

        # instances
        if self.__subcomponents:
            v.append('')
            v.append('\t//instances')

            for inst in sorted(self.subcomponent_names(), key=slm_sort()):
                dev = self.get_subcomponent(inst)
                if dev.is_virtual():
                    continue
                l = '\t' + dev.get_object_name() + ' ' + inst + '('
                ports_names = []
                ports = []
                for inst_pin in dev.get_pins_ordered():
                    if not inst_pin.is_part_of_bus():
                        inst_pin_name = inst_pin.get_object_name()
                        if (inst, inst_pin_name) in self.__virtual_pins:
                            vpin = self.__virtual_pins[(inst, inst_pin_name)]
                            net = self.__pin_connectivity[vpin]
                            net_name = net.get_object_name()
                        else:
                            net_name = ''
                        ports.append('.' + inst_pin_name + '(' + net_name + ')')
                        ports_names.append(inst_pin_name)

                    else:  # bus
                        inst_bus = inst_pin.bus()
                        inst_bus_name = inst_bus.get_name()
                        if inst_bus_name in ports_names:
                            continue
                        concat = []
                        for inst_bus_pin in inst_bus.all_bits():
                            inst_bus_pin_name = inst_bus_pin.get_object_name()
                            if (inst, inst_bus_pin_name) in self.__virtual_pins:
                                vpin = self.__virtual_pins[(inst, inst_bus_pin_name)]
                                net = self.__pin_connectivity[vpin]
                                concat.append(net.get_object_name())
                            else:
                                if self.__is_inst_bus_connected_any(inst, inst_bus):
                                    raise Exception(inst+Component.PIN_SEPARATOR+inst_bus_pin_name+' is '+inst_pin.verilog_type()
                                                    + ' that not connected - you should do legalize() function before')
                        concat = Component.minimize_concat(concat)
                        if len(concat) == 0:
                            ports.append('.' + inst_bus_name + '()')
                        else:
                            ports.append('.' + inst_bus_name + '({' + ', '.join(concat) + '})')
                        ports_names.append(inst_bus_name)

                l += (', '.join(ports))
                l += ');'
                for ll in Component.line_wrap(l):
                    v.append(ll)

        if self.__verilog_code:
            v.append('\t//verilog code')
            v.extend(self.__verilog_code)

        v.append('')
        v.append('endmodule')
        return v

    def print_spectre(self):
        for line in self.write_spectre():
            print(line)

    def write_spectre_to_file(self, path=None):
        text = ''
        for line in self.write_spectre():
            text += line + '\n'
        if path:
            with open(path, 'w') as f:
                f.write(text)
        else:
            return text

    def write_spectre(self):
        def instances_text(comp, inst, sub, prefix=''):
            # write instances connectivity
            l = prefix + inst + ' ('
            ports = []
            for inst_pin in [p for p in sub.get_pins_ordered()]:
                inst_pin_name = inst_pin.get_object_name()
                if (inst, inst_pin_name) in comp.__virtual_pins:
                    vpin = comp.__virtual_pins[(inst, inst_pin_name)]
                    net = comp.__pin_connectivity[vpin]
                    net_name = net.get_object_name()
                    if isinstance(net, GNet):  # change constant name to spectre syntax
                        net_name = '1' if net_name == "1'b1" else '0'
                else:
                    raise Exception('"' + inst_pin_name + '" in "' + inst + '" is not connected')
                ports.append(net_name)
            l += (' '.join(ports))
            l += ') ' + sub.get_object_name()
            params = []
            if sub.get_spice_params():
                params = [p+'='+str(v) for p, v in sub.get_spice_params().items()]
            l += ' ' + (' '.join(params))
            for ll in Component.line_wrap(l, endl=' \\'):
                nl.append(ll)

        nl = ['simulator lang = spectre']  # Spice Header
        
        # subcircuits
        for sub in sorted(self.get_descendants(), key=slm_sort(is_object=True)):  # sort by names
            # subckt header
            nl.append('\n// Cell name: ' + sub.get_object_name() + '\n// View name: schematic')
            subckt_def = 'subckt ' + sub.get_object_name() + ' '
            pins = [p.get_object_name() for p in sub.get_pins_ordered()]
            ports = ' '.join(pins)
            subckt_def += ports
            for ll in Component.line_wrap(subckt_def, endl=' \\'):
                nl.append(ll)

            # subckt instances
            for inner_inst, inner_sub in sorted(sub.get_subcomponents(), key=lambda c: slm_sort()(c[0])):
                instances_text(sub, inner_inst, inner_sub, prefix='\t')

            if sub.__spectre_code:
                nl.append('\n\t// spectre code')
                nl.extend(['\t'+x for x in sub.__spectre_code])

            nl.append('ends ' + sub.get_object_name())
            nl.append('// End of subcircuit definition')

        # top cell
        nl.append('\n// Cell name: ' + self.get_object_name() + '\n// View name: schematic')
        # top cell instances
        for inst, sub in sorted(self.get_subcomponents(), key=lambda c: slm_sort()(c[0])):
            instances_text(self, inst, sub)

        if self.__spectre_code:
            nl.append('\n// spectre code')
            nl.extend(self.__spectre_code)

        return nl

    @staticmethod
    def line_wrap(line, line_width=120, endl=''):
        """splits a long string to multiple strings (lines), returns a list of strings
        line_width is the MINIMUM number of charechters for line to be split,
        i.e. the line break is added at the first blank charachter AFTER line_width charachters
        endl is added at the line-break - needed for tools that require some escape sequence for multi line command (e.g. \ in tcl)
        """
        lines = []
        i = 0
        curr = ''
        is_multiline = False
        for c in line:
            i += 1
            if i > line_width and c.isspace():
                is_multiline = True
                lines.append(curr + endl)
                curr ='\t'
                i = 4
            else:
                curr += c
        if is_multiline:
            curr += '\n'  # add '\n' at the end if did wrapping
        if i > 0:
            lines.append(curr)

        return lines

    @staticmethod
    def minimize_concat(concat):
        # function that try to recognize series of bus signals as separate
        # and concat them into bus format writing

        minimized = True
        bit_re = re.compile(r"([0-9]+)'b([10x]+),([0-9]+)'b([10x]+)")  # (1)'b(1),(3)'b(10x) -> 1,1,2,11
        netbus_re = re.compile(r"(.*)\[([0-9]+:)?([0-9]*)\]\1\[([0-9]+)\]")  # (A)[(31?:?)(20)]A[(5)] -> A,31:?,20,5
        net_re = re.compile(r"^(?:{(\d+){(?P<n_c>.*)}}|(?P<n>.*)),(?:{(\d+){(?:(?P=n)|(?P=n_c))}}|(?:(?P=n)|(?P=n_c)))$")  # 2{?,GND,}?,3{?,(GND),}?
        while minimized:
            minimized = False
            for i in range(len(concat)-1):
                m = re.match(bit_re, concat[i] + ',' + concat[i + 1])  # find match of bit_re
                if m:
                    concat[i] = str(int(m.group(1)) + int(m.group(3))) + "'b" + m.group(2) + m.group(4)
                    del concat[i + 1]
                    minimized = True
                    break
                
                m = re.match(netbus_re, concat[i] + concat[i + 1])
                if m and (int(m.group(3)) == int(m.group(4))+1 or int(m.group(3)) == int(m.group(4))-1):
                    if m.group(2):
                        a, b, c = int(m.group(2)[:-1]), int(m.group(3)), int(m.group(4))
                        if not (a > b > c or a < b < c):  # in case of A[31], A[5], A[8]
                            continue
                        concat[i] = m.group(1) + '[' + m.group(2) + m.group(4) + ']'
                    else:
                        concat[i] = m.group(1) + '[' + m.group(3) + ':' + m.group(4) + ']'
                    del concat[i + 1]
                    minimized = True
                    break

                m = re.match(net_re, concat[i] + ',' + concat[i + 1])  # find match of net_re
                if m:
                    groups = [g if g is not None else ['1', None, None, '1'][i] for i, g in enumerate(m.groups())]
                    groups = [g for g in groups if g is not None]
                    concat[i] = '{' + str(int(groups[0]) + int(groups[2])) + '{' + groups[1] + '}' + '}'
                    del concat[i + 1]
                    minimized = True
                    break

        return concat

    def get_connected(self, pin):  # return net that connected to pin
        p = self.__2pin(pin)['pin']
        return self.__pin_connectivity[p]

    def all_connected(self, net_str):  # return all pins that connected to net
        connected = []
        if not isinstance(net_str, str):
            raise Exception('net_str should be a string')

        lnet = net_str.replace(Component.PIN_SEPARATOR,'/').split('/',1)
        if len(lnet)==1:  # net of component
            try:
                net = self.get_net(net_str)
            except:  # todo: add type
                raise Exception('cannot find net [' + net_str + '] in component [' + self.get_object_name() + ']')
            pin_list = self.__net_connectivity[net]
            i = 0
            while i < len(pin_list):
                pin_str = pin_list[i].get_object_name()
                i+=1
                lpin = pin_str.split(Component.PIN_SEPARATOR)
                if len(lpin)==1:  # pin of component
                    connected.append(pin_str)
                elif len(lpin)==2:  # pin of sub-component 
                    inst, inst_pin = lpin # lpin[0]=instance name, lpin[1]=pin name
                    sub = self.get_subcomponent(inst)
                    if sub.__is_physical:
                        connected.append(pin_str)
                    else:
                        newconnections = sub.all_connected(sub.__pin_connectivity[sub.get_pin(inst_pin)].get_object_name())
                        for p in newconnections:
                            if len(p.split(Component.PIN_SEPARATOR))==1:
                                pin_list.extend([x for x in self.__net_connectivity[self.__pin_connectivity[self.__virtual_pins[(inst,p)]]] if x not in pin_list])
                            else:
                                connected.append(inst + '/' + p)
        else:  # net of a nested subcomponent
            inst, inst_net = lnet # lnet[0]=instance name, lnet[1]=net name
            try:
                sub = self.get_subcomponent(inst)
            except:  # todo: add type
                raise Exception('cannot find subcomponent [' + inst + '] in component [' + self.get_object_name() + ']')
            for pin_str in sub.all_connected(inst_net):
                newconnections = [inst+'/'+pin_str]
                if len(pin_str.split(Component.PIN_SEPARATOR))==1:
                    newconnections = self.all_connected(self.__pin_connectivity[self.__virtual_pins[(inst,pin_str)]].get_object_name())
                connected.extend(x for x in newconnections if x not in connected)
        return connected

    '''
0 - full path +dupes
1 - full path 1 per endpoint
2 - internal pins +dupes
3 - internal pins -dupes
4 - endpoints +dupes
5 - endpoints -dupes
    '''

    def all_fan_in(self, net_str, output_type=0, visited=set()):
        fan_in = []
        drive_pins = 0
        for pin_str in self.all_connected(net_str):
            lpin = pin_str.split(Component.PIN_SEPARATOR)
            if len(lpin)==1:  # pin of component
                if self.get_pin(pin_str).verilog_type() == "input":
                    fan_in.append(pin_str)
                    drive_pins+=1
            elif len(lpin)==2:  # pin of sub-component 
                inst_str, inst_pin = lpin # lpin[0]=instance name, lpin[1]=pin name
                linst = inst_str.split('/')
                sub = self
                for inst in linst:
                    sub = sub.get_subcomponent(inst)
                pin = sub.get_pin(inst_pin)
                if pin.verilog_type() == "output":
                    if sub.__is_sequential:
                        fan_in.append(pin_str)
                        drive_pins+=1
                    else:
                        for inp in [p for p in sub.get_pins() if p.verilog_type() == "input"]:
                            if pin_str not in visited:
                                fan_in.extend(x+'>'+pin_str for x in
                                              self.all_fan_in(inst_str + Component.PIN_SEPARATOR +
                                                              sub.__pin_connectivity[inp].get_object_name()
                                                              , visited=visited.union({pin_str})))
            if drive_pins > 1:
                print("WARNING: There are "+str(drive_pins)+" pins driving net "+net_str)
        if output_type==0:
            return fan_in
        elif output_type==1:
            temp = {}
            for p in fan_in:
                temp[p.partition('>')[0]] = p
            return list(temp.values())
        elif output_type==2:
            return [pin for path in [p.split('>') for p in fan_in] for pin in path]
        elif output_type==3:
            return list(set(pin for path in [p.split('>') for p in fan_in] for pin in path))
        elif output_type==4:
            return [p.partition('>')[0] for p in fan_in]
        elif output_type==5:
            return list(set(p.partition('>')[0] for p in fan_in))

    def all_fan_out(self, net_str, output_type=0, visited=set()):
        fan_out = []
        for pin_str in self.all_connected(net_str):
            lpin = pin_str.split(Component.PIN_SEPARATOR)
            if len(lpin)==1:  # pin of component
                if self.get_pin(pin_str).verilog_type() == "output":
                    fan_out.append(pin_str)
            elif len(lpin)==2:  # pin of sub-component 
                inst_str, inst_pin = lpin # lpin[0]=instance name, lpin[1]=pin name
                linst = inst_str.split('/')
                sub = self
                for inst in linst:
                    sub = sub.get_subcomponent(inst)
                pin = sub.get_pin(inst_pin)
                if pin.verilog_type() == "input":
                    if sub.__is_sequential:
                        fan_out.append(pin_str)
                    else:
                        for outp in [p for p in sub.get_pins() if p.verilog_type() == "output"]:
                            if pin_str not in visited:
                                fan_out.extend(pin_str+'>'+x for x in
                                               self.all_fan_out(inst_str + Component.PIN_SEPARATOR +
                                                                sub.__pin_connectivity[outp].get_object_name()
                                                                , visited=visited.union({pin_str})))
        if output_type==0:
            return fan_out
        elif output_type==1:
            temp = {}
            for p in fan_out:
                temp[p.rpartition('>')[-1]] = p
            return list(temp.values())
        elif output_type==2:
            return [pin for path in [p.split('>') for p in fan_out] for pin in path]
        elif output_type==3:
            return list(set(pin for path in [p.split('>') for p in fan_out] for pin in path))
        elif output_type==4:
            return [p.rpartition('>')[-1] for p in fan_out]
        elif output_type==5:
            return list(set(p.rpartition('>')[-1] for p in fan_out))

    def add_verilog_code(self, code):
        if self.__verilog_code:
            self.__verilog_code.append(code)
        else:
            self.__verilog_code = [code]

    def get_verilog_code(self):
        return self.__verilog_code

    def add_spectre_code(self, code):
        if self.__spectre_code:
            self.__spectre_code.append(code)
        else:
            self.__spectre_code = [code]

    def get_spectre_code(self):
        return self.__spectre_code

    def flatten(self, flatten_separator='__'):
        def get_flatten_name(inst, old_name):
            # support for escaped identifiers in verilog
            if '\\' == old_name[0] and ' ' == old_name[-1]:
                if '\\' == inst[0] and ' ' == inst[-1]:
                    name = inst[:-1] + flatten_separator + old_name[1:]
                else:
                    name = '\\' + inst + flatten_separator + old_name[1:]
            elif '\\' == inst[0] and ' ' == inst[-1]:
                name = inst[:-1] + flatten_separator + old_name + ' '
            else:
                name = inst + flatten_separator + old_name
            if name in collision_names:  # for collision names
                name = collision_names[name]
            return name

        # flatten subcomponents
        for inst, sub in self.get_subcomponents():
            if sub.__is_physical or sub.is_virtual():
                continue
            sub.flatten()

            collision_names = {}
            # flatten inner subcomponents
            for inner_inst, inner_sub in sub.get_subcomponents():
                if not inner_sub.is_virtual():
                    new_name = get_flatten_name(inst, inner_inst)
                    if new_name in self.subcomponent_names():  # check if name already exist, if so, generate new name
                        # save the changes for connectivity later
                        collision_names[new_name] = Component.COLLISION_NAME + str(Component.__count_collision)
                        print('Warning: changed subcomponent name from {} to {}'
                              .format(new_name, collision_names[new_name]))
                        new_name = collision_names[new_name]
                        Component.__count_collision += 1

                    self.add_subcomponent(inner_sub, new_name)

            # flatten nets
            for net_str in sub.net_names():
                if net_str in sub.pin_names():  # dont add net that connected to primary pin
                    continue
                net = sub.get_net(net_str)
                if isinstance(net, GNet):
                    continue
                if net.is_part_of_bus():
                    n_bus = net.bus()
                    netbus_name = get_flatten_name(inst, n_bus.get_name())
                    if netbus_name in self.netbus_names():
                        continue
                    self.add_netbus(Bus(Net, netbus_name, n_bus.get_width()))
                else:
                    new_name = get_flatten_name(inst, net_str)
                    if new_name in self.net_names():  # check if name already exist, if so, generate new name
                        collision_names[new_name] = Component.COLLISION_NAME + str(Component.__count_collision)
                        print('Warning: changed net name from {} to {}'
                              .format(new_name, collision_names[new_name]))
                        new_name = collision_names[new_name]
                        Component.__count_collision += 1

                    self.add_net(Net(new_name))

            # flatten assignments
            for virt_inst, virt_sub in sub.get_subcomponents(filter=lambda c: c.is_virtual()):
                net_in = virt_sub.input_net.get_object_name()
                net_out = virt_sub.output_net.get_object_name()
                flag = False
                # was assign from input to output of subcomponent
                if (inst, net_in) in self.__virtual_pins and (inst, net_out) in self.__virtual_pins:
                    flag = True
                    net_in = self.get_connected(self.__virtual_pins[(inst, net_in)])  # get net that was connected to virtual pin
                    net_out = self.get_connected(self.__virtual_pins[(inst, net_out)])
                # was assign from pin of subcomponent to net of subcomponent
                elif (inst, net_in) in self.__virtual_pins:
                    flag = True
                    net_in = self.get_connected(self.__virtual_pins[(inst, net_in)])
                    if virt_sub.output_net.is_part_of_bus():
                        net_out_bus = virt_sub.output_net.bus().get_name()
                        net_out = get_flatten_name(inst, net_out_bus) + net_out.replace(net_out_bus, '')  # add bit place - '[0]'
                    elif not isinstance(virt_sub.output_net, GNet):  # if its GNet it stays the same name
                        net_out = get_flatten_name(inst, net_out)
                    net_out = self.get_net(net_out)  # get net of subcomponent that got flatted(and now belong to self)
                # was assign from net of subcomponent to pin of subcomponent
                elif (inst, net_out) in self.__virtual_pins:
                    flag = True
                    if virt_sub.input_net.is_part_of_bus():
                        net_in_bus = virt_sub.input_net.bus().get_name()
                        net_in = get_flatten_name(inst, net_in_bus) + net_in.replace(net_in_bus, '')
                    elif not isinstance(virt_sub.input_net, GNet):  # if its GNet it stays the same name
                        net_in = get_flatten_name(inst, net_in)
                    net_in = self.get_net(net_in)
                    net_out = self.get_connected(self.__virtual_pins[(inst, net_out)])
                if flag:
                    self.connect_nets(net_in, net_out)

            # flatten connectivity
            for v_p_str, v_p in sub.__virtual_pins.items():
                if v_p.get_associated_comp().is_virtual():  # skip if its virtual (assignment)
                    continue
                net = sub.get_connected(v_p)
                net_str = net.get_object_name()
                if net_str in sub.pin_names():  # net that connected to primary pin
                    if (inst, net_str) in self.__virtual_pins:
                        net = self.get_connected(self.__virtual_pins[(inst, net_str)])
                    else:
                        net = None
                else:
                    if net.is_part_of_bus():
                        net_bus = net.bus().get_name()
                        net_str = get_flatten_name(inst, net_bus) + net_str.replace(net_bus, '')  # add bit place - '[0]'
                    elif not isinstance(net, GNet):  # if its GNet it stays the same name
                        net_str = get_flatten_name(inst, net_str)
                    net = self.get_net(net_str)
                if net:
                    self.connect(net, get_flatten_name(inst, v_p_str[0]) + Component.PIN_SEPARATOR + v_p_str[1])

            if not sub.is_virtual():
                self.remove_subcomponent(inst)

    def connectivity_paths(self, prefix=None, dicts=(None, None, None)):
        # return 3 dicts: all_connectivity, fan_out_connectivity and fan_in_connectivity
        def add2dicts(a, b):  # add connection from a to b to dicts
            all_connectivity[b].append(a)
            all_connectivity[a].append(b)
            fan_out_connectivity[a].append(b)
            fan_in_connectivity[b].append(a)

        if prefix is None:  # initialization
            dicts = (defaultdict(list), defaultdict(list), defaultdict(list))
        all_connectivity, fan_out_connectivity, fan_in_connectivity = dicts
        prefix_pin = prefix + Component.PIN_SEPARATOR if prefix else ''  # nand.
        prefix_hier = prefix + Component.HIERARCHICAL_SEPARATOR if prefix else ''  # nand/

        # connect input/inout pins of subcomponent(physical) to all output pins
        if self.get_is_physical():
            for i_pin in self.get_pins(filter=lambda p: isinstance(p, (Input, Inout))):
                i_pin_str = prefix_pin + i_pin.get_object_name()  # and.A
                output_pins = self.get_pins(filter=lambda p: isinstance(p, Output))
                for o_pin in output_pins:  # connect input/inout pin to all output pins
                    o_pin_str = prefix_pin + o_pin.get_object_name()
                    add2dicts((i_pin_str, type(i_pin)), (o_pin_str, Output))  # add connection to dicts
        else:
            # add subcomponent connections
            for inst, sub in self.get_subcomponents():
                if sub.is_virtual():  # add assign connection to dicts from net to net
                    add2dicts((prefix_pin + sub.input_net.get_object_name(), Net), (prefix_pin + sub.output_net.get_object_name(), Net))
                else:
                    sub.connectivity_paths(prefix_hier+inst, dicts)  # add subcomponent connections to dicts with prefix name

            # add nets connections
            for net in self.get_nets(filter=lambda n: n in self.__net_connectivity):
                net_str = net.get_object_name()
                for pin in self.get_net_connectivity(net):
                    pin_str = pin.get_object_name()
                    if type(pin) in [Input, Inout]:  # add Input/Inout pin to net
                        add2dicts((prefix_pin + pin_str, type(pin)), (prefix_pin + net_str, Net))
                    elif type(pin) in [Output, Inout]:  # add net to output/Inout connection
                        add2dicts((prefix_pin + net_str, Net), (prefix_pin + pin_str, type(pin)))
                    elif pin.is_virtual():  # if connected to virtual pin
                        if pin.get_associated_comp().is_virtual():  # net assignment - already written in subcomponent connections
                            continue
                        pin_type = type(pin.get_associated_pin())
                        if pin_type == Output:  # from virtual pin to net
                            add2dicts((prefix_hier + pin_str, pin_type), (prefix_pin + net_str, Net))
                        else:  # from net(or constant-GNet) to virtual pin
                            add2dicts((prefix_pin + net_str, type(net)), (prefix_hier + pin_str, pin_type))
        return dicts

    def graph(self, subgraph=False, name=None, dict_pins=None, full_graph=True, view=True, path=None):
        # partly working - still in progress
        from graphviz import Digraph
        if subgraph:
            g = Digraph(name='cluster_' + name, directory='junk',
                        graph_attr={'rankdir': 'LR', 'label': name},  # 'splines':'ortho', 'compound':'false'
                        node_attr={'shape': 'record'})
            # g.attr(label=name)
            # g.node(name)
        else:
            name = self.get_object_name()
            g = Digraph(name=name, directory='junk',
                        graph_attr={'rankdir': 'LR', 'label': name},
                        node_attr={'shape': 'record'})
            # g.node(name)
        if not dict_pins:
            dict_pins = {}
        pins = self.get_pins()
        if pins:
            lbl = {'input': '', 'output': '', 'inout': ''}
            for i, p in enumerate(pins):
                type = p.verilog_type()
                p_str = p.get_object_name()
                pin_graph_name = 'p'+str(len(dict_pins))
                if lbl[type]:
                    lbl[type] += '|<' + pin_graph_name + '> ' + p_str
                else:
                    lbl[type] += '<' + pin_graph_name + '> ' + p_str
                dict_pins[(name, p_str)] = type, name+'_'+type+':'+pin_graph_name

            for type in [t for t in lbl if lbl[t]]:
                with g.subgraph(name='cluster_'+type+'_'+name, graph_attr={'pencolor':'white'}) as a:
                    a.node(name=name+'_'+type, label=lbl[type],width='0',height='0',margin='0',color='red')
                    a.attr(label=type+'_pins')

        for inst, dev in self.get_subcomponents():
            g.subgraph(dev.graph(view=False, subgraph=True, name=inst, dict_pins=dict_pins))

        for net, pins in self.__net_connectivity.items():
            if len(pins) == 1:
                continue
            p1_str = pins[0].get_object_name()
            for pin in pins[1:]:
                p2_str = pin.get_object_name().split('.')
                p2_str = (p2_str[0], p2_str[1])
                if p1_str in self.pin_names():
                    if dict_pins[(name, p1_str)][0] == 'input':
                        g.edge(dict_pins[(name, p1_str)][1], dict_pins[p2_str][1])
                    else:
                        g.edge(dict_pins[p2_str][1], dict_pins[(name, p1_str)][1])
                else:
                    p1_str_ = (p1_str.split('.')[0], p1_str.split('.')[1])
                    g.edge(dict_pins[p1_str_][1], dict_pins[p2_str][1])
        if self.is_virtual():
            g.edge(dict_pins[(name, 'I')][1], dict_pins[(name, 'O')][1])

        if view:
            g.view()
        return g
