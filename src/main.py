#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module aims to solve task scheduling problems.

Usage:
	main.py --version
	main.py (-h | --help)
	main.py folder <DATASET_FOLDER>
	main.py folder <DATASET_FOLDER> --verbose

Arguments:
	folder <DATASET_FOLDER>		The dataset folder that must contain one *.tsk file and one *.cfg file.

Options:
	-h --help		Show this screen.
	--version		Show version.
	--verbose		Toggle verbose output.
"""

"""
Resources
- https://algorithm-visualizer.org/greedy/job-scheduling-problem
- https://visualgo.net/en/graphds
- https://docs.microsoft.com/en-us/visualstudio/python/working-with-c-cpp-python-in-visual-studio?view=vs-2019
- https://numpydoc.readthedocs.io/en/latest/format.html

Design patterns : https://github.com/faif/python-patterns/blob/master/patterns/behavioral/chain_of_responsibility__py3.py

Static analysis
	tests :				https://github.com/pytest-dev/pytest
	type checking :		https://github.com/python/mypy
	style & quality :	https://gitlab.com/pycqa/flake8
	lint :				https://github.com/psf/black
Runtime analysis
	https://github.com/nedbat/coveragepy
	https://github.com/agermanidis/livepython
	https://github.com/benfred/py-spy
"""

# IMPORTS #############################################################################################################

from argparse import ArgumentParser
from pathlib import Path
import logging

from builder import problem_builder
from solver import scheduler
from log import colored_handler

# FUNCTIONS ###########################################################################################################

def create_cli_parser() -> ArgumentParser:
	"""Creates a CLI argument parser and returns it.

	Returns
	-------
	ArgumentParser
		An `ArgumentParser` object.
	"""

	parser = ArgumentParser(prog='SOLVER', description='Solve scheduling problems using graph coloration.', allow_abbrev=True)
	parser.add_argument(
		"folder",
		type = Path,
		help = "Import problem description from FOLDER (the first *.tsk and *.cfg files found are taken, all potential others are ignored)."
	)
	parser.add_argument(
		"--verbose",
		action='store_const',
		const=True,
		help = "Toggle program verbosity."
	)
	parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')

	return parser

# ENTRY POINT #########################################################################################################

def main() -> int:
	"""Script entry point.

	Returns
	-------
	int
		Returns `0` if no error has been encountered, and an other value otherwise.
	"""

	args = create_cli_parser().parse_args()
	logging.getLogger().addHandler(colored_handler(verbose=False if args.verbose == None else True))

	graph = problem_builder(args.folder)
	# display
	"""
	pos = nx.layout.spring_layout(G)
	nx.draw_networkx(G, pos)
	plt.show()
	draw_console(graph)
	"""
	#solution = scheduler(graph)

	return 0

if __name__ == "__main__":
	main()