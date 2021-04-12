
module comp (A, B, Z);

	//ports
	input [3:0] A;
	input B;
	output Z;

	//wires
	wire [3:0] A;
	wire B;
	wire Z;

	//instances
	comp1 mycomp1(.A({A[1:0]}), .B(B), .C(2'b0), .D(1'b0), .E(A), .F({2{B}}), .G({3'b0, A[3], B, {2{B}}, 1'b1}), .I(A[2]), .Z());

endmodule