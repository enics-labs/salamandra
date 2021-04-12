# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import os, sys
sys.path.append(os.path.abspath('..'))
from salamandra import *
from tests.random_tree import *


N = 1000
C = random_tree(N)

T = C[0].topological(root_first = True)
for i in range(N):
    if C[i] in T:
        idx = T.index(C[i])
        for inst, dev in C[i].get_subcomponents():
            if T.index(dev) <= idx:
                raise Exception("topological order is broken", str(C[i]), str(dev))
print('topological root_first is OK')


T = C[0].topological(root_first = False)
for i in range(N):
    if C[i] in T:
        idx = T.index(C[i])
        for inst, dev in C[i].get_subcomponents():
            if T.index(dev) >= idx:
                raise Exception("topological order is broken", str(C[i]), str(dev))

print('topological leaf_first is OK too')

print('tree size is '+str(len(T)))
