# -*- coding: utf-8 -*-

from collections import namedtuple
from typing import *

File_pair = namedtuple('File_pair', ['tsk', 'cfg'])
Node = namedtuple("Node", ["id", "name", "wcet", "period", "deadline"])
Edge = namedtuple("Edge", ["source", "dest", "cost"])
Architecture = List[int]