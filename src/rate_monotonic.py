#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from fractions import Fraction
from typing import Iterable, Callable
from itertools import accumulate

from networkx import nodes

# FUNCTIONS ###########################################################################################################

"""Determine the utilization load carried by an iterable of nodes.

Parameters
----------
processes : Iterable[nodes]
	An iterable of nodes. The nodes must have "wcet" and "period" attributes.

Returns
-------
float
	The processor utilization, computed from the periods and WCETs of all processes.
"""
utilization: Callable[[Iterable[nodes]], float] = lambda processes:\
	accumulate(processes, lambda x: Fraction(x["wcet"], x["period"]), 0)

"""Determine the sufficient condition for schedulability of a processor or core.

Parameters
----------
processes : int
	A number of processes.

Returns
-------
float
	The sufficient utilization rate for a count of processes to be schedulable.
"""
sufficient_condition: Callable[[int], float] = lambda count: count * (pow(2, 1 / count) - 1)

"""Determines whether an iterable of nodes is schedulable or not.

Parameters
----------
processes : Iterable[nodes]
	An iterable of periodic tasks.

Returns
-------
bool
	Returns 'True' if the `processes` are schedulable, and 'False' otherise.
"""
is_schedulable: Callable[[Iterable[nodes]], bool] = lambda processes:\
	utilization(processes) <= sufficient_condition(len(processes))
