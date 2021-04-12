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
    inv.connect_nets('A', 'Z')

    and_ = Component('and')
    and_.add_pin(Input('A1'))
    and_.add_pin(Input('A2'))
    and_.add_pin(Output('Z'))
    and_.connect_nets('A1', 'Z')
    and_.connect_nets(and_.get_net('A2'), and_.get_net('Z'))

    nand = Component('nand')
    nand.add_pinbus(Bus(Input, 'A', 2))
    nand.add_netbus(Bus(Net, 'B', 2))
    nand.connect_netbusses('A', 'B')
    nand.add_pin(Output('Z'))
    nand.add_net(Net('B0B1'))
    nand.add_component(and_, 'i_and')
    nand.add_component(inv, 'i_inv')
    nand.connect('B[0]', 'i_and.A1')
    nand.connect('B[1]', 'i_and.A2')
    nand.connect('B0B1', 'i_and.Z')
    nand.connect('B0B1', 'i_inv.A')
    nand.connect('Z', 'i_inv.Z')

    SoC = Component('SoC')
    SoC.add_pinbus(Bus(Input, 'A', 2))
    SoC.add_pin(Input('B1'))
    SoC.add_pin(Input('B2'))
    SoC.add_net(Net('B1B2'))
    SoC.add_pin(Output('Z1'))
    SoC.add_pin(Output('Z2'))

    SoC.add_subcomponent(nand, 'i_nand')
    SoC.add_subcomponent(and_, 'i_and')
    SoC.add_subcomponent(inv, 'i_inv')
    SoC.connect_bus('A', 'i_nand.A')
    SoC.connect('Z1', 'i_nand.Z')

    SoC.connect('B1', 'i_and.A1')
    SoC.connect('B2', 'i_and.A2')
    SoC.connect('B1B2', 'i_and.Z')
    SoC.connect('B1B2', 'i_inv.A')
    SoC.connect('Z2', 'i_inv.Z')

    if not is_metatest:
        SoC.print_verilog(include_descendants=True)
    return True


if __name__ == '__main__':
    main()