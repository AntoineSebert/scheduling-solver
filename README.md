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

You can install it or upgrade your current installation by following [this guide](https://pip.pypa.io/en/stable/installing/).

You can check the package installer's version with:
```bash
pip --version
```

The packages index can be accessed [here](https://pypi.org/).

### Development Workflow

To simplify the environment's management, we will use *pipenv*.

You can install it with:
```bash
pip install pipenv
```

### Lint & Checks

We encourage the inclusion of linters and formatters as a good practice.

You can install it with:
```bash
pip install pylint
```

## Get started

### Create Workflow

Create the project by running the following:
```bash
pipenv --python 3.6
```

Install all the dependencies by running the following:
```bash
pipenv install --dev
```

## Launch

Run the project with
```bash
python src/main.py data_folder/
```

### Usage

```
Usage:
	main.py --version
	main.py (-h | --help)
	main.py folder <DATASET_FOLDER>
	main.py folder <DATASET_FOLDER> --verbose

Arguments:
	folder <DATASET_FOLDER>   The dataset folder that must contain one *.tsk file and one *.cfg file.

Options:
	-h --help	Show this screen.
	--version	Show version.
	--verbose	Toggle verbose output.
```

### Tests suit and other checks

Security Checks:
```bash
pipenv check
```

Formatting and Syntax Errors:
```bash
pylint src/main.py
```

### Other

Dependency Graph:
```bash
pipenv graph
```

## Simplified operation

```mermaid
graph LR
Start(Start) -->|raw| Builder
Builder -->|IR| Solver
Solver -->|Solution| End(End)
```

## File Hierarchy

```
+ root/
  + data/
  | + case1.cfg
  | + case1.tsk
  + src/
  | + main.py
  + .gitattributes
  + .gitlab-ci.yml
  + .gitignore
  + Pipfile
  + Pipfile.lock
  + README.md
```

## Roadmap

### This month - 22/11/2019

- [ ] catch all exceptions : https://docs.python.org/3/library/contextlib.html
- [ ] write tests
- [ ] preemption
- [ ] optimize : https://docs.python.org/3/library/collections.html, https://docs.python.org/3/library/stdtypes.html
- [ ] setup.py : https://setuptools.readthedocs.io/en/latest/pkg_resources.html
- [ ] cython : http://docs.cython.org/en/latest/src/quickstart/build.html, http://docs.cython.org/en/latest/

### This week - 05/11/2019

- [ ] pqueue of nodes instead of chains
- [ ] support Period, Deadline, Offset, MaxJitter
- [ ] drop networkx

### 29/10/2019

- [ ] generate visual representation
- [ ] OR-tools
