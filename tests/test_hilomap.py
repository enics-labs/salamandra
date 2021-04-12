# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    nand = Component('nand')
    and_ = Component('and2')
    and_.add_pinbus(Bus(Output, 'A_b_o', 8))
    and_.add_pinbus(Bus(Output, 'A_b_o2', 8))
    and_.add_pinbus(Bus(Input, 'A_b_i', 8))
    and_.add_pin(Input('A'))
    nand.add_subcomponent(and_, 'i_and')
    nand.add_pinbus(Bus(Input, 'A_b', 5))
    nand.add_pin(Input('A'))
    nand.add_pinbus(Bus(Output, 'Z', 3))
    nand.add_subcomponent(and_, 'i_and2')

    nand.connect('Z[1]', 'i_and.A_b_o[5]')
    nand.connect('Z[0]', 'i_and.A_b_o[4]')
    nand.connect_nets("1'b1", 'Z[2]')

    nand.connect('1\'b1', 'i_and.A_b_i[7]')
    nand.connect('1\'b0', 'i_and.A_b_i[6]')
    nand.connect('A_b[2]', 'i_and.A_b_i[5]')
    nand.connect('A_b[1]', 'i_and.A_b_i[4]')
    nand.connect('1\'b0', 'i_and.A_b_i[3]')
    nand.connect('1\'b0', 'i_and.A_b_i[2]')

    tielo = Component('tielo')
    tielo.add_pin(Output('Y'))

    tiehi = Component('tiehi')
    tiehi.add_pin(Output('Y'))

    nand.legalize()

    if not is_metatest:
        print('\n------Before hilomap------')
        nand.print_verilog()

    nand.hilomap(tielo=tielo, tiehi=tiehi)

    if not is_metatest:
        print('\n------After hilomap------')
        nand.print_verilog()
    return True


if __name__ == '__main__':
    main()
