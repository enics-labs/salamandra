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

    and_ = Component('and')
    and_.add_pin(Input('A1'))
    and_.add_pin(Input('A2'))
    and_.add_pin(Output('Z'))

    nand = Component('nand')
    nand.add_pinbus(Bus(Input, 'A', 2))
    nand.add_pin(Output('Z'))
    nand.add_net(Net('A0A1'))
    nand.add_component(and_, 'i_and')
    nand.add_component(inv, 'i_inv')
    nand.connect('A[0]', 'i_and.A1')
    nand.connect('A[1]', 'i_and.A2')
    nand.connect('A0A1', 'i_and.Z')
    nand.connect('A0A1', 'i_inv.A')
    nand.connect('Z', 'i_inv.Z')

    # nand.remove_subcomponent('i_and')
    Component.delete_component(and_)
    try:
        nand.legalize()
    except:
        return True
    return False


if __name__ == '__main__':
    main()
