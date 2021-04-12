# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from salamandra.lexer import Lexer
import re
from .net import Net
from .inout import Inout
from .bus import Bus
from .component import Component


def get_spectre_tokens():
    # return tokens for Lexer to run with this
    spectre_tokens = {
        'root': [
            (r'\s*(//|\*).*?\n\s*', None),  # //...\n , *...\n
            (r'\s*subckt\s+([\w!]+(?=\s)|\\\S+\s)\s*([\S\s]*?[^\\]\n)\s*(parameters\s+[\S\s]*?[^\\]\n)?([\S\s]*?)ends\s+\1\s*', 'subckt'),
            # groups: 0.name(=\1), 1.nodes, 2.parameters(?), 3. subckt body
            # Example:
            # subckt SubcircuitName [(] node1 ... nodeN [)]
            #       [ parameters name1=value1 ... [nameN=valueN]]
            #       instance, model, ic, or nodeset statements—or
            #       further subcircuit definitions
            # ends [SubcircuitName]
            (r'\s*(model|global|include)\s+[\S\s]*?([^\\]\n|\Z)\s*', None),  # model...\n or EOF(\Z)
            (r'\s*simulator\s+lang\s*=\s*spectre\s*', None),  # simulator lang = spectre
            (r'\s*([\w!]+|\\\S+\s)(\s+[\S\s]*?)?\s+([\w!]+|\\\S+\s)(\s+(?:[\w!]+|\\\S+\s)\s*=\s*[\w+\-.]+\s+[\S\s]*?[^\\])?\s*(?:\n|\Z)\s*', 'instance'),
            # instance or analysis, groups: 0.name, 1.nodes, 2.master/analysis_type, 3.parameters(?)
            # Example:
            # name [(]node1 ... nodeN[)] master [[param1=value1] ...[paramN=valueN]]
            # Name [(]node1 ... nodeN[)] Analysis_Type [[param1=value1] ...[paramN=valueN]]
        ],
    }
    return spectre_tokens


def spectre2slm_file(fname, top_cell_name='spectre2slm_cell', is_std_cell=False, implicit_instance=False):
    with open(fname, 'rt') as fh:
        text = fh.read()
    return spectre2slm(text, top_cell_name, is_std_cell, implicit_instance)


def spectre2slm(text, top_cell_name='spectre2slm_cell', is_std_cell=False, implicit_instance=False):
    """Parse a text buffer of spectre code
    Args:
      text (str): Source code to parse
      top_cell_name (str): name of top cell component
      is_std_cell (bool): is STD cell (takes only I/O ports)
      implicit_instance (bool): guess instances if not exist
    Returns:
      top cell component
    """

    spectre_tokens_ = get_spectre_tokens()  # get local spectre tokens
    lex = Lexer(spectre_tokens_)
    analysis_type = ['pxf','xf','sp','tran','tdr','noise','pnoise','dc','ac','pz','envlp','pac','pdisto','pnoise','pss',
                     'sens','fourier','dcmatch','stb','sweep','montecarlo']
    forbidden_names = ['simulatorOptions','modelParameter','element','outputParameter','designParamVals','primitives',
                       'subckts','saveOptions']
    comp = None
    text_instances = []
    text_subckts = []
    re_pins_nets = re.compile(r'\s*([\w!\[\]\-]+|\\\S+\s(?:\[-?\d+\])?)')
    re_params = re.compile(r'\s*([\w!]+|\\\S+\s)\s*=\s*([\w+\-.]+)')
    re_bus = re.compile(r'\s*([\w!]+)\[(-?\d+)\]|(\\\S+\s)\[(-?\d+)\]')

    def escape_name_check(name):  # change '\name\n' to '\name '
        if name[0] == '\\':
            return re.sub(r'^(\\\S+)\s(\[(-?\d+)\])?$', r'\1 \2', name)
        return name

    for pos, action, groups in lex.run(text):  # run lexer and search for match
        if action == 'subckt':
            dev_name, pins_text, params, subckt_body = groups
            dev_name = escape_name_check(dev_name)
            comp = Component(dev_name)
            if pins_text:
                # add all pins, if bus try to concatenate bit pin to busses. a[0], a[1] -> a with width 2
                last_bus = None
                pins = re_pins_nets.findall(pins_text)  # find all kind of pins
                for pin in pins:
                    pin = escape_name_check(pin)
                    bus = re_bus.match(pin)  # catch bus
                    if bus:
                        bus = bus.groups()
                        bus = [bus[0] or bus[2], int(bus[1] or bus[3])]  # filter empty - ''. bus: [name, bit]
                        if last_bus:
                            if last_bus[0] == bus[0]:  # continue of the last bus
                                last_bus[2] = last_bus[1] > bus[1]  # save if it goes from msb or lsb
                                last_bus[1] = max(last_bus[1], bus[1])  # check his width
                            else:  # starting another bus. add the last one and start new bus
                                comp.add_pinbus(Bus(Inout, last_bus[0], last_bus[1]+1), msb2lsb_declaration=last_bus[2])
                                last_bus = bus + [True]
                        else:
                            last_bus = bus + [True]
                    else:
                        if last_bus:  # add the last bus if exist
                            comp.add_pinbus(Bus(Inout, last_bus[0], last_bus[1]+1), msb2lsb_declaration=last_bus[2])
                            last_bus = None
                        comp.add_pin(Inout(pin))

                if last_bus:  # add the last bus if exist
                    comp.add_pinbus(Bus(Inout, last_bus[0], last_bus[1]+1), msb2lsb_declaration=last_bus[2])

            if params:  # add parameters
                for p in re_params.findall(params):
                    comp.set_spice_param(escape_name_check(p[0]), escape_name_check(p[1]))

            # save subckt content to look inside later
            if subckt_body:
                text_subckts.append((dev_name, subckt_body))

        elif action == 'instance':
            if groups[2] in analysis_type or groups[0] in forbidden_names:  # not instance - skip
                continue
            text_instances.append(groups)  # save to look inside later

    if text_instances:
        if top_cell_name in Component.all_components():
            comp = Component.get_component_by_name(top_cell_name)
        else:
            comp = Component(top_cell_name)
        if is_std_cell:
            comp.set_is_physical(True)
            comp.set_dont_write_verilog(True)

        # concatenate bit nets to busses. a[0], a[1] -> a with width 2
        nets = ' '.join([groups[1] for groups in text_instances])  # take only nets
        bus_nets = re_bus.findall(nets)  # takes only nets that belong to a bus
        bus_nets = sorted([(escape_name_check(n[0] or n[2]), int(n[1] or n[3])) for n in bus_nets])  # filter empty - '' and sort by name and bit
        for i, net in enumerate(bus_nets):
            if len(bus_nets) == i+1 or net[0] != bus_nets[i+1][0]:  # if reached msb or another bus, add netbus. net: (name, bit)
                if net[0] not in comp.pinbus_names():  # check if already exist as pinbus
                    comp.add_netbus(Bus(Net, net[0], net[1]+1))

    # instances connectivity part
    for groups in text_instances:
        inst_name, nets, dev_name, params = groups
        inst_name, dev_name = escape_name_check(inst_name), escape_name_check(dev_name)
        nets = re_pins_nets.findall(nets)

        if implicit_instance and dev_name not in Component.all_components():
            dev = Component(dev_name)
            dev.set_property('is_guessed', True)
            [dev.add_pin(Inout('A'+str(n))) for n in range(len(nets))]  # add pins to dev. A0, A1...
        else:
            dev = Component.get_component_by_name(dev_name)
        comp.add_subcomponent(dev, inst_name)

        for net, pin in zip(nets, dev.get_pins_ordered()):
            net = escape_name_check(net)
            if net in ['0', '1']:
                net = "1'b0" if net == '0' else "1'b1"
            elif net not in comp.net_names():
                comp.add_net(Net(net))
            comp.connect(net, inst_name+'.'+pin.get_object_name())  # connect net to pin of instance
        if params:
            for p in re_params.findall(params):  # add parameters
                p = escape_name_check(p[0]), escape_name_check(p[1])
                if p[1] in comp.get_spice_params():  # check if value is a parameter of comp
                    p = p[0], comp.get_spice_param(p[1])  # update parameter with his actual value
                dev.set_spice_param(p[0], p[1])

    # read subckt body content
    for dev_name, subckt_body in text_subckts:
        spectre2slm(subckt_body, top_cell_name=dev_name, implicit_instance=implicit_instance)

    return comp
