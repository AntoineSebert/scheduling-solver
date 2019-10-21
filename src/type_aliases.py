#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from typing import List, Tuple
from collections import namedtuple
from networkx import DiGraph

# TYPE ALIASES ########################################################################################################

Architecture = List[List[int]]

Slice = namedtuple('Slice', ['task', 'start', 'end']) # pid = ref(node)
Problem = namedtuple("Problem", ["graphs", "arch"]) # NamedTuple[Iterable[DiGraph], Architecture]
Solution = List[List[List[Slice]]]
