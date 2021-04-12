# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    inv = Component('inv')
    inv.add_pin(Input('A').set_property('tpd', 0.1))
    inv.add_pin(Output('Z').set_property('tpd', 0.3))
    inv.add_pin(Inout('VDD'))
    inv.add_pin(Inout('GND'))

    and_ = Component('and')
    and_.set_property('is_optimized', True)
    and_.add_pin(Input('A1'))
    and_.add_pin(Input('A2'))
    and_.add_pin(Output('Z'))
    and_.add_pin(Inout('VDD').set_property('is_supp', True))
    and_.add_pin(Inout('GND').set_property('is_supp', True))

    nand = Component('nand')
    nand.add_subcomponent(inv, 'inv')
    nand.add_subcomponent(and_, 'and')

    for comp in [inv, and_, nand]:
        a = comp.get_pins(filter=lambda p: p.get_property('tpd') and p.get_property('tpd') < 0.2)
        b = comp.get_pins(filter=lambda p: p.get_property('is_supp'))
        c = comp.get_subcomponents(filter=lambda p: p.get_property('is_optimized'))
    return True


if __name__ == '__main__':
    main()