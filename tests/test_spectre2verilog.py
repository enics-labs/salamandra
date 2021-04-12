# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from salamandra import *


def main():

    if test(is_metatest=False) is True:
        print('Pass')
    else:
        print('Failed')


def test(is_metatest):
    # create nmos and pmos to be able to read spectre file
    pmos = Component('pch_lvt_mac')
    nmos = Component('nch_lvt_mac')
    comps = [pmos, nmos]
    for com in comps:
        com.add_pin(Inout('D'))
        com.add_pin(Inout('G'))
        com.add_pin(Inout('S'))
        com.add_pin(Inout('B'))
        com.set_dont_write_verilog(True)
        com.set_is_physical(True)

    lsr = spectre2slm_file('spectre_files/Scan_Chain.scs', top_cell_name='Latched_Shift_Register_360')
    # adding pins to top cell (without wires(nets) because they already exist)
    lsr.add_pinbus(Bus(Output, 'Q', 360))
    lsr.add_pinbus(Bus(Output, 'Q_B', 360))
    lsr.add_pin(Input('SCLK'))
    lsr.add_pin(Input('SDATA'))
    lsr.add_pin(Inout('VDD'))
    lsr.add_pin(Inout('VSS'))

    text = lsr.write_verilog_to_file(include_descendants=True)
    if not is_metatest:
        print(text)
        # lsr.write_spectre_to_file('junk/check.scs')
        # lsr.write_verilog_to_file('junk/check2.v', include_descendants=True)
    return True


if __name__ == '__main__':
    main()
