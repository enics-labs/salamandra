# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():

    if test(is_metatest=False) is True:
        print('Pass')
    else:
        print('Failed')


def test(is_metatest):
    # test spectre files
    for v in os.listdir('spectre_files/'):
        implicit_instance = False
        if v == 'Scan_Chain.scs':
            implicit_instance = True
        comp = spectre2slm_file('spectre_files/' + v, top_cell_name=v[:-4], implicit_instance=implicit_instance)
        text1 = comp.write_spectre_to_file()
        if not is_metatest:
            print(text1)
            print('----------------------'*2)
        Component.delete_all_components()

        # read again and compare if its the same
        comp = spectre2slm(text1, top_cell_name=v[:-4], implicit_instance=implicit_instance)
        text2 = comp.write_spectre_to_file()

        if text1 != text2:
            return False
        Component.delete_all_components()
    return True


if __name__ == '__main__':
    main()
