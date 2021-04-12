# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))
from salamandra import *


def main():
    test(is_metatest=False)


def test(is_metatest):
	############################################
	####		define FlipFlop				####
	############################################
	FF = ComponentXY('FlipFlop')
	FF.add_pin(Input('D'))
	FF.add_pin(Output('Q'))
	FF.add_pin(Input('CK'))

	FF.set_component_dimensions(1.6, 2.4)

	############################################
	####		define Memory arrey			####
	############################################

	MEM = ComponentXY('MEM_arrey')

	MEM.add_pin(Input('clk'))
	MEM.add_pinbus(Bus(Input, 'WADDR', 2))
	MEM.add_pinbus(Bus(Input, 'RADDR', 2))
	MEM.add_pinbus(Bus(Input, 'DIN', 4))
	MEM.add_pinbus(Bus(Output, 'DOUT', 4))

	MEM.set_pin_position('clk', 5.8, 0.0, 'BOTTOM', 3)
	for i in range(4):
		MEM.set_pin_position('DIN[' + str(i) + ']', 1.2 + i, 0.0, 'BOTTOM', 2)
		MEM.set_pin_position('DOUT[' + str(i) + ']', 1.2 + i, 0.0, 'TOP', 2)

	for row in range(2 ** 2):
		for col in range(4):
			current_FF_name = 'Reg_' + str(row) + '_' + str(col)
			MEM.add_subcomponent(FF, current_FF_name, 1.6 * col, 2.4 * row)
			MEM.connect('clk', current_FF_name + '.CK')

	############################################
	####			outputs					####
	############################################
	if not is_metatest:
		for line in MEM.write_verilog():
			print(line)
		print("# -----------------------------------")
		for lines in sorted(MEM.write_tcl_placement_commands(tool='Synopsys')):
			for line in lines:
				print(line)
		print("# -----------------------------------")
		for line in MEM.write_pin_tcl_placement_commands():
			print(line)
		print("# -----------------------------------")
		print(MEM.write_floorPlan_tcl_commands('sc12_cln65lp'))

	return True


if __name__ == '__main__':
	main()


