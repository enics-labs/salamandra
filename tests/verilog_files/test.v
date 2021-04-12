// Copyright 2021 EnICS Labs, Bar-Ilan University.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

module io();
input i;
output o;
endmodule


module inst_newline();
input i;
output o;
io io(
    .i
    (
        i
    )
    ,
    .o
    (
        o
    )
    )
    ;
endmodule