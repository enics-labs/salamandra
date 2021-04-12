# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    inv = Component('inv')
    inv.add_pin(Input('A'))
    inv.add_pin(Output('Z'))
    inv.set_is_physical(True)

    and_ = Component('and')
    and_.add_pin(Input('A1'))
    and_.add_pin(Input('A2'))
    and_.add_pin(Output('Z'))
    and_.set_is_physical(True)

    nand = Component('nand')
    nand.add_subcomponent(inv, 'inv')
    nand.add_subcomponent(and_, 'and')
    nand.add_pin(Input('A1'))
    nand.add_pin(Input('A2'))
    nand.add_pin(Input('A3'))
    nand.add_pin(Output('Z'))
    nand.connect('A1', 'and.A1')
    nand.connect('A2', 'and.A2')
    nand.add_net(Net('net'))
    nand.add_net(Net('net2'))
    nand.connect('net', 'and.Z')
    nand.connect('net', 'inv.A')
    nand.connect('Z', 'inv.Z')
    nand.connect_nets('A1', 'net2')

    chip = Component('chip')
    chip.add_pin(Input('A1'))
    chip.add_pin(Input('A2'))
    chip.add_pin(Output('Z'))
    chip.add_subcomponent(nand, 'nand')
    chip.add_subcomponent(nand, 'nand2')
    chip.add_subcomponent(inv, 'inv')
    chip.connect('A1', 'nand.A1')
    chip.connect('A1', 'nand2.A1')
    chip.connect('A2', 'nand.A2')
    chip.connect('A2', 'nand2.A2')
    chip.add_net(Net('net'))
    chip.connect('Z', 'nand2.Z')
    chip.connect('net', 'nand.Z')
    chip.connect('net', 'inv.A')
    chip.connect('Z', 'inv.Z')
    chip.connect("1'b0", 'nand.A3')
    Component.PIN_SEPARATOR = '.'
    Component.HIERARCHICAL_SEPARATOR = '/'
    all_connectivity, fan_out_connectivity, fan_in_connectivity = chip.connectivity_paths()
    a = chip.get_descendants_hierarchy(filter=lambda c: not c.is_virtual())
    return True


if __name__ == '__main__':
    main()
