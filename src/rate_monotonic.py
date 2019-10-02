# -*- coding: utf-8 -*-

from fractions import Fraction
from typing import *
from type_alias import Node

def utilization(processes: List[Node]) -> float:
	"""Determine the utilization load carried by a list of tasks.

	Parameters
	----------
	processes : List[Node]
		A list of processes.

	Returns
	-------
	float
		The processor utilization, computed from the periods and WCETs of all processes.

	See Also
	--------
	sufficient_condition, is_schedulable
	"""

	return sum([Fraction(int(n.wcet), int(n.period)) for n in processes])

def sufficient_condition(count: int) -> float:
	"""Determine the sufficient condition for schedulability of a processor or core.

	Parameters
	----------
	processes : int
		A number of processes.

	Returns
	-------
	float
		The sufficient utilization rate for a count of processes to be schedulable.

	See Also
	--------
	utilization, is_schedulable
	"""

	return count * (pow(2, 1 / count) - 1)

def is_schedulable(processes: List[Node]) -> bool:
	"""Determines whether a list of processes is schedulable or not.

	Parameters
	----------
	processes : List[Node]
		A set of periodic tasks.

	Returns
	-------
	bool
		A boolean set to 'True' if the `processes` are schedulable, and 'False' otherise.

	See Also
	--------
	utilization, sufficient_condition
	"""

	return processor_use(processes) <= sufficient_condition(len(processes))