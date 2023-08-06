#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_aggnf
----------------------------------

Tests for `aggnf` module.
"""

import unittest

#import aggnf
from aggnf import cli


class TestAggnf(unittest.TestCase):
    def setUp(self):
        pass

    def test_counter(self):
        data = []
        d = {n: n // 2 for n in range(30)}
        for k in d:
            data.append('%s\t%s\n' % (k, d[k]))

        cnt = cli.countfile(in_data=data, sep=None, fieldnum=-1,
                            ignore_err=False)

        #print(repr(cnt))
        assert (cnt['5'] == 2)

    def tearDown(self):
        pass
