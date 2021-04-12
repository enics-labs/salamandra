# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
    nand_r = verilog2slm_file('verilog_files/more/test_implicit_comp.v', implicit_instance=True)
    text = nand_r[0].write_verilog_to_file(path=None, include_descendants=True)
    if not is_metatest:
        print(text)
    return True


if __name__ == '__main__':
    main()
