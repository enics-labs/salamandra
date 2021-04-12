# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from .net import Net


class GNet(Net):  # Global Net like 0,1,x
    def verilog_type(self):
        return None

    def verilog_declare(self):
        return None

    @staticmethod
    def is_name_valid(name):
        return name in ["1'b0", "1'b1", "1'bx"]
