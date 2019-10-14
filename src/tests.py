#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://docs.python.org/3/library/unittest.html

# IMPORTS #############################################################################################################

import Fraction

from rate_monotonic import sufficient_condition, processor_use

# FUNCTIONS ###########################################################################################################


def test_main() -> bool:
	return 0


def test_utilization() -> bool:
	processes = [
		("0", "1", "1", "8", "0"),
		("0", "1", "2", "5", "0"),
		("0", "1", "2", "10", "0"),
	]
	assert Fraction(29, 40) == processor_use(processes)


def test_sufficient_condition() -> bool:
	assert sufficient_condition(3) == 0.7797631496846196
