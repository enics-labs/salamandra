# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    D = Component('my_buffer')

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

    B = Component('my_dll_')
    B.add_pin(Inout('VDD'))
    B.add_pin(Inout('VSS'))
    B.add_pin(Input('sig'))
    B.add_pin(Output('sig_del'))
    B.add_component(D, 'buf1')
    B.add_component(D, 'buf2')

    B.add_net(Net('salamandra'))

    B.connect('VDD', 'buf1.VDD')
    B.connect('VSS', 'buf1.VSS')
    B.connect('sig', 'buf1.I')
    B.connect('salamandra', 'buf1.Z')

    B.connect('VSS', 'buf2.VSS')
    B.connect('VDD', 'buf2.VDD')
    B.connect('salamandra', 'buf2.I')
    B.connect('sig_del', 'buf2.Z')

    B.add_netbus(Bus(Net, 'address', 5))
    B.connect_bus('address', 'buf1.addr')
    B.connect_bus('address', 'buf2.addr')

    D.set_spice_param('w', 120E-9)
    D.set_spice_param("l", 60E-9)
    D.set_spice_param("mult", 2)

    B.add_spectre_code('// hello world B')
    D.add_spectre_code('// hello world D')

    text = B.write_spectre_to_file()
    if not is_metatest:
        print(text)

    B.set_spice_param("w", 240E-9)
    if not is_metatest:
        print(B.get_spice_params())
    return True


if __name__ == '__main__':
    main()




