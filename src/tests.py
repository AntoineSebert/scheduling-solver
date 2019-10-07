#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from main import *

def test_main():
	return 0

def test_utilization():
	processes = [
		Node("0", "1", "1", "8", "0"),
		Node("0", "1", "2", "5", "0"),
		Node("0", "1", "2", "10", "0"),
	]
	assert Fraction(29, 40) == processor_use(processes)

def test_sufficient_condition():
	assert sufficient_condition(3) == 0.7797631496846196