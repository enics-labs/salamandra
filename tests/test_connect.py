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
    inv.add_pinbus(Bus(Input, 'A_b', 2))
    inv.add_pin(Output('Z'))

    and_ = Component('and')
    and_.add_pin(Input('A1'))
    and_.add_pin(Input('A2'))
    and_.add_pin(Output('Z'))

    nand = Component('nand')
    nand.add_pin(Input('A1'))
    nand.add_pin(Input('A2'))
    nand.add_pin(Output('Z'))

    A1_nand = nand.get_net('A1')
    A2_nand = nand.get_net('A2')
    Z_nand = nand.get_net('Z')

    A1A2_nand = Net('A1A2')
    A_b_nand = Bus(Net, 'A_b', 2)

    nand.add_net(A1A2_nand)
    nand.add_netbus(A_b_nand)

    nand.add_subcomponent(and_, 'i_and')
    nand.add_subcomponent(inv, 'i_inv')
    nand.connect(A1_nand, 'i_and.A1')
    nand.connect(A2_nand, 'i_and.A2')
    nand.connect(A1A2_nand, 'i_and.Z')
    nand.connect(A1A2_nand, 'i_inv.A')
    nand.connect(Z_nand, 'i_inv.Z')
    nand.connect_bus(A_b_nand, 'i_inv.A_b')

    if not is_metatest:
        nand.print_verilog()
    return True


if __name__ == '__main__':
    main()