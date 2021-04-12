# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

from .input import Input
from .output import Output
from .component import Component


class ComponentVIRT(Component):
    def __init__(self, name, comp, input_net, output_net):
        super().__init__(name)
        self.set_dont_write_verilog(True)
        self.input_pin = Input('I')
        self.output_pin = Output('O')
        self.add_pin(self.input_pin)
        self.add_pin(self.output_pin)

        self.input_net = input_net
        self.output_net = output_net
        self.comp = comp

    def verilog_declare(self):
        return 'assign {} = {};'.format(self.output_net, self.input_net)

    def is_virtual(self):
        return True
