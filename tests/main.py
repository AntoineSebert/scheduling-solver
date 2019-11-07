#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# IMPORTS #############################################################################################################


import unittest
from fractions import Fraction
from unittest import TestCase

from rate_monotonic import processor_use, sufficient_condition


# FUNCTIONS ###########################################################################################################


class TestMethods(TestCase):

	def test_main(self: TestCase) -> bool:
		return 0

	def test_utilization(self: TestCase) -> bool:
		processes = [
			("0", "1", "1", "8", "0"),
			("0", "1", "2", "5", "0"),
			("0", "1", "2", "10", "0"),
		]
		assert Fraction(29, 40) == processor_use(processes)

	def test_sufficient_condition(self: TestCase) -> bool:
		assert sufficient_condition(3) == 0.7797631496846196


if __name__ == '__main__':
	unittest.main()
