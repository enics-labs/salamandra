# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import os, sys
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    inv = Component('inv')
    inv.add_pin(Input('A'))
    inv.add_pin(Output('Z'))
    inv.add_pinbus(Bus(Output, 'B', 2))

    nor = Component('nor')
    nor.add_pinbus(Bus(Input, 'A', 2))

    try:
        nor.add_pin(Input('A'))  # Exception: pin "A" already exists as pinbus in component
    except Exception as e:
        if e.args[0] != 'pin "A" already exists as pinbus in component':
            raise
    else:
        return False

    nor.add_pin(Output('Z'))
    nor.add_net(Net('A1_A2'))

    try:
        nor.add_netbus(Bus(Net, 'A1_A2', 2))  # Exception: netbus "A1_A2" already exists as net in component
    except Exception as e:
        if e.args[0] != 'netbus "A1_A2" already exists as net in component':
            raise
    else:
        return False

    nor.add_netbus(Bus(Net, 'net', 2))

    try:
        nor.add_net(Net('net'))  # Exception: net "net" already exists as netbus in component
    except Exception as e:
        if e.args[0] != 'net "net" already exists as netbus in component':
            raise
    else:
        return False

    or_ = Component('or')
    or_.add_pin(Input('A'))

    try:
        or_.add_pinbus(Bus(Input, 'A', 2))  # Exception: pinbus "A" already exists as pin in component
    except Exception as e:
        if e.args[0] != 'pinbus "A" already exists as pin in component':
            raise
    else:
        return False

    or_.add_pin(Output('Z'))

    nor.add_subcomponent(or_, 'i_or')
    nor.add_subcomponent(inv, 'i_inv')
    nor.connect('A1_A2', 'i_or.Z')
    nor.connect('A1_A2', 'i_inv.A')
    nor.connect('Z', 'i_inv.Z')

    if not is_metatest:
        for l in nor.write_verilog():
            print(l)

    return True


if __name__ == '__main__':
    main()
