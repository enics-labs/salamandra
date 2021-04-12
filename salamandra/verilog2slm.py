# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from salamandra.lexer import Lexer
import re
from .net import Net
from .bus import Bus
from .input import Input
from .output import Output
from .inout import Inout
from .component import Component


def get_verilog_tokens(is_std_cell=False, instances=False):
    # return tokens for lexer to run with this
    comments = [(r'\s*(?:/\*[\S\s]*?\*/|\(\*[\S\s]*?\*\))\s*', None),  # /*...*/ | (*...*)
                (r'\s*(?://|`).*$', None)  # //... | `...
                ]
    nets = [(r'\s*,?\s*(\d+)\'([bodhBODH])([a-fA-F0-9x]+)\s*,?\s*', 'gnet'),  # 1'b0 / 13'h0 / 1'bx -> 1,b,x
            (r'\s*,?\s*(\d+)\s*{\s*', 'multi_cat', 'cat'),  # 2{
            (r'\s*,?\s*([\w$]+|\\\S+\s)\s*(?:\[\s*(-?\d+)\s*:?\s*(-?\d+)?\s*\])?\s*', 'net'),  # A,A[2],A[2:0], -> A,2,0
            (r'\s*{\s*', None, 'cat'),  # {
            (r'\s*,\s*', None),  # ,
            ]
    cat = [(r'\s*}\s*', 'cat_end', '#pop'), *nets]

    if not instances:
        verilog_tokens = {
            'root': [
                (r'\s*module\s+([\w$]+|\\\S+\s)\s*(?:\([\S\s]*?\))?\s*;\s*', 'module', 'module'),
                # module name(pins); -> name
                *comments
            ],
            'module': [
                (r'\s*function\s', None, 'function'),  # function...
                (r'\s*begin\s', None, 'begin_end'),  # begin...
                (r'\s*(else\s+if\s+\([\S\s]*?\)\s[\S\s]*?;|case\s[\S\s]*?\sendcase\s)\s*', None),  # else if (...) ...; | case...endcase

                (r'\s*(input|inout|output|wire)(\s+signed)?(?:\s+\[\s*(-?\d+)\s*:\s*(-?\d+)\s*\])?\s+', 'pin_net_start', 'pins_nets'),
                # (input)\(wire) (signed)? [(31):(0)]?...
                (r'\s*assign\s+', 'assign_start', 'nets_assign'),  # assign
                (r'\s*((?:[\w$]+|\\\S+)\s+(?:[\w$]+|\\\S+\s)\s*\([\S\s]*?\)\s*;\s*)', 'instance'),
                # (mux i_mux(...);)
                *comments,
                (r'\s*endmodule\s*', 'end_module', '#pop'),
            ],
            'nets_assign': [*nets, (r'\s*=\s*', 'assign_eq'), (r'\s*;\s*', 'assign_end', '#pop'), *comments, (r'[\S\s]*?;', 'assign_break', '#pop')],
            'pins_nets': [*nets, (r'\s*;\s*', 'pin_net_end', '#pop'), *comments],
            'cat': [*cat],
            'function': [(r'((?!\sendfunction\s)[\S\s])*?function\s', None, 'function'), (r'[\S\s]*?(\s|^)endfunction\s', None, '#pop')],
            'begin_end': [(r'((?!\send\s)[\S\s])*?begin\s', None, 'begin_end'), (r'[\S\s]*?(\s|^)end\s', None, '#pop')],
        }
        if is_std_cell is True:
            verilog_tokens['module'][2] = (r'\s*((assign|wire)\s[\S\s]*?;|else\s+if\s+\([\S\s]*?\)\s[\S\s]*?;|case\s[\S\s]*?\sendcase\s)\s*', None)  # ignore assign and wire
            verilog_tokens['module'][3] = (r'\s*(input|inout|output)(\s+signed)?(?:\s+\[\s*(-?\d+)\s*:\s*(-?\d+)\s*\])?\s+', 'pin_net_start', 'pins_nets')  # ignore wire
            del verilog_tokens['module'][4:6]  # remove assign and instances
    else:
        verilog_tokens = {
            'instances': [(r'\s*([\w$]+|\\\S+\s)\s*([\w$]+|\\\S+\s)\s*\(\s*', 'instance_start', 'instance_ports'), *comments],
            # (mux) (i_mux)(...
            'instance_ports': [
                (r'\s*,?\s*\.([\w$]+|\\\S+\s)\s*\(\s*', 'pin_start', 'nets_instance'),  # ,? .I(...
                (r'\s*\)\s*;\s*', None, '#pop'),  # );
                (r'\s*,\s*', None),  # ,
                *comments
            ],
            'nets_instance': [*nets, (r'\s*\)\s*', 'pin_end', '#pop'), *comments],
            'cat': [*cat],
        }
    return verilog_tokens


def verilog2slm_file(fname, is_std_cell=False, implicit_wire=False, implicit_instance=False, verbose=False):
    """
    Parse a named Verilog file

    Args:
      fname (str): File to parse.
      is_std_cell (bool): is STD cell (takes only I/O ports)
      implicit_wire (bool): add implicit wires
      implicit_instance (bool): guess instances if not exist
      verbose (bool): print warnings if exist
    Returns:
      List of parsed objects.
    """
    # with open(fname, 'rb') as fh:
    #     text_ba = bytearray(fh.read())
    #     for i in range(len(text_ba)):
    #         if text_ba[i] is 0x80:
    #             text_ba[i] = 92
    #     text = text_ba.decode()
    with open(fname, 'rt') as fh:
        text = fh.read()

    return verilog2slm(text, is_std_cell, implicit_wire, implicit_instance, verbose)


def verilog2slm(text, is_std_cell=False, implicit_wire=False, implicit_instance=False, verbose=False):
    """
    Parse a text buffer of Verilog code

    Args:
      text (str): Source code to parse
      is_std_cell (bool): is STD cell (takes only I/O ports)
      implicit_wire (bool): add implicit wires
      implicit_instance (bool): guess instances if not exist
      verbose (bool): print warnings if exist
    Returns:
      List of components objects.
    """
    verilog_tokens_ = get_verilog_tokens(is_std_cell)  # get local verilog tokens
    lex = Lexer(verilog_tokens_)
    comp = None
    pin_net = None
    multi_cat = []
    assign_pos = None
    pins_nets = []
    types = {'input': Input, 'output': Output, 'inout': Inout, 'wire': Net}
    comps = []
    text_instances = ''
    components = []

    for pos, action, groups in lex.run(text):  # run lexer and search for match
        if action == 'module':  # initiate Component
            module_name = check_escape(groups[0])
            if module_name in Component.all_components():
                if verbose:
                    print('Warning: component ' + module_name + ' already exist')
                comp = None
            else:
                comp = Component(module_name)
                if is_std_cell:
                    comp.set_is_physical(True)
                    comp.set_dont_write_verilog(True)
            text_instances = ''
            multi_cat = []
            pins_nets = []

        elif comp is None:
            continue

        elif action == 'pin_net_start':  # wire/input/...
            v_type, signed, msb, lsb = groups
            v_type = types[v_type]
            signed = False if signed is None else True
            if msb is not None:  # could be 0
                msb, lsb = max(int(msb), int(lsb)), min(int(msb), int(lsb))
            pins_nets = []
            pin_net = (v_type, signed, msb, lsb)

        elif action in ['net', 'gnet']:  # save all pins/nets to add later
            if assign_pos:  # if inside assign
                pins_nets.extend(get_nets(action, groups, comp))
            else:
                pins_nets.extend(get_nets(action, groups))

        elif action == 'pin_net_end':  # reached end of wire/port statement -> add Net/s / Pin/s
            v_type, signed, msb, lsb = pin_net
            # get the right function according to the type
            if v_type == Net:  # add net/netbus
                if msb is not None:  # add netbus
                    for name in pins_nets:
                        if name in comp.netbus_names():  # in case its also a pin(pin_adds_net)
                            continue
                        comp.add_netbus(Bus(v_type, name, (msb, lsb), signed=signed))
                else:  # add net
                    for name in pins_nets:
                        if name in comp.net_names():  # in case its also a pin(pin_adds_net)
                            continue
                        comp.add_net(v_type(name))
            else:  # add pin/pinbus
                if msb is not None:  # add pinbus
                    for name in pins_nets:
                        comp.add_pinbus(Bus(v_type, name, (msb, lsb), signed=signed))
                else:  # add pin
                    for name in pins_nets:
                        comp.add_pin(v_type(name))
            pin_net = None
            pins_nets = []

        elif action == 'instance':  # save all instance connectivity for later
            text_instances += '\n'+groups[0]

        elif action == 'assign_start':
            assign_pos = pos[0]  # save position of assign command
            pins_nets = []

        elif action == 'assign_eq':  # "="
            assign_nets = pins_nets  # save all left-side nets
            pins_nets = []

        elif action == 'assign_end':  # connect all assign nets
            for net_l, net_r in zip(assign_nets, pins_nets):
                comp.connect_nets(net_r, net_l)
            assign_pos = None
            pins_nets = []

        elif action == 'assign_break':  # can't interpret assign command
            if verbose:
                print('Warning: skipped assign command "'+text[assign_pos:pos[1]]+'"')
            assign_pos = None

        elif action == 'multi_cat':  # 2{...
            multi_cat.append((groups[0], len(pins_nets)))  # save start location of concat

        elif action == 'cat_end':  # duplicate by num, 2{..}
            if multi_cat:
                num, start = multi_cat.pop()
                pins_nets += pins_nets[start:] * (int(num) - 1)

        elif action == 'end_module':  # "endmodule"
            comps.append((comp, text_instances))

    # instances connectivity part
    for comp, text_instances in comps:
        if text_instances:
            inst_name = None
            sub = None
            sub_pin = None
            is_guessed = False
            verilog_tokens_ = get_verilog_tokens(instances=True)  # get local verilog tokens
            lex = Lexer(verilog_tokens_)

            for pos, action, groups in lex.run(text_instances, start='instances'):  # run lexer and search for match
                if action == 'instance_start':  # adding new subcomponent
                    inst, inst_name = groups  # nand i_nand
                    inst, inst_name = check_escape(inst), check_escape(inst_name)
                    if inst not in Component.all_components():
                        if not implicit_instance:
                            raise Exception('instance ' + inst + ' should be implemented in the file or before')
                        sub = Component(inst)  # if not existed create it(with flag implicit_instance)
                        sub.set_property('is_guessed', True)
                    else:
                        sub = Component.get_component_by_name(inst)
                    comp.add_subcomponent(sub, inst_name)
                    is_guessed = sub.get_property('is_guessed')

                elif action == 'pin_start':  # .I(...
                    sub_pin = check_escape(groups[0])
                    pins_nets = []

                elif action in ['net', 'gnet']:  # save all pins/nets to add later
                    pins_nets.extend(get_nets(action, groups, comp))

                elif action == 'pin_end':
                    if implicit_instance and is_guessed:  # add pin/bus if implicit instance
                        if len(pins_nets) > 1 and sub_pin not in sub.pinbus_names():
                            sub.add_pinbus(Bus(Inout, sub_pin, len(pins_nets)))
                        elif len(pins_nets) <= 1 and sub_pin not in sub.pin_names():  # pin or empty pin
                            sub.add_pin(Inout(sub_pin))

                    if len(pins_nets) == 1:  # net
                        if sub_pin in sub.pin_names():  # net2pin
                            comp.connect(pins_nets[0], inst_name + Component.PIN_SEPARATOR + sub_pin)
                        else:  # net2pinbus#1
                            comp.connect(pins_nets[0], inst_name + Component.PIN_SEPARATOR + sub_pin + '[0]')
                    else:  # netbus
                        net_names = comp.net_names()
                        for i, net in enumerate(pins_nets):  # connect each net from msb to lsb
                            if implicit_wire and net not in net_names:
                                comp.add_net(Net(net))
                            comp.connect(net, inst_name + Component.PIN_SEPARATOR + sub_pin + '[{}]'.format(len(pins_nets)-1-i))

                elif action == 'multi_cat':  # 2{...
                    multi_cat.append((groups[0], len(pins_nets)))  # save start location of concat

                elif action == 'cat_end':
                    if multi_cat:  # duplicate by num, 2{..}
                        num, start = multi_cat.pop()
                        pins_nets += pins_nets[start:] * (int(num) - 1)

        components.append(comp)
    return components


def check_escape(name):
    # change "\name\n" to "\name "
    if name and name[0] == '\\':
        name = re.sub(r'^(\\\S+)\s(\[(-?\d+)\])?$', r'\1 \2', name)
    return name


def get_nets(action, groups, comp=None):
    # get nets from string. A[1:0] -> A[1],A[0]. 2'b0-> 1'b0,1'b0. and more...
    nets = []
    if action == 'net':
        name, msb, lsb = groups
        name = check_escape(name)
        if msb is not None:  # could be 0
            lsb = msb if lsb is None else lsb
            msb, lsb = int(msb), int(lsb)
            msb2lsb = 1 if msb > lsb else -1
            for bit in range(msb, lsb - msb2lsb, -msb2lsb):
                nets.append(name+'['+str(bit)+']')
        else:
            if comp and name in comp.netbus_names():  # if bus, add all bits
                for bit in comp.get_netbus(name).all_bits():
                    nets.append(bit.get_object_name())
            else:
                nets.append(name)

    elif action == 'gnet':
        radix2bits = {'b': 2, 'o': 8, 'd': 10, 'h': 16}
        size, radix, value = groups  # 2,b,01/xx
        if 'x' in value:
            value_bin = value
        else:
            value_dec = int(value, radix2bits[radix.lower()])  # convert value to decimal
            value_bin = bin(value_dec)[2:].zfill(int(size))  # convert value to binary padded to size

        for bit in range(int(size)):
            nets.append("1'b{}".format(value_bin[bit]))

    return nets
