#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from fractions import Fraction
import unittest

from rate_monotonic import sufficient_condition

# FUNCTIONS ###########################################################################################################

class TestMethods(unittest.TestCase):

	def test_main(self) -> bool:
		return 0


	def test_utilization(self) -> bool:
		processes = [
			("0", "1", "1", "8", "0"),
			("0", "1", "2", "5", "0"),
			("0", "1", "2", "10", "0"),
		]
		assert Fraction(29, 40) == processor_use(processes)


	def test_sufficient_condition(self) -> bool:
		assert sufficient_condition(3) == 0.7797631496846196

if __name__ == '__main__':
	unittest.main()