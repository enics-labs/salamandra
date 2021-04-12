# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from .pin import Pin
class Inout(Pin):
    def verilog_type(self):
        return 'inout'
