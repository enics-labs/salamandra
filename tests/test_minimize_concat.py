# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    and_ = Component('and')
    and_.add_pinbus(Bus(Input, 'A_b', 16))
    and_.add_pin(Output('Z'))

    nand = Component('nand')
    nand.add_netbus(Bus(Net, 'A_b', 5))
    nand.add_net(Net('VDD'))
    nand.add_net(Net('GND'))

    nand.add_subcomponent(and_, 'i_and')
    nand.connect('A_b[0]', 'i_and.A_b[2]')
    nand.connect('A_b[1]', 'i_and.A_b[3]')
    nand.connect("1'b0", 'i_and.A_b[4]')
    nand.connect("1'b0", 'i_and.A_b[5]')
    nand.connect("1'b1", 'i_and.A_b[6]')
    nand.connect("1'bx", 'i_and.A_b[7]')
    nand.connect("VDD", 'i_and.A_b[8]')
    nand.connect("VDD", 'i_and.A_b[9]')
    nand.connect("VDD", 'i_and.A_b[10]')
    nand.connect("GND", 'i_and.A_b[11]')
    nand.connect('A_b[4]', 'i_and.A_b[12]')
    nand.connect('A_b[3]', 'i_and.A_b[13]')
    nand.connect('A_b[2]', 'i_and.A_b[14]')

    nand.legalize()
    text = nand.write_verilog_to_file()
    if not is_metatest:
        print(text)
    return True


if __name__ == '__main__':
    main()