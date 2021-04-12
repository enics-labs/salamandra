# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    a = Component('A')
    a.add_pin(Pin('s'))
    a.add_pin(Input('g'))
    a.add_pin(Input('d'))
    a.add_pin(Input('b'))

    b = Component('B')
    b.add_pin(Pin('gate'))
    b.add_pin(Pin('source'))
    b.add_pin(Pin('body'))
    b.add_pin(Pin('drain'))

    a.add_subcomponent(b, 'B1')
    a.connect('g', 'B1.gate')
    a.connect('d', 'B1.drain')
    a.connect('s', 'B1.source')
    a.connect('b', 'B1.body')
    a.add_subcomponent(b, 'B2')
    a.connect('d', 'B2.drain')
    a.connect('g', 'B2.gate')
    a.connect('b', 'B2.body')
    a.connect('s', 'B2.source')

    if not is_metatest:
        for l in a.write_spectre():
            print(l)
    return True


if __name__ == '__main__':
    main()

