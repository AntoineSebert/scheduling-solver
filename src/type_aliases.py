#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Tuple
from collections import namedtuple
from networkx import DiGraph

Architecture = List[List[int]]

Slice = namedtuple('Slice', ['id', 'start', 'end'])

Problem = Tuple[List[DiGraph], Architecture]
Solution = List[List[List[Slice]]]