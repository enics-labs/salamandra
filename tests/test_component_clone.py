# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    inv = Component('inv')
    inv.add_pin(Input('A'))
    inv.add_pin(Output('Z'))
    inv.add_pin(Inout('VDD'))
    inv.add_pin(Inout('GND'))
    inv.set_is_physical(True)

    and_ = Component('and')
    and_.add_pin(Input('A1'))
    and_.add_pin(Input('A2'))
    and_.add_pin(Output('Z'))
    and_.add_pin(Inout('VDD'))
    and_.add_pin(Inout('GND'))
    and_.set_is_physical(True)

    nand = Component('nand')
    nand.add_net(Net('A1A2_2'))
    nand.add_pin(Input('A1'))
    nand.add_pin(Input('A2'))
    nand.add_pin(Output('Z'))
    nand.add_pin(Inout('VDD'))
    nand.add_pin(Inout('GND'))
    nand.add_net(Net('A1A2'))

    nand.add_subcomponent(and_, 'i_and')
    nand.add_subcomponent(inv, 'i_inv')
    nand.connect('VDD', 'i_and.VDD')
    nand.connect('GND', 'i_and.GND')
    nand.connect('VDD', 'i_inv.VDD')
    nand.connect('GND', 'i_inv.GND')
    nand.connect('A1', 'i_and.A1')
    nand.connect('A2', 'i_and.A2')
    nand.connect('A1A2', 'i_and.Z')
    nand.connect('A1A2', 'i_inv.A')
    nand.connect('Z', 'i_inv.Z')
    nand.connect_nets('VDD', 'GND')
    nand.set_property('is_optimized', True)

    nand2 = Component('nand2', original=nand)
    nand2.add_pin(Input('CLK'))
    nand2.disconnect('i_and.A2')
    nand2.connect('CLK', 'i_and.A2')

    nor = Component('nor')
    nor.add_pinbus(Bus(Input, 'A', 2))
    nor.add_pin(Output('Z'))

    or_ = Component('or')
    or_.add_pinbus(Bus(Input, 'A', 2))
    or_.add_pin(Output('Z'))

    nor.add_subcomponent(or_, 'i_or')
    nor.add_subcomponent(inv, 'i_inv_')
    nor.add_net(Net('A1_A2'))
    nor.connect_bus('A', 'i_or.A')
    nor.connect('A1_A2', 'i_or.Z')
    nor.connect('A1_A2', 'i_inv_.A')
    nor.connect('Z', 'i_inv_.Z')

    nor2 = Component('nor2', original=nor)
    # nor2.add_pin(Inout('VDD'))
    # nor2.disconnect('i_inv_.Z')
    # nor2.connect('VDD', 'i_inv_.Z')

    # nor2.add_pinbus(Bus(Input, 'CLK', 2))
    # nor2.disconnect_bus('i_or.A')
    # nor2.connect_bus('CLK', 'i_or.A')

    nor.add_pin(Inout('VDD'))
    nor.disconnect('i_inv_.Z')
    nor.connect('VDD', 'i_inv_.Z')

    nor.add_pinbus(Bus(Input, 'CLK', 2))
    nor.disconnect_bus('i_or.A')
    nor.connect_bus('CLK', 'i_or.A')

    mem = Component('mem')
    mem.add_pinbus(Bus(Input, 'A', 2))
    mem.add_pinbus(Bus(Output, 'Z', 2))

    buff = Component('buff')
    buff.add_pinbus(Bus(Input, 'A', 2))
    buff.add_pinbus(Bus(Output, 'Z', 2))
    buff2 = Component('buff2')
    buff2.add_pinbus(Bus(Input, 'A', 2))
    buff2.add_pinbus(Bus(Output, 'Z', 2))

    mem.add_subcomponent(buff, 'i_buff')
    mem.add_subcomponent(buff2, 'i_buff2')
    mem.connect_bus('A', 'i_buff.A')
    mem.add_netbus(Bus(Net, 'W', 2))
    mem.connect_bus('W', 'i_buff.Z')
    mem.connect_bus('W', 'i_buff2.A')
    mem.connect_bus('Z', 'i_buff2.Z')

    mem2 = Component('mem2', original=mem)

    if not is_metatest:
        for l in nand.write_verilog():
            print(l)
        print('-----------------------------')
        for l in nand2.write_verilog():
            print(l)
        print('-----------------------------')
        for l in nor.write_verilog():
            print(l)
        print('-----------------------------')
        for l in nor2.write_verilog():
            print(l)
        print('-----------------------------')
        for l in mem.write_verilog():
            print(l)
        print('-----------------------------')
        for l in mem2.write_verilog():
            print(l)

    return True


if __name__ == '__main__':
    main()
