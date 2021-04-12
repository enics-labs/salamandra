# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os
sys.path.append(os.path.abspath('..'))

from salamandra import *


'''
This file builds two adders in Salamandra:
A ripple adder using a variable amount of full adders in parallel
A serial adder using a single full adder and a flip flop

Each adder is itself composed of logic gates

Some other components, like a short circuit, are also defined here but unused.

The purpose of this file was to create an environment with which to test 
all_connected(), all_fan_in(), & all_fan_out() in, but it may have other uses.
'''


def main():
	test(is_metatest=False)


def test(is_metatest):
	# Length of the ripple adder
	BITLENGTH = 6

	#########
	# GATES #
	#########

	inv = Component('inv')
	inv.add_pin(Input('A'))
	inv.add_pin(Output('Y'))
	inv.set_is_physical(True)
	inv.set_is_sequential(False)

	andgate = Component('and')
	andgate.add_pin(Input('A'))
	andgate.add_pin(Input('B'))
	andgate.add_pin(Output('Y'))
	andgate.set_is_physical(True)
	andgate.set_is_sequential(False)

	orgate = Component('or')
	orgate.add_pin(Input('A'))
	orgate.add_pin(Input('B'))
	orgate.add_pin(Output('Y'))
	orgate.set_is_physical(True)
	orgate.set_is_sequential(False)

	xor = Component('xor')
	xor.add_pin(Input('A'))
	xor.add_pin(Input('B'))
	xor.add_pin(Output('Y'))
	xor.set_is_physical(True)
	xor.set_is_sequential(False)

	#############
	# FLIP FLOP #
	#############

	FF = Component('flipflop')
	FF.add_pin(Input('D'))
	FF.add_pin(Output('Q'))
	FF.add_pin(Input('CK'))
	FF.set_is_physical(True)
	FF.set_is_sequential(True)

	#########
	# SHORT #
	#########
	'''
	This component isn't used in the adder.
	It's a simple short cirucit cell, 
	which can be used to test some edge cases 
	with all_connected and all_fan_in/out
	'''
	short = Component('short')
	short.add_pin_adds_net = False
	# pins
	short.add_pin(Input('A'))
	short.add_pin(Output('Y'))
	short.add_net(Net('shortnet'))
	short.connect('shortnet', 'A')
	short.connect('shortnet', 'Y')
	short.set_is_physical(True)
	short.set_is_sequential(False)

	#########
	# ADDER #
	#########

	adder = Component('adder')
	# pins
	adder.add_pin(Input('A'))
	adder.add_pin(Input('B'))
	adder.add_pin(Input('Cin'))
	adder.add_pin(Output('S'))
	adder.add_pin(Output('Cout'))
	# adder.set_is_physical(True)
	adder.set_is_sequential(False)

	# subcomponents
	adder.add_component(xor, 'xor0')
	adder.add_component(xor, 'xor1')
	adder.add_component(andgate, 'and0')
	adder.add_component(andgate, 'and1')
	adder.add_component(orgate, 'or')

	# nets
	adder.add_net(Net('XOROUT'))
	adder.add_net(Net('AND0OUT'))
	adder.add_net(Net('AND1OUT'))

	# connections
	adder.connect('A', 'xor0.A')
	adder.connect('B', 'xor0.B')
	adder.connect('XOROUT', 'xor0.Y')

	adder.connect('A', 'and0.A')
	adder.connect('B', 'and0.B')
	adder.connect('AND0OUT', 'and0.Y')

	adder.connect('XOROUT', 'xor1.A')
	adder.connect('Cin', 'xor1.B')
	adder.connect('S', 'xor1.Y')

	adder.connect('XOROUT', 'and1.A')
	adder.connect('Cin', 'and1.B')
	adder.connect('AND1OUT', 'and1.Y')

	adder.connect('AND0OUT', 'or.A')
	adder.connect('AND1OUT', 'or.B')
	adder.connect('Cout', 'or.Y')

	##########
	# RIPPLE #
	##########

	ripple = Component('ripple')
	ripple.set_is_sequential(True)

	# pins
	ripple.add_pinbus(Bus(Input, 'A', BITLENGTH))
	ripple.add_pinbus(Bus(Input, 'B', BITLENGTH))
	ripple.add_pinbus(Bus(Output, 'S', BITLENGTH))
	ripple.add_pin(Output('COUT'))
	ripple.add_pin(Inout('GND'))

	cnet = 'GND'

	for x in range(BITLENGTH):
		ripple.add_component(adder, 'adder' + str(x))
		ripple.connect(cnet, 'adder' + str(x) + '.Cin')
		ripple.connect('A' + str([x]), 'adder' + str(x) + '.A')
		ripple.connect('B' + str([x]), 'adder' + str(x) + '.B')
		ripple.connect('S' + str([x]), 'adder' + str(x) + '.S')
		cnet = 'COUT'
		if x < BITLENGTH - 1:
			cnet = 'adder' + str(x) + 'out'
			ripple.add_net(Net(cnet))
		ripple.connect(cnet, 'adder' + str(x) + '.Cout')

	##########
	# Serial #
	##########

	serial = Component('serial')

	# pins
	serial.add_pin(Input('A'))
	serial.add_pin(Input('B'))
	serial.add_pin(Output('S'))
	serial.add_pin(Input('CK'))

	# components
	serial.add_component(adder, 'adder')
	serial.add_component(FF, 'ff')

	# nets
	serial.add_net(Net('adderout'))
	serial.add_net(Net('ffout'))

	# connections
	serial.connect('A', 'adder.A')
	serial.connect('B', 'adder.B')
	serial.connect('S', 'adder.S')
	serial.connect('CK', 'ff.CK')
	serial.connect('adderout', 'adder.Cout')
	serial.connect('adderout', 'ff.D')
	serial.connect('ffout', 'ff.Q')
	serial.connect('ffout', 'adder.Cin')

	if not is_metatest:
		# f = open('ripple.v', 'w')
		for l in ripple.write_verilog():
			print(l)
			# f.write(l + '\n')
		# f.close

		# f = open('serial.v', 'w')
		for l in serial.write_verilog():
			# f.write(l + '\n')
			print(l)
		# f.close

	return True

if __name__ == '__main__':
	main()





