import xml.etree.ElementTree as ET
from pathlib import Path
from functools import total_ordering, reduce
import sys

# https://stackoverflow.com/questions/37237954/calculate-the-lcm-of-a-list-of-given-numbers-in-python
def lcm(denominators):
    return reduce(lambda x,y: (lambda a,b: next(i for i in range(max(a,b),a*b+1) if i%a==0 and i%b==0))(x,y), denominators)

class Task:
    def __init__(self, id, name, wcet, period, deadline, max_jitter, offset, cpu_id, core_id):
        self.id = id
        self.Name = name
        self.wcet = wcet
        self.period = period
        self.deadline = deadline
        self.max_jitter = max_jitter
        self.offset = offset
        self.cpu_id = cpu_id
        self.core_id = core_id

        self.is_preempted = False
        self.jobs = []

    @classmethod
    def from_xml_element(cls, xml_elem):
        # <Node Id="3" Name="DM2" WCET="568" Period="80000" Deadline="80000" MaxJitter="-1" Offset="0" CpuId="0" CoreId="-1" />
        assert xml_elem.tag == "Node"
        return cls(xml_elem.attrib["Id"], xml_elem.attrib["Name"],int(xml_elem.attrib["WCET"]),int(xml_elem.attrib["Period"]), int(xml_elem.attrib["Deadline"]),int(xml_elem.attrib["MaxJitter"]), int(xml_elem.attrib["Offset"]), xml_elem.attrib["CpuId"], xml_elem.attrib["CoreId"])

class TaskChain:
    def __init__(self, budget, name, tasks : []):
        self.budget = int(budget)
        self.name = name
        self.tasks = tasks

    @classmethod
    def from_xml_element(cls, xml_elem, task_dict_names):
        assert xml_elem.tag == "Chain"
        tasks = []
        for child in xml_elem:
            if child.tag == "Runnable":
                tasks.append(task_dict_names[child.attrib["Name"]])

        return cls(xml_elem.attrib["Budget"], xml_elem.attrib["Name"], tasks)

class Core:
    def __init__(self, id, macrotick, hyperperiod):
        self.slices = {}
        #dict(slice.assoc_task_id -> list of slices)
        self.tasks = {}
        #dict(task_id -> task)
        self.id = id
        self.macrotick = int(macrotick)
        self.hyperperiod = hyperperiod

    @classmethod
    def from_xml_element(cls, xml_elem, hyperperiod):       
        assert xml_elem.tag == "Core"
        return cls(xml_elem.attrib["Id"], xml_elem.attrib["MacroTick"], hyperperiod)

    def addSlicesFromXMLElement(self, elem, task_dict):
        assert elem.tag == "Schedule"
        last_slice_end = -1

        for child in elem:
            s = Slice.from_xml_element(child)

            
            if not s.start >= last_slice_end:
                raise ValueError("Value Error: Slices have to be in order and not overlap!" + ET.tostring(child, "unicode"))
            last_slice_end = s.end

            if s.assoc_task_id in self.slices:
                self.slices[s.assoc_task_id].append(s)
            else:
                self.slices[s.assoc_task_id] = [s]
        
        self.createJobs(task_dict)
    
    def createJobs(self, task_dict):
        for task_id, slice_list in self.slices.items():
            if task_id not in self.tasks:
                self.tasks[task_id] = task_dict[task_id]
            self.tasks[task_id].jobs = []
            task_period = task_dict[task_id].period
            
            cur_slice = slice_list[0]
            cur_job = Job(task_id, 0, task_period)
            self.tasks[task_id].jobs.append(cur_job)

            for cur_slice in slice_list:
                # Only use slices in one hyperperiod
                while cur_slice != None and cur_slice.start < self.hyperperiod: 
                    # If slice not in current job -> create next job
                    while cur_slice.start >= cur_job.interval_end:
                        cur_job = Job(task_id, cur_job.interval_end, cur_job.interval_end + task_period)
                        self.tasks[task_id].jobs.append(cur_job)
                    
                    # If slice in current job

                    # --- If slice longer than job
                    if cur_slice.end > cur_job.interval_end:
                        # Split slice -> core.slices will not be updated!
                        s1 = Slice(cur_slice.start, cur_job.interval_end - cur_slice.start, task_id)
                        cur_slice = Slice(cur_job.interval_end, cur_slice.end - cur_job.interval_end, task_id)
                        cur_job.addSlice(s1)
                    else:
                        # Add whole slice
                        cur_job.addSlice(cur_slice)
                        cur_slice = None
            
            if not int(self.hyperperiod/task_dict[task_id].period) == len(self.tasks[task_id].jobs):
                raise ValueError("Error: Expected {} jobs for task {}, got {}".format(int(self.hyperperiod/task_dict[task_id]), task_id, len(self.tasks[task_id].jobs)))

@total_ordering
class Slice:
    def __init__(self, start, duration, assoc_task_id):
        self.start = start
        self.duration = duration
        self.end = self.start + self.duration
        self.assoc_task_id = assoc_task_id
    
    @classmethod
    def from_xml_element(cls, xml_elem):
        assert xml_elem.tag == "Slice"
        return cls(int(xml_elem.attrib["Start"]), int(xml_elem.attrib["Duration"]), xml_elem.attrib["TaskId"])
    
    def get_length_in_interval(self, a, b):
        if self.start > b or a > self.end:
            return 0
        else:
            return min(self.end, b) - max(self.start, a)

    def __eq__(self, other):
        if isinstance(other, Slice):
            return self.start == other.start and self.end == other.end
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, Slice):
            return not (self.start == other.start and self.end == other.end)
        else:
            return True

    def __lt__(self, other):
        return self.start < other.start

    def __str__(self):
        return "Slice([{},{}], T {})".format(self.start, self.end, self.assoc_task_id)

class Job:
    def __init__(self, assoc_task_id, interval_begin, interval_end):
        self.interval_begin = interval_begin
        self.interval_end = interval_end
        self.assoc_task_id = assoc_task_id

        self.start = -1 # begin of earliest slice in job, within interval
        self.end = -1 # end of latest slice in job, within interval
        self.length = 0
        self.is_preempted = False
        self.slices = []

    def __str__(self):
        s = "Job("
        for sl in self.slices:
            s = s + "[{},{}], ".format(sl.start, sl.end)
        return s + "T {}, Start {}, End {}, Length {}, Preempted: {})".format(self.assoc_task_id, self.start, self.end, self.length, self.is_preempted)
    
    def addSlice(self, slice : Slice):
        assert slice.assoc_task_id == self.assoc_task_id
        self.slices.append(slice)

        # Slice starts earlier than others?
        if self.start != -1:
            self.start = min(self.start, slice.start)
        else:
            self.start = slice.start
        
        # Slice ends later than others?
        self.end = max(self.end, slice.end)

        # DO we have multiple slices?
        if len(self.slices) > 1:
            self.is_preempted = True

        # Set new length
        self.length = self.length + slice.duration

        # ASSERT
        assert self.end <= self.interval_end and self.start >= self.interval_begin

    def intersect_interval(self, a, b):
        su = 0
        i = 0

        while i < len(self.slices) and self.slices[i].start < b:
            su = su + self.slices[i].get_length_in_interval(a, b)
            i = i + 1
        
        return su 
class Cpu:
    def __init__(self, id, cores : {}):
        self.id = id
        self.cores = cores # dict{coreid -> core}  
    
    @classmethod
    def from_xml_element(cls, xml_elem, hyperperiod):
        assert xml_elem.tag == "Cpu"
        cores = {}
        for child in xml_elem:
            cores[child.attrib["Id"]] = Core.from_xml_element(child, hyperperiod)

        return cls(xml_elem.attrib["Id"], cores)

class Testcase:
    def __init__(self, tc_folder : Path):
        self.cpus = {} # dict{cpuid -> Cpu}    
        self.tasks = {} # dict{taskid -> Task}
        self.tasks_names = {} # dict{taskname -> Task}   
        self.chains = {} # dict{chainname -> Chain}
        
        try:
            self.parseTestcase(tc_folder)
            self.checkTestcase()
            self.checkChains()
        except ValueError as e:
            print(e)

    def parseTestcase(self, tc_folder : Path):
        cfg_file = list(tc_folder.glob("*.cfg"))[0]
        tsk_file = list(tc_folder.glob("*.tsk"))[0]
        schedule_file = list(tc_folder.glob("*.xml"))[0]

        print("1. Parsing testcase: {}, {}, {}\n".format(cfg_file, tsk_file, schedule_file))
        print("-------------------------------------\n")
        # Parse Tasks
        tsk_tree = ET.parse(tsk_file)
        for node_elem in tsk_tree.getroot()[0]:
            if node_elem.tag == "Node":
                t = Task.from_xml_element(node_elem)
                self.tasks[node_elem.attrib["Id"]] = t
                self.tasks_names[node_elem.attrib["Name"]] = t
        
        # Parse Chains
        for node_elem in tsk_tree.getroot()[0]:
            if node_elem.tag == "Chain":
                self.chains[node_elem.attrib["Name"]] = TaskChain.from_xml_element(node_elem, self.tasks_names)
        
        # Calculate Hyperperiod
        _period_list = []
        for task in self.tasks.values():
            _period_list.append(task.period)
        self.hyperperiod = lcm(_period_list)

        cfg_tree = ET.parse(cfg_file)
        for cpu_elem in cfg_tree.getroot():
            self.cpus[cpu_elem.attrib["Id"]] = Cpu.from_xml_element(cpu_elem, self.hyperperiod)

        schedule_tree = ET.parse(schedule_file)
        for schedule_elem in schedule_tree.getroot():
            cpu_id = schedule_elem.attrib["CpuId"]
            core_id = schedule_elem.attrib["CoreId"]
            self.cpus[cpu_id].cores[core_id].addSlicesFromXMLElement(schedule_elem, self.tasks)

    def checkTestcase(self):
        print("2. Checking testcase:", end="\n\n")
        valid = self.checkTaskMapping() and self.checkJobs()
        if valid:
            print("--> The whole testcase is: {}\n".format("\033[92m" + "valid" + "\033[0m"))
        else:
            print("--> The whole testcase is: {}\n".format("\033[91m" + "invalid" + "\033[0m"))
        print("-------------------------------------\n")
        return valid
    
    def checkTaskMapping(self):
        # returns true if all tasks mapped to correct cpu and core
        print("--- checking task mapping")
        check = True
        found_tasks = {} #dict{task_id, (cpu_id, core_id)}
        for cpu in self.cpus.values():
            for core in cpu.cores.values():
                for task_id in core.tasks.keys():
                    if task_id in found_tasks:
                        print("Task {} has already been mapped to CPU {}, Core {}. It can't also be mapped to CPU {}, Core {}.".format(task_id, found_tasks[task_id][0], found_tasks[task_id][1], cpu.id, core.id))
                        check = False
                    else:
                        found_tasks[task_id] = (cpu.id, core.id)

                        if not (self.tasks[task_id].cpu_id == cpu.id or self.tasks[task_id].cpu_id== "-1"):
                            check = False
                            print("Task {} has been mapped to the wrong CPU {}. Expected CPU {}.".format(task_id, cpu.id, self.tasks[task_id].cpu_id))
                        if not (self.tasks[task_id].core_id == core.id or self.tasks[task_id].core_id == "-1"):
                            check = False
                            print("Task {} has been mapped to the wrong Core {}. Expected Core {}.".format(task_id, core.id, self.tasks[task_id].core_id))
        
        if check:
            print("Task mapping: {}\n".format("\033[92m" + "valid" + "\033[0m"))
        else:
            print("Task mapping: {}\n".format("\033[91m" + "invalid" + "\033[0m"))
        return check

    def checkJobs(self):
        print("--- checking tasks: deadlines, wcet, jitter, macrotick")
        all_valid = True
        for cpu in self.cpus.values():
            for core in cpu.cores.values():
                for taskid, task in core.tasks.items():
                    job_list = task.jobs             

                    job_nr = int(core.hyperperiod/task.period)
                    # job_list is sorted by start time. it has hyperperiod/task.period jobs

                    initial_release_time = job_list[0].start
                    initial_finish_time = job_list[0].end
                    if not (initial_release_time != -1 and initial_finish_time != -1):
                        raise ValueError("Error: Job {} has invalid start or end time. (Is there any slice in job?)".format(job_list[0]))

                    i = 0
                    for job in job_list:
                        # check WCET
                        if job.length < task.wcet:
                            print("Task {} has not enough slice time in interval [{},{}] ({}<{})".format(task.id, job.interval_begin, job.interval_end, job.length, task.wcet))
                            all_valid = False
                        
                        # check deadlines
                        deadline_interval = (initial_release_time + i*task.period, initial_release_time + i*task.period + task.deadline)

                        if i == len(job_list) - 1:
                            # For last job wrap interval to beginning
                            assert (i+1) % job_nr == 0
                            intersect1 = job.intersect_interval(deadline_interval[0], job.interval_end)
                            intersect2 = job_list[(i+1) % job_nr].intersect_interval(0, deadline_interval[1]-deadline_interval[0])
                            if (intersect1 +  intersect2 < task.wcet):
                                print("Task {} has not enough slice time in deadline interval [{},{}] UNION [{},{}] ({}<{})".format(task.id, deadline_interval[0], deadline_interval[1], 0, deadline_interval[1]-deadline_interval[0], intersect1+intersect2, task.wcet))
                                all_valid = False
                        else:
                            intersect1 = job.intersect_interval(deadline_interval[0], deadline_interval[1])
                            intersect2 = job_list[(i+1) % job_nr].intersect_interval(deadline_interval[0], deadline_interval[1])
                            if (intersect1 + intersect2 < task.wcet):
                                print("Task {} has not enough slice time in deadline interval [{},{}] ({}<{})".format(task.id, deadline_interval[0], deadline_interval[1], intersect1+intersect2, task.wcet))
                                all_valid = False

                        # check max jitter
                        start_jitter = abs(initial_release_time - (job.start - i*task.period))
                        end_jitter = abs(initial_finish_time - (job.end - i*task.period))
                        max_jitter = max(start_jitter, end_jitter)

                        if not task.max_jitter == -1 and max_jitter > task.max_jitter:
                            print("Task {} has too much jitter after interval [{},{}] ({}>{})".format(task.id, job.interval_begin, job.interval_end, max_jitter, task.max_jitter))
                            print([initial_release_time, initial_finish_time, start_jitter, end_jitter])
                            all_valid = False

                        # check preemption & macrotick
                        if job.is_preempted:
                            task.is_preempted = True
                            for i in range(len(job.slices) - 1):
                                # For each except last slice check divisable by macrotick
                                if job.slices[i].duration % core.macrotick != 0:
                                    all_valid = False
                                    print("Task {} has a slice [{},{}] whose duration {} is not a multiple of the macrotick {}".format
                                    (
                                        task.id, job.slices[i].start, job.slices[i].end, job.slices[i].duration, core.macrotick
                                    ))
                        # 
                        i = i + 1
                    
                    if(task.is_preempted):
                        print("\033[94m" + "Task {} on Core {} is preempted".format(taskid, core.id) + "\033[0m")


        if all_valid:
            print("Tasks: {}\n".format("\033[92m" + "valid" + "\033[0m"))
        else:
            print("Tasks: {}\n".format("\033[91m" + "invalid" + "\033[0m"))            
        return all_valid

    def checkChains(self):
        print("3. Checking chains: ")
        costs = []

        for chain in self.chains.values():
            first_task = self.tasks[chain.tasks[0].id]
            max_latency = -1
            relative_latencies = []
            
            # check for all jobs in one hyperperiod for first_task
            for job in first_task.jobs:
                start = job.start
                last_end = job.end
                latency = 0
                wraparounds = 0

                # iterate through tasks in chain
                for i in range(1, len(chain.tasks)):
                    # find next job for current task that starts after the last job
                    task = chain.tasks[i]
                    tasks_job_nr = int(self.hyperperiod/task.period)
                    index = int(last_end / task.period) % tasks_job_nr

                    if task.jobs[index].start >= last_end:
                        last_end = task.jobs[index].end
                    else:
                        # job started too earlz -> take job from next interval

                        # next interval would be out of hyperperiod -> wrap around and increase latency by hyperperiod
                        if index+1 >= tasks_job_nr:
                            wraparounds += 1

                        index = (index + 1) % tasks_job_nr
                        last_end = task.jobs[index].end
                
                
                real_end = last_end + wraparounds*self.hyperperiod
                latency = real_end - start
                relative_latencies.append(latency/chain.budget)

                if latency > max_latency:
                    max_latency = latency

                if latency > chain.budget:
                    print("Chain {} exceeded its budget with start job {}: {}>{}"
                    .format(chain.name, job, latency, chain.budget))
            
            assert len(relative_latencies) == len(first_task.jobs)
            
            cost = sum(relative_latencies)/len(relative_latencies)
            costs.append(cost)
            if max_latency <= chain.budget:
                print("--- Chain {} is {}. Cost is {}".format(chain.name, "\033[92m" + "okay" + "\033[0m", cost))
            else:
                print("--- Chain {} is {}. Cost is {}".format(chain.name, "\033[91m" + "exceeding budget" + "\033[0m", cost))
        
        print("\n--> Mean cost is {}".format(sum(costs)/len(costs)))



if len(sys.argv) > 1:
    tc = Testcase(Path(sys.argv[1]))
else:
    print("No path argument")


