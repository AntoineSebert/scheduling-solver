# -*- coding: utf-8 -*-

"""This module aims to solve task scheduling problems."""

"""
Resources
- https://algorithm-visualizer.org/greedy/job-scheduling-problem
- https://visualgo.net/en/graphds

Data structure : acyclic directed weighted graph

Analysis
- https://github.com/nedbat/coveragepy
- https://github.com/facebook/pyre-check
- https://github.com/python/mypy
- https://gitlab.com/pycqa/flake8
"""

# IMPORTS #############################################################################################################

import argparse
from typing import *
from collections import namedtuple
from fractions import Fraction

# DATA STRUCTURES #####################################################################################################

File_pair = namedtuple('File_pair', ['tsk', 'cfg'])
Node = namedtuple("Node", ["id", "name", "wcet", "period", "deadline"])
Edge = namedtuple("Edge", ["source", "dest", "cost"])
"""
Processor = []
Architecture = [Processor]
"""

# FUNCTIONS ###########################################################################################################

def get_input_files() -> File_pair:
	"""Get the filepath for the .tsk and .cfg files from the command line."""

	parser = argparse.ArgumentParser(prog='SOLVER', description = 'Solve scheduling problems.', allow_abbrev=True)
	parser.add_argument(
		"--task",
		nargs = '?',
		type = argparse.FileType('r', encoding="utf-8"),
		default = "data/case_1.tsk",
		help = "Import problem description from TASK file"
	)
	parser.add_argument(
		"--conf",
		nargs = '?',
		type = argparse.FileType('r', encoding="utf-8"),
		default = "data/case_1.cfg",
		help = "Import system configuration from CONFIGURATION file"
	)
	parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
	args = parser.parse_args()

	return File_pair(tsk=args.task, cfg=args.conf)

def utilization(processes: List[Node]) -> float:
	"""Determine the utilization load carried by a list of tasks."""

	return sum([Fraction(int(n.wcet), int(n.period)) for n in processes])

def sufficient_condition(count: int) -> float:
	"""Determine the sufficient condition for schedulability of a processor or core."""

	return count * (pow(2, 1 / count) - 1)

def is_schedulable(processes: List[Node]) -> bool:
	"""Returns 'True' if a set of periodic tasks are schedulable, and 'False' otherise."""

	return processor_use(processes) <= sufficient_condition(len(processes))

# ENTRY POINT #########################################################################################################

def main():
	"""Script entry point"""

	# import files
	file_pair = get_input_files()
	print("Files imported: ")
	print("\t" + file_pair.tsk.name)
	print("\t" + file_pair.cfg.name)

if __name__ == "__main__":
	main()

# Tests
def test_main():
	return 0