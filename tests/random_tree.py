# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import os, sys
sys.path.append(os.path.abspath('..'))
from salamandra import *
import random
import math


def random_tree(N, prob = None):
    """returns a random tree consists of N components: C0, C1, .. C(N-1)
    each component Ci only instantiates components Cj, such that j>i
    """
    C = []

    if not prob:
        prob = 1/math.sqrt(N)

    for i in range(N):
        C.append(Component('C'+str(i)))

    for i in range(N):
        for j in range(i+1, N):
            if random.uniform(0, 1) < prob:
                C[i].add_subcomponent(C[j], 'i_'+str(j))

    return C


def main():
    N = 20
    prob = 0.5
    coms = random_tree(N, prob)
    for module in coms:
        for line in module.write_verilog():
            print(line)


if __name__ == '__main__':
    main()
