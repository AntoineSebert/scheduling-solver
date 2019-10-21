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


import logging
from pathlib import Path
from argparse import ArgumentParser
from time import process_time
from typing import NoReturn

import timed
from log import colored_handler
from solver import scheduler
from builder import problem_builder


# FUNCTIONS ###########################################################################################################


def _create_parser_arg_group(parser: ArgumentParser) -> NoReturn:
	"""Adds a mutual exclusive group of arguments to the parser to handle dataset batch or single mode.

	Parameters
	----------
	parser : ArgumentParser
		An `ArgumentParser` object, that will be modified.
	"""

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument(
		"--case",
		type=Path,
		help="Import problem description from FOLDER (only the first *.tsk and *.cfg files found are taken, \
		all potential others are ignored).",
		metavar='FOLDER'
	)
	group.add_argument(
		"--collection",
		type=Path,
		help="Recursively import problem descriptions from FOLDER and/or subfolders\
		(only the first *.tsk and *.cfg files found of each folder are taken, all potential others are ignored).",
		metavar='FOLDER'
	)


def _create_cli_parser() -> ArgumentParser:
	"""Creates a CLI argument parser and returns it.

	Returns
	-------
	parser : ArgumentParser
		An `ArgumentParser` object holding the program's CLI.
	"""

	parser = ArgumentParser(
		prog="SOLVER",
		description="Solve task scheduling problems using graph coloration.",
		allow_abbrev=True,
	)
	parser.add_argument(
		"--verbose", action="store_const", const=True, help="Toggle program verbosity."
	)
	parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
	_create_parser_arg_group(parser)

	return parser


# ENTRY POINT #########################################################################################################


def main() -> int:
	"""Script entry point.

	Returns
	-------
	int
		Returns `0` if no error has been encountered, and an other value otherwise.
	"""

	args = _create_cli_parser().parse_args()
	logging.getLogger().addHandler(
		colored_handler(verbose=False if args.verbose is None else True)
	)

	problems = problem_builder(args.case, False) if args.case is not None else problem_builder(args.collection, True)
	solutions = scheduler(problems)

	logging.info("Total working time: " + str(timed.global_time) + "s.")
	logging.info("Total ellasped time: " + str(process_time()) + "s.")

	return 0


if __name__ == "__main__":
	main()
