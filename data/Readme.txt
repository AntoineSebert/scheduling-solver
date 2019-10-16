
.cfg: Architecture
The architecture has at least one CPU and at least one Core for each CPU.

Cpu           : the CPU element, attributed with an "Id" tag which is a unique integer. It has children tagged with "Core"
Core          : the Core element, attributed with an "Id" tag which is a unique integer within the parent element. It is also attributed with "MacroTick" tag.
MacroTick     : the attribute tag for a Core; integer; indicates time in microseconds; shows the time granularity of the core scheduling.
				Preempltion is possible through the MacroTick. Preemption is not allowed by assigning big 9999999 to microtick.



.tsk: Applications
The application has tasks and chains. A task is tagged with "Node":
Id                  : Integer; Unique
Name                : A unique name for the task
WCET                : Worst Case Execution Time of the task; in microseconds
Period              : Period of a task in microseconds
Deadline            : Deadline of a task in microseconds
Offset				: The earliest activation time of task within its period in microseconds.
MaxJitter           : Maximum Jitter in microseconds that the task can have. -1 for no jitter limitations.
CpuId               : Id of the assigned CPU. Must be assigned.
CoreId              : Id of the assigned Core of the CPU; optional; -1 for no core assignment.


A chain shows task flow; modedeled with DAG; tagged with "Chain":
Budget              : End to End Response of the chain in microseconds.
Priority            : [0,1]; shows the Priority of the chain. 1 is the highest Priority and 0 is the lowest.
Name                : A unique name for the chain.

A chain has at least one task which is tagged with "Runnable" and attributed with the Name of the task.
