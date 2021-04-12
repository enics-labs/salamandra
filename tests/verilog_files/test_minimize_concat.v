// Copyright 2021 EnICS Labs, Bar-Ilan University.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

module and (a,b,c,d,A_b, Z);

	//ports
	input [24:0] A_b;
	input [-5:5] c;
    input [5:-5] d;
	input [7:4] a;
    input [0:3] b;
	output Z;

	//wires
	wire [24:0] A_b;
	wire Z;

endmodule


module nand ();

	//wires
	wire [1:0] A_b;
	wire GND;
	wire VDD;

	//instances
	and i_and(.a(),.b(),.c(),.d(),.A_b({1'bx, GND, {3{VDD, {2{VDD, GND}}}}, 4'bx100, A_b[1:0], 2'bxx}), .Z());

endmodule
