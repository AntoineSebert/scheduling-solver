# 02229 - Systems Optimization: Group Project

## Authors

Milán **Balázs**

Nicolai **Herrmann**

Jessika **Pecl**

Antoine **Sébert**

## Prerequisites

### Python

Get the interpreter on the [official website](https://www.python.org/downloads/).

We will be working with the version **3.7.x**.

You can check the interpreter's version with:

```bash
$ python --version
```

### Package Installer

We will use *pip* as package installer.

You can install it by following [this guide](https://pip.pypa.io/en/stable/installing/).

Then, check if the package installer has been installed for *Python 3.7* with:

```bash
$ pip --version
```

The packages index can be accessed [here](https://pypi.org/).

### Python Dependency Manager

To manage the deps, we will use *poetry*.

You can install it by following [this guide](https://poetry.eustace.io/docs/#installation).

Then, check if the package installer has been installed with:

```bash
$ poetry --version
```

## Get started

### Get the sources

Clone the branch with:

```bash
$ git clone --single-branch --branch constraint-programming https://gitlab.com/Zeltex/02229---systems-optimization
```

### Create workflow

Go to the repository that has just been cloned and install the dependencies by running the following:

```bash
$ poetry install
```

You can update the dependencies by running the following:

```bash
$ poetry update
```

## Launch

Change your working directory to the project's directory and run it with:

```bash
$ poetry run python src/main.py
```

### Usage

You can show the CLI usage with:

```bash
$ poetry run python src/main.py --help
usage: SOLVER [-h] [-f FORMAT] [--verbose] [--version]
              (--case FOLDER | --collection FOLDER)

Solve task scheduling problems using graph coloration.

optional arguments:
  -h, --help            show this help message and exit
  -f FORMAT, --format FORMAT
                        Either one of xml, json, raw, svg
  --verbose             Toggle program verbosity.
  --version             show program's version number and exit
  --case FOLDER         Import problem description from FOLDER (only the first
                        *.tsk and *.cfg files found are taken, all potential
                        others are ignored).
  --collection FOLDER   Recursively import problem descriptions from FOLDER
                        and/or subfolders (only the first *.tsk and *.cfg
                        files found of each folder are taken, all potential
                        others are ignored).
```

### Example

Solve the test case [data/Case 1](data/Case 1) with:

```bash
$ poetry run python src/main.py --case "data/Case 1"
```

Solve all the test cases [data/100pct](data/100pct) with:

```bash
$ poetry run python src/main.py --collection "data/100pct"
```

Redirects the console output including the solution to a file:

```bash
$ poetry run python src/main.py --case "data/Case 1" 2> file.txt
```
*Note: If the file does not exist, it will be created.*

### Tests suite and style checks

Run the tests with:

```bash
$ poetry run python -m unittest
```

*Note: this feature is not supported yet. See the [roadmap](#Roadmap) section.*

Perform a style check on the whole source with:

```bash
$ poetry run flake8
```

## Simplified operation

```mermaid
graph LR
Start(Start) -->|XML| Builder
Builder -->|IR| Solver
Solver -->|Solution| Formatter
Formatter -->|Fmt Solution| End(End)
```

## File Hierarchy

```
--root/
  +--build/					// future support for Cython builds
  +--data/					// test cases
  |  +--100pct/					// complex test case
  |  +--200pct/					// complex test case
  |  +--300pct/					// complex test case
  |  +--400pct/					// complex test case
  |  +--500pct/					// complex test case
  |  +--Case 1/					// simple test case
  |  +--Case 2/					// simple test case
  |  +--Case 3/					// simple test case
  |  +--Case 4/					// simple test case
  |  +--Case 5/					// simple test case
  |  +--Case 6/					// simple test case
  |  +--readme.txt				// test case data model definition
  +--src/					// sources
  |  +--builder.py				// problem builder
  |  +--datatypes.py			// structured data
  |  +--draw.py					// problem & solution painter
  |  +--formatter.py			// solution formatter
  |  +--log.py					// logging handler
  |  +--main.py					// entry point
  |  +--rate_monotonic.py		// rate monotonic -related utilities
  |  +--solver.py				// problem solver / solution generator
  |  +--timed.py				// timed function wrapper
  +--tests/					// tests
  |  +--main.py					// tests for src/main.py
  +--.flake8				// project-specific styles
  +--.gitattributes			// project attributes
  +--.gitignore				// unstaged files and folders
  +--.gitlab-ci.yml			// Gitlab pipeline configuration
  +--pyproject.toml			// poetry configuration
  +--README.md				// this file
  +--setup.py				// python package definition
```

## Roadmap

### This month - 22/11/2019

- [ ] catch all exceptions : https://docs.python.org/3/library/contextlib.html
- [ ] preemption
- [ ] benchmark : https://github.com/python/pyperformance
- [ ] optimize : https://docs.python.org/3/library/collections.html, https://docs.python.org/3/library/stdtypes.html, https://stackoverflow.com/questions/45123238/python-class-vs-tuple-huge-memory-overhead/45123561
- [ ] setup.py : https://setuptools.readthedocs.io/en/latest/pkg_resources.html, https://setuptools.readthedocs.io/en/latest/setuptools.html
- [ ] cython : http://docs.cython.org/en/latest/src/quickstart/build.html, http://docs.cython.org/en/latest/
- [ ] write tests : https://docs.python.org/3/library/unittest.html
- [ ] random problem generator

### This week - 12/11/2019

- [ ] add references support to avoid data copy
- [ ] workload update (static attrs in core and cpu, invalidated on modification)
- [ ] repair pipeline
- [ ] generate visual representation (SVG formatter)

### 04/11/2019

- [ ] replace named tuples by mutable equivalent : https://bitbucket.org/intellimath/recordclass/src/default/
- [ ] OR-tools : get feasible solution, support Period, Deadline, Offset, MaxJitter
- [ ] linux cluster for benchmarks
