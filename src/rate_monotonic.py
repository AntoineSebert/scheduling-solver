#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from fractions import Fraction
from typing import List, Callable

from networkx import nodes

# FUNCTIONS ###########################################################################################################

"""Determine the utilization load carried by a list of tasks.

Parameters
----------
processes : List[nodes]
	A list of processes.

Returns
-------
float
	The processor utilization, computed from the periods and WCETs of all processes.
"""
utilization: Callable[[List[nodes]], float] = lambda processes: sum(
	[Fraction(int(n["wcet"]), int(n["period"])) for n in processes]
)

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

"""Determines whether a list of processes is schedulable or not.

Parameters
----------
processes : List[nodes]
	A set of periodic tasks.

Returns
-------
bool
	A boolean set to 'True' if the `processes` are schedulable, and 'False' otherise.
"""
is_schedulable: Callable[[List[nodes]], bool] = lambda processes:\
	utilization(processes) <= sufficient_condition(len(processes))
