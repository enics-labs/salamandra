# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    D = Component('my_buf')

    pvdd = Inout('VDD')
    pvss = Inout('VSS')
    pi = Input('I')
    pz = Output('Z')
    pb = Bus(Input, 'addr', 5)

    D.add_pin(pvdd)
    D.add_pin(pvss)
    D.add_pin(pi)
    D.add_pin(pz)
    D.add_pinbus(pb)

    B = Component('my_dll')
    B.add_pin(Inout('VDD'))
    B.add_pin(Inout('VSS'))
    B.add_pin(Input('sig'))
    B.add_pin(Output('sig_del'))
    B.add_subcomponent(D, 'buf1')
    B.add_component(D, 'buf2')

    # add_pin automatically creates pin and connects them
    # B.add_net(Net('VDD'))
    # B.add_net(Net('VSS'))
    # B.add_net(Net('sig'))
    # B.add_net(Net('sig_del'))
    # B.connect('VDD', 'VDD')
    # B.connect('VSS', 'VSS')
    # B.connect('sig', 'sig')
    # B.connect('sig_del', 'sig_del')
    # B.connect('sig_del', 'sig_del')

    B.add_net(Net('salamandra'))

    B.connect('VDD', 'buf1.VDD')
    B.connect('VSS', 'buf1.VSS')
    B.connect('sig', 'buf1.I')
    B.connect('salamandra', 'buf1.Z')
    # B.connect('sig_del', 'buf1.Z')

    B.connect('VDD', 'buf2.VDD')
    B.connect('VSS', 'buf2.VSS')
    B.connect('salamandra', 'buf2.I')
    B.connect('sig_del', 'buf2.Z')
    # B.connect('sig_del', 'buf2.Z')

    B.add_netbus(Bus(Net, 'address', 5))
    # B.connect('address[0]', 'buf1.addr[0]')
    # B.connect('address[1]', 'buf1.addr[1]')
    # B.connect('address[2]', 'buf1.addr[2]')
    # B.connect('address[3]', 'buf1.addr[3]')
    # B.connect('address[4]', 'buf1.addr[4]')
    B.connect_bus('address', 'buf1.addr')

    for x in B.write_verilog():
        if not is_metatest:
            print(x)
    for x in D.write_verilog():
        if not is_metatest:
            print(x)

    return True


if __name__ == '__main__':
    main()


