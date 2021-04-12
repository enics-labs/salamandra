# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.insert(0, os.path.abspath('..'))
import salamandra as slm


def main():
    test(is_metatest=False)


def test(is_metatest):
    m = slm.Component('m')

    m.add_pinbus(slm.Bus(slm.Input, 'I', 8, signed=True))
    m.add_pinbus(slm.Bus(slm.Input, 'Iu', 8, signed=False))
    m.add_netbus(slm.Bus(slm.Net, 'N', 8, signed=True))
    m.add_netbus(slm.Bus(slm.Net, 'Nu', 8, signed=False))
    m.add_pinbus(slm.Bus(slm.Output, 'X', 8))

    if not is_metatest:
        for l in m.write_verilog():
            print(l)
    return True


if __name__ == '__main__':
    main()
