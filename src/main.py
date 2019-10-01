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

from collections import namedtuple

# DATA STRUCTURES #####################################################################################################

File_pair = namedtuple('File_pair', ['tsk', 'cfg'])
Node = namedtuple("Node", ["id", "name", "wcet", "period", "deadline"])
Edge = namedtuple("Edge", ["source", "dest", "cost"])
"""
Processor = []
Architecture = [Processor]
"""

def main():
	"""Script entry point"""
	print("Hello, World!")

if __name__ == "__main__":
	main()

# Tests
def test_main():
	return 0