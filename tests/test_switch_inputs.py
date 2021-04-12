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
    and_.add_pin(Input('A1'))
    and_.add_pin(Input('A2'))
    and_.add_pin(Output('Z'))

    nand = Component('nand')
    nand.add_pin(Input('A1'))
    nand.add_pin(Input('A2'))
    nand.add_pin(Output('Z'))

    nand.add_subcomponent(and_, 'i_and')
    nand.connect('A1', 'i_and.A1')
    nand.connect('A2', 'i_and.A2')
    nand.connect('Z', 'i_and.Z')

    old0 = nand.get_connected('i_and.A1')
    old1 = nand.get_connected('i_and.A2')

    nand.disconnect('i_and.A1')
    nand.disconnect('i_and.A2')

    nand.connect(old0, 'i_and.A2')
    nand.connect(old1, 'i_and.A1')

    if not is_metatest:
        nand.print_verilog()
    return True


if __name__ == '__main__':
    main()
