# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    and_ = Component('and_')
    and_.add_pin(Input('A0'))
    and_.add_pin(Input('A1'))
    and_.add_pin(Output('Z'))
    # and_.connect_nets('A0', 'Z')
    # and_.connect_nets('A1', 'Z')
    and_.set_is_physical(True)

    or_ = Component('or_')
    or_.add_pin(Input('A0'))
    or_.add_pin(Input('A1'))
    or_.add_pin(Output('Z'))
    # or_.connect_nets('A0', 'Z')
    # or_.connect_nets('A1', 'Z')
    or_.set_is_physical(True)

    comp1 = Component('comp1')
    comp1.add_pin(Input('A'))
    comp1.add_pin(Output('Z0'))
    comp1.add_pin(Output('Z1'))
    comp1.add_subcomponent(and_, 'and')
    comp1.connect('A', 'and.A0')
    comp1.connect('A', 'and.A1')
    comp1.connect('Z0', 'and.Z')
    # comp1.connect_nets('A', 'Z1')

    comp2 = Component('comp2')
    comp2.add_pin(Input('A'))
    comp2.add_pin(Output('Z0'))
    comp2.add_pin(Output('Z1'))
    # comp2.connect_nets('A', 'Z0')
    # comp2.connect_nets('A', 'Z1')
    comp2.set_is_physical(True)

    comp3 = Component('comp3')
    comp3.add_pin(Input('A0'))
    comp3.add_pin(Input('A1'))
    comp3.add_pin(Output('Z'))
    comp3.add_subcomponent(or_, 'or')
    comp3.connect('A0', 'or.A0')
    comp3.connect('A1', 'or.A1')
    comp3.connect('Z', 'or.Z')

    comp4 = Component('comp4')
    comp4.add_pin(Input('A0'))
    comp4.add_pin(Input('A1'))
    comp4.add_pin(Output('Z'))
    # comp4.connect_nets('A0', 'Z')
    # comp4.connect_nets('A1', 'Z')
    comp4.set_is_physical(True)

    nand = Component('nand')
    nand.add_pin(Input('A0'))
    nand.add_pin(Input('A1'))
    nand.add_pin(Output('Z0'))
    nand.add_pin(Output('Z1'))
    nand.add_subcomponent(comp1, 'comp1')
    nand.add_subcomponent(comp2, 'comp2')
    nand.add_subcomponent(comp3, 'comp3')
    nand.add_subcomponent(comp4, 'comp4')

    nand.add_net(Net('net1'))
    nand.add_net(Net('net2'))
    nand.add_net(Net('net3'))
    nand.add_net(Net('net4'))

    nand.connect('A0', 'comp1.A')
    nand.connect('A1', 'comp2.A')
    nand.connect('Z0', 'comp3.Z')
    nand.connect('Z1', 'comp4.Z')

    nand.connect('net1', 'comp1.Z0')
    nand.connect('net1', 'comp3.A0')
    nand.connect('net2', 'comp1.Z1')
    nand.connect('net2', 'comp4.A0')
    nand.connect('net3', 'comp2.Z0')
    nand.connect('net3', 'comp3.A1')
    nand.connect('net4', 'comp2.Z1')
    nand.connect('net4', 'comp4.A1')

    chip = Component('chip')
    chip.add_pinbus(Bus(Input, 'A', 2))
    chip.add_pinbus(Bus(Output, 'Z', 2))
    chip.add_subcomponent(nand, 'nand')

    chip.connect('A[0]', 'nand.A0')
    chip.connect('A[1]', 'nand.A1')
    chip.connect('Z[0]', 'nand.Z0')
    chip.connect('Z[1]', 'nand.Z1')

    if not is_metatest:
        chip.graph()

    return True


if __name__ == '__main__':
    main()
