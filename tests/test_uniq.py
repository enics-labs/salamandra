# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import os, sys
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def addComp(ucom):
    ucom[1] = Component('inv')
    ucom[1].add_pin(Input('A'))
    ucom[1].add_pin(Output('Z'))
    ucom[1].set_dont_uniq(True)

    ucom[2] = Component('buffer')
    ucom[2].add_pin(Input('A'))
    ucom[2].add_pin(Output('Z'))
    ucom[2].add_net(Net('A_'))
    ucom[2].add_component(ucom[1], 'inv1')
    ucom[2].add_component(ucom[1], 'inv2')
    ucom[2].connect('A', 'inv1.A')
    ucom[2].connect('A_', 'inv1.Z')
    ucom[2].connect('A_', 'inv2.A')
    ucom[2].connect('Z', 'inv2.Z')

    ucom[3] = Component('SoC')
    ucom[3].add_pinbus(Bus(Input, 'A', 2))
    ucom[3].add_pinbus(Bus(Output, 'Z', 2))
    ucom[3].add_netbus(Bus(Net, 'A_', 2))
    ucom[3].add_component(ucom[1], 'inv3')
    ucom[3].add_component(ucom[1], 'inv4')
    ucom[3].add_component(ucom[2], 'buff3')
    ucom[3].add_component(ucom[2], 'buff4')
    ucom[3].connect('A[0]', 'inv3.A')
    ucom[3].connect('A[1]', 'inv4.A')
    ucom[3].connect('A_[0]', 'inv3.Z')
    ucom[3].connect('A_[1]', 'inv4.Z')
    ucom[3].connect('A_[0]', 'buff3.A')
    ucom[3].connect('A_[1]', 'buff4.A')
    ucom[3].connect('Z[0]', 'buff3.Z')
    ucom[3].connect('Z[1]', 'buff4.Z')

    ucom[4] = Component('X')
    ucom[4].add_component(ucom[2], 'buffX')

    ucom[3].add_component(ucom[4], 'i_X')


def is_passed(com):
    count = com.count_instances()
    for inst in count:
        if count[inst] != 1:
            # check if inst is defined as dont_uniq
            if Component.get_component_by_name(inst).get_dont_uniq():
                continue
            return False
    return True


def test(is_metatest):
    ucom = {}
    addComp(ucom)
    if not is_metatest:
        print("--- === --- === --- BEFORE --- === --- === ---")
        show_verilog(ucom[3])
        print("////////////////////")
        print("-- Summary before: --")
        print(ucom[3].count_instances())

    ucom[3].uniq()
    result = is_passed(ucom[3])

    if not is_metatest:
        print("--- === --- === --- AFTER --- === --- === ---")
        show_verilog(ucom[3])
        print("////////////////////")
        print("-- Summary after: --")
        print(ucom[3].count_instances())
        print("Results:", 'Pass' if result else 'Failed')

    return result


def show_verilog(com):
    com.print_verilog(include_descendants=True)


if __name__ == '__main__':
    main()
