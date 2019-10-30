# 02229 - Systems Optimization: Group Project

## Authors

Milán **Balázs**

Nicolai **Herrmann**

Jessika **Pecl**

Antoine **Sébert**

## Prerequisites

### Python

Get the interpreter on the [official website](https://www.python.org/downloads/).

We will be working with the version **3.6.x**.

You can check the interpreter's version with:

```bash
$ python --version
```

### Package Installer

We will use *pip* as package installer.

You can install it or upgrade your current installation by following [this guide](https://pip.pypa.io/en/stable/installing/).

Then, check if the package installer has been installed for *Python 3.6* with:

```bash
$ pip --version
```

The packages index can be accessed [here](https://pypi.org/).

### Development Workflow

To simplify the environment's management, we will use *pipenv*.

You can install it with:

```bash
$ pip install pipenv
```

## Get started

### Get the sources

Clone the branch with:

### Create workflow

Create the project by running the following:

```bash
$ pipenv --python 3.6
```

Install all the dependencies by running the following:

```bash
$ pipenv update
```

## Launch

Change your working directory to the project's directory and run it with:

```bash
$ cd ".../02229---systems-optimization"
$ python src/main.py
```

### Usage

You can show the CLI usage with:

```bash
$ python src/main.py --help
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
$ python src/main.py --case "data/Case 1"
```

Solve all the test cases [data/100pct](data/100pct) with:

```bash
$ python src/main.py --collection "data/100pct"
```

### Tests suite and style checks

Run the tests with:

```bash
$ python -m unittest
```

*Note: this feature is not supported yet. See the [roadmap](#Roadmap) section.*

Perform a style check on the whole source with:

```bash
$ flake8
```

### Other

Dependency Graph:
```bash
$ pipenv graph
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
  +--Pipfile				// pipenv configuration
  +--README.md				// this file
  +--setup.py				// python package definition
```

## Roadmap

### This month - 22/11/2019

- [ ] catch all exceptions : https://docs.python.org/3/library/contextlib.html
- [ ] write tests : https://docs.python.org/3/library/unittest.html
- [ ] preemption
- [ ] benchmark : https://github.com/python/pyperformance
- [ ] optimize : https://docs.python.org/3/library/collections.html, https://docs.python.org/3/library/stdtypes.html, https://stackoverflow.com/questions/45123238/python-class-vs-tuple-huge-memory-overhead/45123561
- [ ] setup.py : https://setuptools.readthedocs.io/en/latest/pkg_resources.html
- [ ] cython : http://docs.cython.org/en/latest/src/quickstart/build.html, http://docs.cython.org/en/latest/

### This week - 05/11/2019

- [ ] pqueue of nodes instead of chains
- [ ] support Period, Deadline, Offset, MaxJitter
- [ ] OR-tools
- [ ] add references support to avoid data copy
- [ ] repair pipeline
- [ ] generate visual representation

### 31/10/2019

- [ ] workload update (static attrs in core and cpu, invalidated on modification)
- [ ] replace named tuples by mutable equivalent : https://bitbucket.org/intellimath/recordclass/src/default/
- [ ] investigate bug while processing [](data/300pct)
- [ ] replace `float` by `Fraction`
- [ ] change `Problem.name` to `Problem.filepair`
