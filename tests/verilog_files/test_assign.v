// Copyright 2021 EnICS Labs, Bar-Ilan University.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

module comp (A1, A2, Z);

	//ports
	input A1;
	input A2;
	output Z;

	//wires
	wire A1;
	wire A2;
	wire Z;

    wire [7:0] A_buss2;
	wire [1:0] A_buss;
	wire B1;
	wire B2;

	//assignments
	assign Z = A2;
	assign {Z, B1} = {A2, A1};
	assign A_buss = {A2, A1};
	assign A_buss = { 2{B1} };
	assign A_buss2 = { {2{B1}}, A_buss, B2, 3'b10x};

	//instances

endmodule
