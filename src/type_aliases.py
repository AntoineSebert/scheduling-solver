#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List # https://docs.python.org/3/library/stdtypes.html#list
from collections import namedtuple # https://docs.python.org/3/library/collections.html#collections.namedtuple

Architecture = List[List[int]]

Slice = namedtuple('Slice', ['id', 'start', 'end'])

Solution = List[List[List[Slice]]]