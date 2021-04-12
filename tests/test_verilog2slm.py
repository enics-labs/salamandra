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

    # read sts_cells before syn/pnr or enable implicit_instance flag
    # std_cells = verilog2slm_file('verilog_files/more/std_cells.v', is_std_cell=True)
    # components = verilog2slm_file('verilog_files/more/syn.v')
    # components = verilog2slm_file('verilog_files/more/pnr.v', implicit_wire=True)
    # for com in components:
    #     if com.get_object_name() == 'riscv_core':
    #         all_connectivity, fan_out_connectivity, fan_in_connectivity = com.connectivity_paths()
    #         com.flatten()
    #     com.hilomap(tiehi=Component.get_component_by_name('TIEHI_X1M_A12TR'),
    #                 tielo=Component.get_component_by_name('TIELO_X1M_A12TR'))
    #     com.write_verilog_to_file('check_syn.v', append=True)


def test(is_metatest):
    # test verilog files
    for v in os.listdir('verilog_files/'):
        if v == 'more':
            continue
        if not is_metatest:
            print('reading '+v)
        components = verilog2slm_file('verilog_files/' + v)
        text1 = ''
        for com in components:
            text1 += com.write_verilog_to_file()
        if not is_metatest:
            print(text1)
            print('----------------------')
        Component.delete_all_components()

        # read again and compare if its the same
        components = verilog2slm(text1)
        text2 = ''
        for com in components:
            text2 += com.write_verilog_to_file()

        if text1 != text2:
            return False
        Component.delete_all_components()
    return True


if __name__ == '__main__':
    main()
