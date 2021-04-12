# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *
import math


def main():
    test(is_metatest=False)


def test(is_metatest):
    mux_dict = {}
    mux2and3(mux_dict)
    mux_ = mux(65, mux_dict)
    # mux32 = mux(32)
    # mux65.add_subcomponent(mux(59), 'x_mux32')

    if not is_metatest:
        for c in mux_.get_descendants(inclusive=True):
            for l in c.write_verilog():
                print(l)

    return True


def mux2and3(mux_dict):
    mux2 = Component('mux2')

    # pins
    mux2.add_pinbus(Bus(Input, 'I', 2))
    mux2.add_pinbus(Bus(Input, 'SEL', 1))
    mux2.add_pin(Output('Z'))

    mux3 = Component('mux3')

    # pins
    mux3.add_pinbus(Bus(Input, 'I', 3))
    mux3.add_pinbus(Bus(Input, 'SEL', 2))
    mux3.add_pin(Output('Z'))

    # sub-components
    mux3.add_component(mux2, 'i_mux1')
    mux3.add_component(mux2, 'i_mux2')

    # nets
    mux3.add_net(Net('int'))

    # connectivity
    mux3.connect('I[0]', 'i_mux1.I[0]')
    mux3.connect('I[1]', 'i_mux1.I[1]')
    mux3.connect('SEL[0]', 'i_mux1.SEL[0]')
    mux3.connect('int', 'i_mux1.Z')

    mux3.connect('int', 'i_mux2.I[0]')
    mux3.connect('I[2]', 'i_mux2.I[1]')
    mux3.connect('SEL[1]', 'i_mux2.SEL[0]')
    mux3.connect('Z', 'i_mux2.Z')

    mux_dict[2] = mux2
    mux_dict[3] = mux3


def mux(n, mux_dict):
    if n in mux_dict:
        return mux_dict[n]

    log_n = math.ceil(math.log2(n))
    m = Component('mux'+str(n))

    m.add_pinbus(Bus(Input, 'I', n))
    m.add_pinbus(Bus(Input, 'SEL', log_n))
    m.add_pin(Output('Z'))

    n1 = n//2
    n2 = n - n1

    m.add_component(mux(n1, mux_dict), 'i_muxA')
    m.add_component(mux(n2, mux_dict), 'i_muxB')
    m.add_component(mux(2, mux_dict),  'i_muxZ')

    m.add_net(Net('int1'))
    m.add_net(Net('int2'))

    for i in range(n1):
        m.connect('I['+str(i)+']', 'i_muxA.I['+str(i)+']')
    for i in range(n2):
        m.connect('I['+str(n1+i)+']', 'i_muxB.I['+str(i)+']')

    for i in range(math.ceil(math.log2(n1))):
        m.connect('SEL['+str(i)+']', 'i_muxA.SEL['+str(i)+']')
    for i in range(math.ceil(math.log2(n2))):
        m.connect('SEL['+str(i)+']', 'i_muxB.SEL['+str(i)+']')

    m.connect('int1', 'i_muxA.Z')
    m.connect('int1', 'i_muxZ.I[0]')
    m.connect('int2', 'i_muxB.Z')
    m.connect('int2', 'i_muxZ.I[1]')
    m.connect('SEL['+str(log_n-1)+']', 'i_muxZ.SEL[0]')
    m.connect('Z', 'i_muxZ.Z')

    mux_dict[n] = m
    return m


if __name__ == '__main__':
    main()
