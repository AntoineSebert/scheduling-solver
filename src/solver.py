#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from typing import NoReturn, Iterable, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue, Empty
from weakref import ref
from itertools import groupby

from networkx import DiGraph, nodes

import logging
from timed import timed_callable
from datatypes import Problem, Solution, Slice, PrioritizedItem
from rate_monotonic import utilization


# FUNCTIONS ###########################################################################################################


def _chain_stress(graph: DiGraph) -> float:
	"""Computes the stress ratio for a graph.
	The lower that number is, the more the chain is stressed
	(in PriorityQueue, lowest valued entries are retrieved first.

	Parameters
	----------
	graph : DiGraph
		An oriented task graph.

	Returns
	-------
	float
		The stress level for the graph.

	Raises
	------
	NetworkXNotImplemented
		If the chain budget is shorter than the scheduled tasks duration.
	"""

	assigned_tasks_duration = sum([node[1].get("wcet") for node in graph.nodes(data=True) if node[1].get("coreid") != -1])

	if graph.graph.get("budget") < assigned_tasks_duration:
		raise NotImplementedError("The Chain duration is shorter than the total tasks duration")

	unassigned_tasks_duration = sum(
		[node[1].get("wcet") for node in graph.nodes(data=True) if node[1].get("coreid") == -1]
	)
	stress = (graph.graph.get("budget") - assigned_tasks_duration)

	return stress / unassigned_tasks_duration if 0 < unassigned_tasks_duration else stress


def _get_processes_for_core(graphs: Iterable[DiGraph], core: Tuple[int, int]) -> Optional[List[nodes]]:
	"""Returns the list of processes scheduled on a core.

	Parameters
	----------
	graphs : Iterable[DiGraph]
		A list of graphs in which perform the search.
	core : Tuple[int, int]
		A core to look for in the processes' attributes. The tuple member is the cpu, the second the core itself.

	Returns
	-------
	Optional[List[nodes]]
		A list of processes if there are any, or `None` otherwise.
	"""

	with ThreadPoolExecutor(max_workers=len(graphs)) as executor:
		futures = [executor.submit(
			lambda graph, core: [
				node for node in graph.nodes(data=True) if node[1].get("cpuid") == core[0] and node[1].get("coreid") == core[1]
			],
			graph, core
		) for graph in graphs]

	processes = [node for future in futures if future.result() for node in future.result()]

	return processes if processes else None


def _get_cpu_utilization_tuple(graphs: Iterable[DiGraph], cpu: List[int], cpu_index: int)\
	-> Tuple[float, PriorityQueue]:
	"""Get the global utilization carried by the processes scheduled on a cpu, and by core.

	Parameters
	----------
	graphs : Iterable[DiGraph]
		A list of graphs in which perform the search.
	cpu : List[int]
		A CPU from the architecture.
	cpu_index : int
		A CPU index within the architecture.

	Returns
	-------
	Tuple[float, PriorityQueue]
		A tuple containing the CPU utilization, and a priority queue of tuples,
		containin the utilization by core and the core id.
	"""

	ratio_pqueue = PriorityQueue(maxsize=len(cpu))
	u_sum = 0.0

	for coreid, core_utilization in enumerate([
		utilization(_get_processes_for_core(graphs, (cpu_index, coreid))) for coreid, core in enumerate(cpu)
	]):
		u_sum += core_utilization
		ratio_pqueue.put((core_utilization, coreid))

	return (u_sum, ratio_pqueue)


def _create_chain_pqueue(graphs: Iterable[DiGraph]) -> PriorityQueue:
	"""Creates a priority queue for all chains in the problem, depending on the chain stress.

	Parameters
	----------
	graphs : Iterable[DiGraph]
		A list of chains of processes.

	Returns
	-------
	chain_pqueue : PriorityQueue
		A priority queue containing tuples of chain stress and reference to the chain.
	"""

	chain_pqueue = PriorityQueue(maxsize=len(graphs))
	with ThreadPoolExecutor(max_workers=len(graphs)) as executor:
		futures = [executor.submit(_chain_stress, graph) for graph in graphs]
		for i, future in enumerate(futures):
			chain_pqueue.put(PrioritizedItem(future.result(), ref(graphs[i])))

	return chain_pqueue


def _create_utilization_table(problem: Problem) -> List[Tuple[float, PriorityQueue]]:
	"""Create an utilization table from a problem statement.

	Parameters
	----------
	problem : Problem
		A problem statement.

	Returns
	-------
	utilization_table : List[Tuple[float, PriorityQueue]]
		A list of tuples, each tuple representing a CPU, containing a pair of float, being the CPU utilization,
		and a priority queue of floats, being the utilization
	"""

	utilization_table = list()
	with ThreadPoolExecutor(max_workers=len(problem.arch)) as executor:
		futures = [executor.submit(_get_cpu_utilization_tuple, problem.graphs, cpu, i) for i, cpu in enumerate(problem.arch)]
		utilization_table = [future.result() for future in futures]

	return utilization_table


@timed_callable("Generating a coloration for the problem...")
def _color_graphs(problem: Problem) -> NoReturn:
	"""Color the graphs within the problem.

	Parameters
	----------
	problem : Problem
		The problem to work on.

	Returns
	-------
	List[Tuple[int, Tuple[int, int]]]
		A list of tuples, each tuple representing a task id whithin its chain, and a tuple of cpu id and core id.
	"""

	chain_pq = _create_chain_pqueue(problem.graphs)
	utilization_table = _create_utilization_table(problem)

	# while chain_pq not empty
	try:
		# get first item of chain_pq
		while (chain := chain_pq.get_nowait()):
			# get first item of process list without core
			for node in filter(lambda node: node[1].get("coreid") == -1, chain.item().nodes(data=True)):
				# get first core from utilization_table with the same processor
				try:
					# add process to it
					core = utilization_table[node[1].get("cpuid")][1].get_nowait()
					node[1].update({"coreid": core[1]})
					utilization_table[node[1].get("cpuid")][1].put_nowait(core)
					# reschedule cpu
					utilization_table[node[1].get("cpuid")] = _get_cpu_utilization_tuple(
						problem.graphs,
						[node[1] for node in utilization_table[node[1].get("cpuid")][1].queue], node[1].get("cpuid")
					)
				except Empty:
					pass
			# if chain_pq not entirely scheduled, put it back in chain_pq
			if [node for node in chain.item().nodes(data=True) if node[1].get("coreid") == -1]:
				chain_pq.put_nowait(chain)
	except Empty:
		pass

	return [(node[0], (
		node[1].get("cpuid"),
		node[1].get("coreid")
	)) for chain in problem.graphs for node in chain.nodes(data=True)]


def _theoretical_scheduling_time(graph: DiGraph) -> int:
	"""Computes the theoretical scheduling time of a graph.

	Parameters
	----------
	graph : DiGraph
		An oriented task graph.

	Returns
	-------
	int
		The theoretical shortest scheduling time for `graph`.
	"""

	return sum([node[1].get("wcet") for node in graph.nodes(data=True)])


@timed_callable("Computing shortest theoretical scheduling time...")
def _shortest_theoretical_scheduling(graphs: Iterable[DiGraph]) -> int:
	"""Computes the shortest theoretical scheduling time from the longest scheduling path of all graphs.

	Parameters
	----------
	graphs: Iterable[DiGraph]
		An iterable of directed oriented graph imported from the `Problem`.

	Returns
	-------
	int
		The theoretical shortest scheduling time.
	"""

	with ThreadPoolExecutor(max_workers=len(graphs)) as executor:
		futures = [executor.submit(_theoretical_scheduling_time, graph) for graph in graphs]

	return min([future.result() for future in futures])


def _schedule_graph(graph: DiGraph, solution: Solution) -> NoReturn:
	"""Schedules a graph into a solution.

	Parameters
	----------
	graph : DiGraph
		A `DiGraph` to schedule.
	solution: Solution
		A `Problem` from the problem builder.
	"""

	# for each process in chain
	for node in graph.nodes(data=True):
		# assign time slice for each process & add it to corresponding core, at the end of the list
		task_list = solution[node[1].get("cpuid")][node[1].get("coreid")]
		start = 0 if not task_list else task_list[-1].end
		task_list.append(
			Slice(task=graph.graph.get("name") + '-' + str(node[0]), start=start, end=start + node[1].get("wcet"))
		)


@timed_callable("Generating a solution from the coloration...")
def _generate_solution(problem: Problem) -> Solution:
	"""Creates and returns a solution from the relaxed problem.

	Parameters
	----------
	problem : Problem
		A `Problem` from the problem builder.

	Returns
	-------
	Solution
		A solution for the problem.
	"""

	solution = [[list() for item in core] for core in [cpu for cpu in problem.arch]]

	# group graphs by desc priority level
	for keyvalue, group in groupby(problem.graphs, key=lambda graph: graph.graph.get("priority")):
		# for each level
		for i in reversed(sorted(list(group), key=lambda graph: len(graph))):
			_schedule_graph(i, solution)

	return solution


def _hyperperiod_duration(solution: Solution) -> int:
	"""Computes the hyperperiod length for a solution.

	Parameters
	----------
	solution : Solution
		A non-empty solution.

	Returns
	-------
	int
		The hyperperiod length for the solution.
	"""

	return max([core[-1].end for cpu in solution for core in cpu if core])


def _solve_single_problem(problem: Problem) -> Solution:
	"""Creates the solution for a problem.

	Parameters
	----------
	problem: Problem
		A `Problem` from the problem builder.

	Returns
	-------
	solution : Solution
		A solution for the problem.
	"""

	logging.info("Solving " + problem.name)
	logging.info("Theoretical shortest scheduling time:\t" + str(_shortest_theoretical_scheduling(problem.graphs)) + "ms.")

	coloration = _color_graphs(problem)
	logging.info("Coloration found:\n\t" + '\n\t'.join(str(node) for node in coloration))

	solution = _generate_solution(problem)

	logging.info("Solution found:\n\t" + '\n\t'.join([str(scheduling) for scheduling in solution]))
	logging.info("Hyperperiod duration:\t" + str(_hyperperiod_duration(solution)))

	return solution


# ENTRY POINT #########################################################################################################


def scheduler(problems: Iterable[Problem]) -> List[Solution]:
	"""Generates a solution for the problem.

	Parameters
	----------
	problem : Problem
		A `Problem` from the problem builder.

	Returns
	-------
	Optional[Solution]
		A solution if there is one, or `None` otherwise.
	"""

	futures = list()

	with ThreadPoolExecutor(max_workers=len(problems)) as executor:
		futures = [executor.submit(_solve_single_problem, problem) for problem in problems]

	return [future.result() for future in futures]
