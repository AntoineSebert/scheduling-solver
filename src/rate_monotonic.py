#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from fractions import Fraction
from typing import Iterable, Callable

from networkx import nodes

# FUNCTIONS ###########################################################################################################

"""Determine the utilization ratio for a process.

Parameters
----------
node : nodes
	A node, that must have "wcet" and "period" attributes.

Returns
-------
float
	The processor utilizationfor the process.
"""
process_ratio: Callable[[nodes], Fraction] = lambda node: Fraction(node[1]["wcet"], node[1]["period"])


def utilization(processes: Iterable[nodes]) -> float:
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

	return sum([process_ratio(node) for node in processes]) if processes is not None else 0.0


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
