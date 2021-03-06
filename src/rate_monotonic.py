#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


from fractions import Fraction
from typing import Callable, Iterable

from datatypes import Node


# FUNCTIONS ###########################################################################################################


"""Determine the workload ratio for a node.

Parameters
----------
node : Node
	A node representing a task.

Returns
-------
Fraction
	The processor workload for the task.
"""
process_ratio: Callable[[Node], Fraction] = lambda node: Fraction(node.wcet, node.period)


"""Determine the workload load carried by an iterable of nodes.

Parameters
----------
processes : Iterable[Node]
	An iterable of nodes representing tasks.

Returns
-------
Fraction
	The processor workload, computed from the periods and WCETs of all tasks.
"""
workload: Callable[[Iterable[Node]], Fraction] = lambda tasks:\
	sum(process_ratio(node) for node in tasks) if tasks is not None else 0.0


"""Determine the sufficient condition for schedulability of a count of tasks.

Parameters
----------
count : int
	A number of processes.

Returns
-------
Fraction
	The sufficient workload rate for a count of tasks to be schedulable.
"""
sufficient_condition: Callable[[int], Fraction] = lambda count: count * (Fraction(2)**Fraction(1, count) - 1)


"""Determines whether an iterable of nodes is schedulable or not.

Parameters
----------
tasks : Iterable[Node]
	An iterable of nodes representing periodic tasks.

Returns
-------
bool
	Returns 'True' if the tasks are schedulable, and 'False' otherise.
"""
is_schedulable: Callable[[Iterable[Node]], bool] = lambda tasks: workload(tasks) <= sufficient_condition(len(tasks))
