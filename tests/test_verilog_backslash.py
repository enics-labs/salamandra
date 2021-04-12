# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    # with '\'
    nand = Component(r'\nand ')
    and_ = Component(r'\and ')
    and_.add_pinbus(Bus(Input, r'\A[0] ', 5))
    and_.add_netbus(Bus(Net, r'net', 5))
    and_.add_pin(Input(r'\A# '))
    and_.add_pinbus(Bus(Input, r'\AA# ', 2))
    or_ = Component(r'\or ')
    or_.add_pinbus(Bus(Input, r'\A ', 5))
    or_.set_is_physical(True)
    and_.add_subcomponent(or_, r'\or ')
    and_.connect_bus(r'\A[0] ', r'\or .\A ')
    nand.add_subcomponent(and_, r'\i_and ')
    nand.add_pin(Input(r'\B# '))
    nand.add_pinbus(Bus(Input, r'\BB# ', 1))
    nand.add_pinbus(Bus(Input, r'\A[0] ', 2))
    nand.add_pin(Input(r'\B[0] '))
    nand.add_netbus(Bus('Net', r'\A_buss[0] ', 5))
    nand.connect(r'\B# ', r'\i_and .\A# ')
    nand.connect(r'\BB# [0]', r'\i_and .\AA# [0]')
    nand.connect(r'\A_buss[0] [2]', r'\i_and .\A[0] [3]')
    nand.connect(r'\A_buss[0] [3]', r'\i_and .\A[0] [4]')
    nand.connect(r'\A_buss[0] [0]', r'\i_and .\A[0] [2]')
    nand.connect(r'\B[0] ', r'\i_and .\A[0] [0]')

    # without '\'
    nand2 = Component('nand')
    and2_ = Component('and2')
    and2_.add_pinbus(Bus(Input, 'A', 5))
    and2_.add_netbus(Bus(Net, 'net', 5))
    or2_ = Component('or')
    or2_.add_pinbus(Bus(Input, 'A', 5))
    or2_.set_is_physical(True)
    and2_.add_subcomponent(or2_, 'or')
    and2_.connect_bus('A', 'or.A')
    nand2.add_subcomponent(and2_, 'i_and')
    nand2.add_pinbus(Bus(Input, 'A', 2))
    nand2.add_pin(Input('B'))
    nand2.add_netbus(Bus('Net', 'A_buss', 5))
    nand2.connect('A_buss[2]', 'i_and.A[3]')
    nand2.connect('A_buss[3]', 'i_and.A[4]')
    nand2.connect('A_buss[0]', 'i_and.A[2]')
    nand2.connect('B', 'i_and.A[0]')

    if not is_metatest:
        print('------with backslash-------')
        nand.legalize()
        # nand.flatten()
        for l in nand.write_verilog():
            print(l)
        print('\n\n------without backslash-------')
        nand2.legalize()
        for l in nand2.write_verilog():
            print(l)
    return True


if __name__ == '__main__':
    main()
