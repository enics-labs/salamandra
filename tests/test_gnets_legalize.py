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

    nand.connect("1'b0", 'i_and.A')
    # nand.connect('A_b[1]', 'i_and.A_b_o[4]')
    # nand.connect('A_b[2]', 'i_and.A_b_o[5]')

    nand.connect('1\'b0', 'i_and.A_b_i[2]')
    nand.connect('1\'b0', 'i_and.A_b_i[3]')
    nand.connect('A_b[1]', 'i_and.A_b_i[4]')
    nand.connect('A_b[2]', 'i_and.A_b_i[5]')
    nand.connect('1\'b0', 'i_and.A_b_i[6]')
    nand.connect('1\'b1', 'i_and.A_b_i[7]')

    nand2 = Component('nand2', nand)
    nand.legalize()
    nand2.legalize()
    if not is_metatest:
        # with open('verilog_files/{}.v'.format(re.findall(r'/(\w+)\.py', __file__)[0]), 'w') as f:
        #     for com in [and_, nand, nand2]:
        #         for l in com.write_verilog():
        #             f.write(l)
        #             f.write('\n')
        for com in [nand, nand2]:
            for l in com.write_verilog():
                print(l)
    return True


if __name__ == '__main__':
    main()
