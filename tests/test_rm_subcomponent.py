# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import os, sys
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    inv = Component('inv')
    inv.add_pin(Input('A'))
    inv.add_pin(Output('Z'))

    and_ = Component('and')
    and_.add_pin(Input('A1'))
    and_.add_pin(Input('A2'))
    and_.add_pin(Input('AA'))
    and_.add_pinbus(Bus(Input, 'B', 2))
    and_.add_pin(Output('Z'))

    nand = Component('nand')
    nand.add_pin(Input('A1'))
    nand.add_pin(Input('A2'))
    nand.add_pinbus(Bus(Input, 'bus', 2))
    nand.add_pin(Output('Z'))
    nand.add_net(Net('A1A2'))

    nand.add_subcomponent(and_, 'i_and')
    nand.add_subcomponent(inv, 'i_inv')
    nand.connect_bus('bus', 'i_and.B')
    nand.connect('A1', 'i_and.A1')
    nand.connect('A2', 'i_and.A2')
    nand.connect('A1A2', 'i_and.Z')
    nand.connect('A1A2', 'i_inv.A')
    nand.connect('Z', 'i_inv.Z')

    if not is_metatest:
        print('before removing i_and')
        nand.print_verilog()

    nand.remove_subcomponent('i_and')

    if not is_metatest:
        print('\n\nafter removing i_and')
        nand.print_verilog()

    nand.remove_subcomponents()

    if not is_metatest:
        print('\n\nafter removing all')
        nand.print_verilog()
        
    return True


if __name__ == '__main__':
    main()
