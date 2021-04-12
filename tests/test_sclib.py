# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    myGate = Component('coolGate')

    myXor3 = Xor3()
    myAoi21 = Aoi21()

    myGate.add_pin(Input('Bob1'))
    myGate.add_pin(Input('Bob2'))
    myGate.add_pin(Input('Bob3'))
    myGate.add_pin(Input('Bob4'))
    myGate.add_pin(Input('Bob5'))
    myGate.add_pin(Output('Z'))

    myGate.add_component(myXor3, 'coolXor')
    myGate.add_component(myAoi21, 'coolAoi')

    myGate.connect('Bob1', 'coolXor.A1')
    myGate.connect('Bob2', 'coolXor.A2')
    myGate.connect('Bob3', 'coolXor.A3')

    myGate.add_net(Net('xorZ'))
    myGate.connect('xorZ', 'coolXor.Z')
    myGate.connect('xorZ', 'coolAoi.A1')
    myGate.connect('Bob4', 'coolAoi.A2')
    myGate.connect('Bob5', 'coolAoi.B')
    myGate.connect('Z', 'coolAoi.ZN')

    if not is_metatest:
        for l in myGate.write_verilog():
            print(l)

    return True


if __name__ == '__main__':
    main()
