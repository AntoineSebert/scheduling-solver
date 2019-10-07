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

We will use *pip* as **package installer**.

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

### Libraries

#### NetworkX

The project relies on the package *NetworkX*.

Its documentation can be found at https://networkx.github.io/documentation/stable/tutorial.html.

You can install it with:
```bash
pip install networkx
```
or update an existing installation with:
```bash
pip install --upgrade networkx
```

## Get started

### Create Workflow

Create the project by running the following:
```bash
pipenv --python 3.7
```

Install all the dependencies by running the following:
```bash
pipenv install --dev
```

## Launch

Run the project with
```bash
python src/main.py
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

- [ ] 24/09/2019 - 01/10/2019 | @all | Investigate possible solutions
- [ ] logging : https://docs.python.org/3/library/logging.html or https://github.com/Delgan/loguru + verbose output
- [ ] time benchmark
- [ ] progressbar
- [ ] benchmark strats
- [ ] random problem generation : https://networkx.github.io/documentation/stable/reference/randomness.html
- [ ] support multiple graph file formats
- [ ] parallelize : https://docs.python.org/3/library/asyncio-task.html
- [ ] catch all exceptions : https://docs.python.org/3/library/contextlib.html
- [ ] select analysis tools