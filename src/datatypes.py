#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


from typing import List
from weakref import ref
from collections import namedtuple
from dataclasses import dataclass, field


# CLASSES #############################################################################################################


@dataclass(order=True)
class PrioritizedItem:
	priority: float
	item: ref = field(compare=False)


# TYPE ALIASES ########################################################################################################


Architecture = List[List[int]]

Slice = namedtuple('Slice', ['task', 'start', 'end'])
Problem = namedtuple("Problem", ["name", "graphs", "arch"])
Solution = List[List[List[Slice]]]
