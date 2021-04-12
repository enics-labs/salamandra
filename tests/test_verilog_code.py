# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import os, sys
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    m = Component('MyModule')
    x = Net('yyy')
    m.add_net(x)
    code = "\tassign {}=1'b0;".format(x.get_object_name())
    m.add_verilog_code(code)

    result = False
    for i, l in enumerate(m.write_verilog()):
        if l.endswith('verilog code'):
            result = m.write_verilog()[i+1] == code
        if not is_metatest:
            print(l)

    return result


if __name__ == '__main__':
    main()
