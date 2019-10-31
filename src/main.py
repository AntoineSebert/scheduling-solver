#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Resources
- https://numpydoc.readthedocs.io/en/latest/format.html

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
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm

from log import colored_handler
from solver import solve
from builder import build
from formatter import OutputFormat
from datatypes import Filepaths


# FUNCTIONS ###########################################################################################################


def _add_dataset_arggroup(parser: ArgumentParser) -> ArgumentParser:
	"""Adds a mutual exclusive group of arguments to the parser to handle dataset batch or single mode, then returns it.

	Parameters
	----------
	parser : ArgumentParser
		An `ArgumentParser`, to which will be added an argument group.

	Returns
	-------
	parser : ArgumentParser
		An `ArgumentParser` holding the program's CLI.
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

	return parser


def _create_cli_parser() -> ArgumentParser:
	"""Creates a CLI argument parser and returns it.

	Returns
	-------
	parser : ArgumentParser
		An `ArgumentParser` holding the program's CLI.
	"""

	parser = ArgumentParser(
		prog="SOLVER",
		description="Solve task scheduling problems using graph coloration.",
		allow_abbrev=True,
	)

	parser.add_argument(
		'-f', '--format',
		nargs=1,
		default=['raw'],
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

	return _add_dataset_arggroup(parser)


def _import_files_from_folder(folder_path: Path) -> Filepaths:
	"""Creates a filepath pair from a given folder.

	Parameters
	----------
	folder_path : Path
		A `Path` from which build the filepath pair of `*.tsk` and `*.cfg` files.
		Only the first encountered file of each type is taken, all the others are ignored.

	Returns
	-------
	Filepaths
		A `Filepaths` pointing to the `*.tsk` and `*.cfg` files.
	"""

	tsk = next(filter(Path.is_file, folder_path.glob('*.tsk')))
	cfg = next(filter(Path.is_file, folder_path.glob('*.cfg')))

	if tsk.stem != cfg.stem:
		logging.warning("The names of the files mismatch: '" + tsk.stem + "' and '" + cfg.stem + "'")

	return Filepaths(tsk, cfg)


def _get_filepath_pairs(folder_path: Path, recursive: bool = False) -> List[Filepaths]:
	"""Gathers the filepath pairs from a given folder.

	Parameters
	----------
	folder_path : Path
		A `Path` from which build the filepath pairs of`*.tsk` and `*.cfg` files.
	recursive : bool
		Toggles the recursive search for cases (default: False).
		All the folders and subfolders containing at least one `*.tsk` and `*.cfg` file will be taken.

	Returns
	-------
	filepath_pairs : List[Filepaths]
		A list of `Filepaths`.
	"""

	filepath_pairs = list()

	try:
		filepath_pairs = [_import_files_from_folder(folder_path)]
	except StopIteration:
		pass

	if recursive:
		for subfolder in filter(lambda e: e.is_dir(), folder_path.iterdir()):
			try:
				[filepath_pairs.append(filepath) for filepath in _get_filepath_pairs(subfolder, True) if filepath]
			except StopIteration:
				pass

	return filepath_pairs


def _solve(filepath_pair: Filepaths, format: OutputFormat, pbar: tqdm) -> str:
	"""Handles a test case from building to solving and formatting.

	Parameters
	----------
	filepath_pair : Filepaths
		A `Filepaths` pointing to the `*.tsk` and `*.cfg` files.
	format : OutputFormat
		A member of `OutputFormat` to use to format the `Solution` of the `Problem`.
	pbar : tqdm
		A progress bar to update each time an action of the test case in completed.

	Returns
	-------
	output : str
		A `Solution` formatted as a `str` in the given format.
	"""

	output = filepath_pair

	for function in [build, solve, OutputFormat[format]]:
		output = function(output)
		pbar.update()

	return output


# ENTRY POINT #########################################################################################################


def main() -> int:
	"""Script entry point.

	Returns
	-------
	int
		Returns `-1` if errors has been encountered, and a list of formatted `Solution` for the test cases otherwise.
	"""

	args = _create_cli_parser().parse_args()
	logging.getLogger().addHandler(colored_handler(verbose=args.verbose))

	filepath_pairs = _get_filepath_pairs(args.case, False) if args.case else _get_filepath_pairs(args.collection, True)

	if not filepath_pairs:
		raise FileNotFoundError("No matching files found. At least one *.tsk file and one *.cfg file are necessary.")

	for filepath_pair in filepath_pairs:
		logging.info("Files found:\n\t" + filepath_pair.tsk.name + "\n\t" + filepath_pair.cfg.name)

	with ThreadPoolExecutor(max_workers=len(filepath_pairs)) as executor, tqdm(total=len(filepath_pairs) * 3) as pbar:
		futures = [executor.submit(_solve, filepath_pair, args.format[0], pbar) for filepath_pair in filepath_pairs]
		results = [future.result() for future in as_completed(futures)]

		logging.info("Total ellasped time: " + str(process_time()) + "s.")

		return results

	return -1


if __name__ == "__main__":
	main()
