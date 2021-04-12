# Copyright 2021 EnICS Labs, Bar-Ilan University.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0

import sys, os, importlib
sys.path.append(os.path.abspath('..'))
import glob
from salamandra import *


tests = [f[:-3] for f in glob.glob("test_*.py")]  # all tests files
tests.remove('test_topological')

success = 0
print('Tests Running\n')

for t in tests:
    test = importlib.import_module('tests.{}'.format(t))
    result = test.test(is_metatest=True)
    print('{} - {}'.format(t, result))
    if result:
        success += 1
    Component.delete_all_components()

print('\nTests Results: {}/{} Succeeded'.format(success, len(tests)))
