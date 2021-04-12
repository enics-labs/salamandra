# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    inv = Component('ben')
    inv.add_pin(Input('A'))
    inv.add_pin(Output('Z'))
    inv.add_pin(Inout('VDD'))
    inv.add_pin(Inout('GND'))

    and_ = Component('and')
    and_.add_pin(Input('A1'))
    and_.add_pin(Input('A2'))
    and_.add_pin(Output('Z'))
    and_.add_pin(Inout('VDD'))
    and_.add_pin(Inout('GND'))

    nand = Component('nand')
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

    i_and_Z = nand._Component__virtual_pins[('i_and', 'Z')]

    if not is_metatest:
        print('before disconnect Zs')
        nand.print_verilog()

    nand.disconnect(i_and_Z)
    nand.disconnect('i_inv.Z')

    if not is_metatest:
        print('after disconnect Z')
        nand.print_verilog()

    return True


if __name__ == '__main__':
    main()
