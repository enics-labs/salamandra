// Copyright 2021 EnICS Labs, Bar-Ilan University.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

module mux32 (I, SEL, Z);

	//ports
	input [31:0] I;
	input [4:0] SEL;
	output Z;

	//wires
	wire [31:0] I;
	wire [4:0] SEL;
	wire Z;
	wire int1;
	wire int2;

	//instances
	mux16 i_muxA(.I({I[15:0]}), .SEL({SEL[3:0]}), .Z(int1));
	mux16 i_muxB(.I({I[31:16]}), .SEL({SEL[3:0]}), .Z(int2));
	mux2 i_muxZ(.I({int2, int1}), .SEL({SEL[4]}), .Z(Z));

endmodule


module mux2 (I, SEL, Z);

	//ports
	input [1:0] I;
	input [0:0] SEL;
	output Z;

	//wires
	wire [1:0] I;
	wire [0:0] SEL;
	wire Z;

endmodule


module mux8 (I, SEL, Z);

	//ports
	input [7:0] I;
	input [2:0] SEL;
	output Z;

	//wires
	wire [7:0] I;
	wire [2:0] SEL;
	wire Z;
	wire int1;
	wire int2;

	//instances
	mux4 i_muxA(.I({I[3:0]}), .SEL({SEL[1:0]}), .Z(int1));
	mux4 i_muxB(.I({I[7:4]}), .SEL({SEL[1:0]}), .Z(int2));
	mux2 i_muxZ(.I({int2, int1}), .SEL({SEL[2]}), .Z(Z));

endmodule


module mux4 (I, SEL, Z);

	//ports
	input [3:0] I;
	input [1:0] SEL;
	output Z;

	//wires
	wire [3:0] I;
	wire [1:0] SEL;
	wire Z;
	wire int1;
	wire int2;

	//instances
	mux2 i_muxA(.I({I[1:0]}), .SEL({SEL[0]}), .Z(int1));
	mux2 i_muxB(.I({I[3:2]}), .SEL({SEL[0]}), .Z(int2));
	mux2 i_muxZ(.I({int2, int1}), .SEL({SEL[1]}), .Z(Z));

endmodule


module mux16 (I, SEL, Z);

	//ports
	input [15:0] I;
	input [3:0] SEL;
	output Z;

	//wires
	wire [15:0] I;
	wire [3:0] SEL;
	wire Z;
	wire int1;
	wire int2;

	//instances
	mux8 i_muxA(.I({I[7:0]}), .SEL({SEL[2:0]}), .Z(int1));
	mux8 i_muxB(.I({I[15:8]}), .SEL({SEL[2:0]}), .Z(int2));
	mux2 i_muxZ(.I({int2, int1}), .SEL({SEL[3]}), .Z(Z));

endmodule
