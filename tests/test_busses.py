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
    inv.add_pinbus(Bus(Inout, 'VDD', (0, -1)))

    nor = Component('nor')
    nor.add_pinbus(Bus(Input, 'B', 2))
    nor.add_pinbus(Bus(Inout, 'VDD', 4))
    nor.add_pin(Output('Z'))
    nor.add_net(Net('A1_A2'))

    or_ = Component('or')
    or_.add_pinbus(Bus(Input, 'A', 2))
    or_.add_pin(Output('Z'))
    or_.add_pin(Inout('VDD0'))
    or_.add_pin(Inout('VDD2'))

    nor.add_subcomponent(or_, 'i_or')
    nor.add_subcomponent(inv, 'i_inv')
    nor.connect_bus('B', 'i_or.A')
    nor.connect('A1_A2', 'i_or.Z')
    nor.connect('A1_A2', 'i_inv.A')
    nor.connect('Z', 'i_inv.Z')

    nor.connect('VDD[0]', 'i_or.VDD0')
    nor.connect('VDD[2]', 'i_or.VDD2')
    nor.connect('VDD[1]', 'i_inv.VDD[0]')
    nor.connect('VDD[1]', 'i_inv.VDD[-1]')

    if not is_metatest:
        print('before disconnect')
        for l in nor.write_verilog():
            print(l)

    nor.disconnect_bus('i_or.A')
    nor.disconnect_bus('i_inv.VDD')

    if not is_metatest:
        print('after disconnect')
        for l in nor.write_verilog():
            print(l)

    return True


if __name__ == '__main__':
    main()
