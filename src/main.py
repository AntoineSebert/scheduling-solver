#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Resources
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

from log import colored_handler
from solver import scheduler
from builder import problem_builder
from formatter import OutputFormat


# FUNCTIONS ###########################################################################################################


def _add_dataset_arggroup(parser: ArgumentParser) -> NoReturn:
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
		help="Import problem description from FOLDER\
		(only the first *.tsk and *.cfg files found are taken, all potential others are ignored).",
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
		'-f', '--format',
		nargs=1,
		default='xml',
		choices=[member.name for member in OutputFormat],
		help="Either one of " + ', '.join([member.name for member in OutputFormat]),
		metavar="FORMAT",
		dest="format"
	)
	parser.add_argument(
		"--verbose",
		action="store_true",
		help="Toggle program verbosity.",
		default=False
	)
	parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

	_add_dataset_arggroup(parser)

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
		colored_handler(verbose=args.verbose)
	)

	problems = problem_builder(args.case, False) if args.case is not None else problem_builder(args.collection, True)
	solutions = scheduler(problems)

	logging.info("Total ellasped time: " + str(process_time()) + "s.")

	formatted = OutputFormat[args.format[0]](solutions)

	for solution in formatted:
		logging.info("Formatted solutions: \n" + solution)

	return formatted # yield output ?


if __name__ == "__main__":
	main()
