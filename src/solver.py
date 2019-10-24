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
from rate_monotonic import workload


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
		A core to look for in the processes' attributes. The tuple member is the cpu id, the second the core itself.

	Returns
	-------
	Optional[List[nodes]]
		A list of processes if there are any, or `None` otherwise.
	"""

	with ThreadPoolExecutor(max_workers=len(graphs)) as executor:
		futures = [executor.submit(
			lambda g, c: filter(lambda n: n[1].get("cpuid") == c[0] and n[1].get("coreid") == c[1], g.nodes(data=True)),
			graph, core
		) for graph in graphs]

	processes = [node for future in futures if future.result() for node in future.result()]

	return processes if processes else None


def _get_cpuload(graphs: Iterable[DiGraph], cpu: Tuple[int, List[int]]) -> Tuple[float, PriorityQueue]:
	"""Get the global workload carried by the processes scheduled on a cpu, and by core.

	Parameters
	----------
	graphs : Iterable[DiGraph]
		A list of graphs in which perform the search.
	cpu : Tuple[int, List[int]]
		A CPU tuple from the architecture.

	Returns
	-------
	Tuple[float, PriorityQueue]
		A tuple containing the CPU workload, and a priority queue of tuples,
		containing the workload by core and the core id.
	"""

	ratios = PriorityQueue(maxsize=len(cpu[1]))
	u_sum = 0.0

	for coreid, coreload in [
		(coreid, workload(_get_processes_for_core(graphs, (cpu[0], coreid)))) for coreid, core in enumerate(cpu[1])
	]:
		u_sum += coreload
		ratios.put((coreload, coreid))

	return (u_sum, ratios)


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
		futures = {ref(graph): executor.submit(_chain_stress, graph) for graph in graphs}

	for graph, future in futures.items():
		chain_pqueue.put(PrioritizedItem(future.result(), graph))

	return chain_pqueue


def _create_proc_workload(problem: Problem) -> List[Tuple[float, PriorityQueue]]:
	"""Create a worload list from a problem statement.

	Parameters
	----------
	problem : Problem
		A problem statement.

	Returns
	-------
	List[Tuple[float, PriorityQueue]]
		A list of tuples, each tuple representing a CPU, containing a pair of float, being the CPU workload,
		and a priority queue of floats, being the workload
	"""

	with ThreadPoolExecutor(max_workers=len(problem.arch)) as executor:
		futures = [
			executor.submit(_get_cpuload, problem.graphs, (cpuid, corelist)) for cpuid, corelist in problem.arch.items()
		]

	return [future.result() for future in futures]


@timed_callable("Generating a coloration for the problem...")
def _color_graphs(problem: Problem) -> List[Tuple[int, Tuple[int, int]]]:
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
	proc_workload = _create_proc_workload(problem)

	# while chain_pq not empty
	while not chain_pq.empty():
		# get first item of chain_pq
		chain = chain_pq.get_nowait()
		# get first item of process list without core
		for node in filter(lambda node: node[1].get("coreid") == -1, chain.item().nodes(data=True)):
			# get first core from proc_workload with the same processor
			try:
				# add process to it
				core = proc_workload[node[1].get("cpuid")][1].get_nowait()
				node[1].update({"coreid": core[1]})
				proc_workload[node[1].get("cpuid")][1].put_nowait(core)
				# reschedule cpu
				proc_workload[node[1].get("cpuid")] = _get_cpuload(
					problem.graphs,
					(node[1].get("cpuid"), [node[1] for node in proc_workload[node[1].get("cpuid")][1].queue])
				)
			except Empty:
				pass

		# if at least one node not scheduled, put chain back in chain_pq
		for node in chain.item().nodes(data=True):
			if node[1].get("coreid") == -1:
				chain_pq.put_nowait(PrioritizedItem(_chain_stress(chain), chain))
				break

	return [
		((chain.graph.get("name"), node[0]), (node[1].get("cpuid"), node[1].get("coreid")))
		for chain in problem.graphs for node in chain.nodes(data=True)
	]


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
		task_list = solution.get(node[1].get("cpuid"))[node[1].get("coreid")]
		start = 0 if not task_list else task_list[-1].end
		task_list.append(Slice(task=(graph.graph.get("name"), node[0]), start=start, end=start + node[1].get("wcet")))


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

	solution = {cpu: [list() for core in corelist] for cpu, corelist in problem.arch.items()}

	# group graphs by desc priority level
	for keyvalue, group in groupby(problem.graphs, lambda graph: graph.graph.get("priority")):
		# for each level
		for graph in reversed(sorted(list(group), key=lambda graph: len(graph))):
			_schedule_graph(graph, solution)

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

	return max([task_list[-1].end for _, corelist in solution.items() for task_list in corelist if task_list])


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

	logging.info(
		"Solution found:\n\t" + '\n\t'.join(
			[str(key) + '\n\t\t' + '\n\t\t'.join([str(val) for val in values]) for key, values in solution.items()]
		)
	)
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
	List[Solution]
		A list of solutions.
	"""

	with ThreadPoolExecutor(max_workers=len(problems)) as executor:
		futures = [executor.submit(_solve_single_problem, problem) for problem in problems]

	return [future.result() for future in futures]
