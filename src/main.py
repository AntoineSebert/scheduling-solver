#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Resources
- https://algorithm-visualizer.org/greedy/job-scheduling-problem
- https://visualgo.net/en/graphds
- https://numpydoc.readthedocs.io/en/latest/format.html

Design patterns
- https://github.com/faif/python-patterns/blob/master/patterns/behavioral/chain_of_responsibility__py3.py

Static analysis
	tests :			https://github.com/pytest-dev/pytest
	type checking :	https://github.com/python/mypy
Runtime analysis
	https://github.com/nedbat/coveragepy
	https://github.com/agermanidis/livepython
	https://github.com/benfred/py-spy
"""

# IMPORTS #############################################################################################################

from log import colored_handler
from solver import scheduler
from builder import problem_builder
import logging
from pathlib import Path
from argparse import ArgumentParser
import timed

# FUNCTIONS ###########################################################################################################


def create_cli_parser() -> ArgumentParser:
	"""Creates a CLI argument parser and returns it.

	Returns
	-------
	parser : ArgumentParser
									An `ArgumentParser` object.
	"""

	parser = ArgumentParser(
		prog="SOLVER",
		description="Solve task scheduling problems using graph coloration.",
		allow_abbrev=True,
	)
	parser.add_argument(
		"folder",
		type=Path,
		help="Import problem description from FOLDER (only the first *.tsk and *.cfg files found are taken, \
		all potential others are ignored).",
	)
	parser.add_argument(
		"--verbose", action="store_const", const=True, help="Toggle program verbosity."
	)
	parser.add_argument("--version", action="version", version="%(prog)s 0.0.1")

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
	logging.getLogger().addHandler(
		colored_handler(verbose=False if args.verbose is None else True)
	)

	problem = problem_builder(args.folder)

	solution = scheduler(problem)

	logging.info("Finished. Total ellapsed time:" + str(timed.global_time) + "s.")

	return 0


if __name__ == "__main__":
	main()
