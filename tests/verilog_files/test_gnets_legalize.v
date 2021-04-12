// Copyright 2021 EnICS Labs, Bar-Ilan University.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

module and2 (A, A_b_i, A_b_o, A_b_o2);

	//ports
	input [7:0] A_b_i;
    output [7:0] A_b_o;
	output [7:0] A_b_o2;
	input A;

	//wires
	wire [7:0] A_b_i;
    wire [7:0] A_b_o;
	wire [7:0] A_b_o2;
	wire A;

endmodule


module nand (A, A_b);

	//ports
	input [4:0] A_b;
	input A;

	//wires
	wire [4:0] A_b;
	wire A;
	wire UC_0;
	wire UC_1;
	wire UC_2;
	wire UC_3;

	//instances
	and2 i_and0(.A(1'b0), .A_b_i({2'b10, A_b[2:1], 4'b00xx}), .A_b_o({2'b11, A_b[2:1], 2'b00, UC_0, UC_1}), .A_b_o2());
	and2 i_and1(.A(1'b0), .A_b_i({2'b10, A_b[2:1], 4'b00xx}), .A_b_o({2'b11, A_b[2:1], 2'b00, UC_2, UC_3}), .A_b_o2());

endmodule


module nand2 (A, A_b);

	//ports
	input [4:0] A_b;
	input A;

	//wires
	wire [4:0] A_b;
	wire A;
	wire UC_4;
	wire UC_5;
	wire UC_6;
	wire UC_7;

	//instances
	and2 i_and0(.A(1'b0), .A_b_i({2'b10, A_b[2:1], 4'b00xx}), .A_b_o({2'b11, A_b[2:1], 2'b00, UC_4, UC_5}), .A_b_o2());
	and2 i_and1(.A(1'b0), .A_b_i({2'b10, A_b[2:1], 4'b00xx}), .A_b_o({2'b11, A_b[2:1], 2'b00, UC_6, UC_7}), .A_b_o2());

endmodule
